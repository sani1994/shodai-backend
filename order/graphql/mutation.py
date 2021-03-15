import json
import uuid

import geocoder
import graphene
import requests

from datetime import timedelta
from django.conf import settings
from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone
from graphene_django import DjangoObjectType

from bases.views import checkAuthentication, from_global_id, coupon_checker
from coupon.models import CouponCode, CouponUser, CouponUsageHistory
from utility.notification import email_notification, send_sms
from .queries import OrderType, OrderProductType
from ..models import Order, OrderProduct, PaymentInfo, DeliveryCharge, InvoiceInfo, TimeSlot, DiscountInfo
from product.models import Product
from userProfile.models import Address, BlackListedToken


class OrderStatusEnum(graphene.Enum):
    ORDERED = "OD"  # ORDER COLLECT FROM CUSTOMER
    ORDER_ACCEPTED = "OA"  # ORDER ACCEPTED BY RETAILER OR PRODUCER
    ORDER_READY = "RE"  # ORDER IS READY FOR DELIVERY PERSON
    ORDER_AT_DELIVERY = "OAD"  # ORDER IS WITH DELIVERY PEROSN
    ORDER_COMPLETED = "COM"  # ORDER IS DELIVERED TO CUSTOMER
    ORDER_CANCELLED = "CN"  # ORDER IS CANCEL BY CUSTOMER


class OrderTypeEnum(graphene.Enum):
    FIXED_PRICE = "FP"
    BIDDING = "BD"


class AreaChoicesEnum(graphene.Enum):
    Dhaka = 'Dhaka'


class PaymentMethodEnum(graphene.Enum):
    ONLINE_PAYMENT = 'SSLCOMMERZ'
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY'


class PaymentStatusEnum(graphene.Enum):
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class PaymentInfoType(DjangoObjectType):
    class Meta:
        model = PaymentInfo


class OrderProductInput(graphene.InputObjectType):
    product_id = graphene.String(required=True)
    order_product_qty = graphene.Float(required=True)


class OrderInput(graphene.InputObjectType):
    delivery_date_time = graphene.DateTime(required=True)
    delivery_place = graphene.NonNull(AreaChoicesEnum)
    net_pay_able_amount = graphene.String(required=True)
    total_vat = graphene.String(required=True)
    order_total_price = graphene.String(required=True)
    lat = graphene.Float(required=True)
    long = graphene.Float(required=True)
    home_delivery = graphene.Boolean(required=True)
    address = graphene.Int(required=True)
    order_type = graphene.NonNull(OrderTypeEnum)
    contact_number = graphene.String()
    products = graphene.List(OrderProductInput)
    payment_method = graphene.NonNull(PaymentMethodEnum)
    note = graphene.String()
    code = graphene.String(required=True)


class EmailInput(graphene.InputObjectType):
    order_id = graphene.ID(required=True)
    time_slot_id = graphene.ID(required=True)


class OrderProductInputA(graphene.InputObjectType):
    product_id = graphene.String(required=True)
    order_id = graphene.ID()
    order_product_qty = graphene.Float(required=True)


class TransactionInput(graphene.InputObjectType):
    transaction_id = graphene.String()
    invoice_number = graphene.String()
    payment_id = graphene.String()


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if checkAuthentication(user, info):
            if user.user_type == 'CM':
                order_instance = Order.objects.create(user=user,
                                                      created_by=user,
                                                      delivery_date_time=input.delivery_date_time,
                                                      delivery_place=input.delivery_place,
                                                      lat=input.lat,
                                                      long=input.long,
                                                      order_status="OD",
                                                      order_type=input.order_type,
                                                      contact_number=input.contact_number if input.contact_number else user.mobile_number)

                product_list = input.products
                sub_total_without_offer = total_vat = sub_total = 0
                for p in product_list:
                    product_id = from_global_id(p.product_id)
                    product = Product.objects.get(id=product_id)
                    op = OrderProduct.objects.create(product=product,
                                                     order=order_instance,
                                                     order_product_qty=p.order_product_qty)

                    sub_total_without_offer += float(product.product_price) * p.order_product_qty
                    sub_total += float(op.order_product_price) * op.order_product_qty
                    total_vat += float(op.order_product_price_with_vat - op.order_product_price) * op.order_product_qty

                coupon_discount_amount = 0
                if input.code:
                    discount_amount, coupon, is_using, _ = coupon_checker(input.code, product_list, user, False)
                    if discount_amount:
                        coupon_discount_amount = discount_amount
                        is_using.remaining_usage_count -= 1
                        is_using.save()
                        coupon.max_usage_count -= 1
                        coupon.save()
                        if coupon.coupon_code_type == 'RC':
                            new_coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
                                                                   name="Discount Code",
                                                                   discount_percent=int(config("DC_DISCOUNT_PERCENT")),
                                                                   max_usage_count=1,
                                                                   minimum_purchase_limit=int(config("DC_MIN_PURCHASE_LIMIT")),
                                                                   discount_amount_limit=int(config("DC_DISCOUNT_LIMIT")),
                                                                   expiry_date=timezone.now() + timedelta(days=int(config("DC_VALIDITY_PERIOD"))),
                                                                   discount_type='DP',
                                                                   coupon_code_type='DC',
                                                                   created_by=user,
                                                                   created_on=timezone.now())
                            CouponUser.objects.create(coupon_code=new_coupon,
                                                      created_for=coupon.created_by,
                                                      remaining_usage_count=1,
                                                      created_by=user,
                                                      created_on=timezone.now())
                            if not settings.DEBUG:
                                sms_body = "Dear Customer,\n" + \
                                           "Congratulations! You have received {}% discount ".format(config("DC_DISCOUNT_PERCENT")) + \
                                           "based on your successful referral. " + \
                                           "Use this code [{}] to ".format(new_coupon.coupon_code) + \
                                           "avail exciting discount on your next purchase.\n\n" + \
                                           "www.shod.ai"
                                send_sms(mobile_number=coupon.created_by.mobile_number, sms_content=sms_body)

                delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
                if input.note:
                    order_instance.note = input.note[:500]
                order_instance.address = Address.objects.get(id=input.address)
                order_instance.payment_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.bill_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.total_vat = total_vat
                order_instance.order_total_price = sub_total + total_vat + delivery_charge - coupon_discount_amount
                order_instance.save()

                if user.first_name and user.last_name:
                    billing_person_name = user.first_name + " " + user.last_name
                elif user.first_name:
                    billing_person_name = user.first_name
                else:
                    billing_person_name = ""
                invoice = InvoiceInfo.objects.create(invoice_number=order_instance.invoice_number,
                                                     billing_person_name=billing_person_name,
                                                     billing_person_email=user.email,
                                                     billing_person_mobile_number=user.mobile_number,
                                                     delivery_contact_number=order_instance.contact_number,
                                                     delivery_address=order_instance.address.road,
                                                     delivery_date_time=order_instance.delivery_date_time,
                                                     delivery_charge=delivery_charge,
                                                     discount_amount=sub_total_without_offer - sub_total + coupon_discount_amount,
                                                     net_payable_amount=order_instance.order_total_price,
                                                     payment_method=input.payment_method,
                                                     order_number=order_instance,
                                                     user=user,
                                                     created_by=user)

                if sub_total_without_offer != sub_total:
                    DiscountInfo.objects.create(discount_amount=sub_total_without_offer - sub_total,
                                                discount_type='PD',
                                                discount_description='Product Offer Discount',
                                                invoice=invoice)
                if coupon_discount_amount:
                    DiscountInfo.objects.create(discount_amount=coupon_discount_amount,
                                                discount_type='CP',
                                                discount_description='Coupon Code: {}'.format(input.code),
                                                coupon=coupon,
                                                invoice=invoice)
                    CouponUsageHistory.objects.create(discount_type=coupon.discount_type,
                                                      discount_percent=coupon.discount_percent,
                                                      discount_amount=coupon_discount_amount,
                                                      coupon_code=coupon.coupon_code,
                                                      coupon_user=is_using,
                                                      invoice_number=invoice,
                                                      created_by=user,
                                                      created_on=timezone.now())

                return CreateOrder(order=order_instance)
            else:
                raise Exception('Unauthorized request!')


class SendEmail(graphene.Mutation):
    class Arguments:
        input = EmailInput(required=True)

    msg = graphene.String()

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if checkAuthentication(user, info):
            order_instance = Order.objects.filter(pk=input.order_id)[0]
            invoice = InvoiceInfo.objects.filter(invoice_number=order_instance.invoice_number)[0]
            place = order_instance.address.road
            g = geocoder.osm(place)
            if g:
                order_instance.lat = g.osm['y']
                order_instance.long = g.osm['x']
                order_instance.save()
            else:
                g = geocoder.osm('Adabar, Dhaka')
                order_instance.lat = g.osm['y']
                order_instance.long = g.osm['x']
                order_instance.save()

            product_list = OrderProduct.objects.filter(order__pk=input.order_id)
            matrix = []
            is_product_discount = False
            product_total_price = 0
            for p in product_list:
                if p.order_product_price != p.product_price:
                    is_product_discount = True
                    total_by_offer = float(p.order_product_price) * p.order_product_qty
                    product_total_price += total_by_offer
                    col = [p.product.product_name, p.product.product_unit, p.product_price,
                           p.order_product_price, int(p.order_product_qty), total_by_offer]
                else:
                    total = float(p.product_price) * p.order_product_qty
                    product_total_price += total
                    col = [p.product.product_name, p.product.product_unit, p.product_price,
                           "--", int(p.order_product_qty), total]
                matrix.append(col)

            is_coupon_discount = DiscountInfo.objects.filter(discount_type='CP', invoice=invoice)
            coupon_discount = is_coupon_discount[0].discount_amount if is_coupon_discount else 0

            time_slot = TimeSlot.objects.get(id=input.time_slot_id)
            delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
            client_name = invoice.billing_person_name

            content = {'user_name': client_name,
                       'order_number': order_instance.order_number,
                       'shipping_address': order_instance.address.road + " " + order_instance.address.city + " " + order_instance.address.zip_code,
                       'mobile_no': order_instance.contact_number,
                       'order_date': order_instance.created_on.date(),
                       'delivery_date_time': str(
                           order_instance.delivery_date_time.date()) + " ( " + time_slot.slot + " )",
                       'sub_total': product_total_price,
                       'vat': order_instance.total_vat,
                       'delivery_charge': delivery_charge,
                       'total': order_instance.order_total_price,
                       'order_details': matrix,
                       'is_product_discount': is_product_discount,
                       'coupon_discount': coupon_discount,
                       'delivery_charge_discount': 0,
                       'saved_amount': invoice.discount_amount,
                       'note': order_instance.note if order_instance.note else None,
                       'colspan_value': "4" if is_product_discount else "3"}

            subject = 'Your shodai order (#' + str(order_instance.order_number) + ') summary'
            from_email, to = 'noreply@shod.ai', user.email
            html_customer = get_template('email.html')
            html_content = html_customer.render(content)
            msg = EmailMultiAlternatives(subject, 'shodai', from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            """
            To send notification to admin
            """

            if invoice.payment_method == "CASH_ON_DELIVERY":
                payment_method = "Cash on Delivery"
            else:
                payment_method = "Online Payment"
            content = {'user_name': client_name,
                       'user_mobile': user.mobile_number,
                       'order_number': order_instance.order_number,
                       'platform': "Website",
                       'shipping_address': order_instance.address.road + " " + order_instance.address.city + " " + order_instance.address.zip_code,
                       'mobile_no': order_instance.contact_number,
                       'order_date': order_instance.created_on.date(),
                       'delivery_date_time': str(
                           order_instance.delivery_date_time.date()) + " ( " + time_slot.slot + " )",
                       'invoice_number': invoice.invoice_number,
                       'payment_method': payment_method,
                       'sub_total': product_total_price,
                       'vat': order_instance.total_vat,
                       'delivery_charge': delivery_charge,
                       'total': order_instance.order_total_price,
                       'order_details': matrix,
                       'is_product_discount': is_product_discount,
                       'coupon_discount': coupon_discount,
                       'delivery_charge_discount': 0,
                       'saved_amount': invoice.discount_amount,
                       'note': order_instance.note if order_instance.note else None,
                       'colspan_value': "4" if is_product_discount else "3"}

            admin_subject = 'Order (#' + str(order_instance.order_number) + ') has been placed'
            admin_email = config("TARGET_EMAIL_USER").replace(" ", "").split(',')
            html_admin = get_template('admin_email.html')
            html_content = html_admin.render(content)
            msg_to_admin = EmailMultiAlternatives(admin_subject, 'shodai', from_email, admin_email)
            msg_to_admin.attach_alternative(html_content, "text/html")
            msg_to_admin.send()

            # sms_body = f"Dear " + client_name + \
            #            ",\r\n\nYour order #" + str(order_instance.pk) + \
            #            " has been placed. Your total payable amount is " + \
            #            str(order_instance.order_total_price) + " and preferred delivery slot is " \
            #            + str(order_instance.delivery_date_time.date()) + " (" + time_slot.slot + ")" + \
            #            ". \n\nThank you for shopping with shodai "
            # sms_flag = send_sms(mobile_number=user.mobile_number, sms_content=sms_body)

            return SendEmail(msg="email sent successfully")


class PaymentMutation(graphene.Mutation):
    status = graphene.String()
    message = graphene.String()
    url = graphene.String()
    content = graphene.JSONString()

    class Arguments:
        order_id = graphene.ID()
        address_id = graphene.ID()

    @staticmethod
    def mutate(root, info, **kwargs):
        user = info.context.user
        if checkAuthentication(user, info):
            if user.user_type == 'CM':
                address = Address.objects.get(pk=kwargs["address_id"], user=user)
                obj = Order.objects.get(pk=kwargs["order_id"], user=user)
                order_product_list = OrderProduct.objects.filter(order=obj)
                products = [op.product for op in order_product_list]
                product_name = [p.product_name for p in products]
                category = [p.product_meta.product_category.type_of_product for p in products]

                body = {
                    "project_id": config("PAYMENT_PROJECT_ID", None),
                    "project_secret": config("PAYMENT_PROJECT_SECRET", None),
                    "invoice_number": obj.invoice_number,
                    "product_name": ' '.join(product_name) if product_name else "None",
                    "product_category": ' '.join(category) if category else "None",
                    "product_profile": "general",
                    "customer_name": user.username,
                    "customer_email": user.email if user.email else 'None',
                    "customer_mobile": user.mobile_number,
                    "customer_address": obj.delivery_place,
                    "customer_city": address.city if address.city else 'Dhaka',
                    "customer_country": address.country if address.country else 'BD'
                }
                data = json.dumps(body)
                response = requests.post(config("PAYMENT_PROJECT_URL", None), data=data)
                content = response.json()

                if response.status_code == 200:
                    if content["status"] == "success":
                        payment_id = content["payment_id"]
                        order_id = obj.pk
                        bill_id = obj.bill_id
                        invoice_number = obj.invoice_number

                        payment = PaymentInfo(payment_id=payment_id,
                                              order_id=Order.objects.get(pk=order_id),
                                              bill_id=bill_id,
                                              invoice_number=invoice_number,
                                              payment_status="INITIATED")
                        payment.save()

                        url = content["payment_url"]
                        return PaymentMutation(status="success", message="Payment successful", url=url)
                    else:
                        return PaymentMutation(status="success", message="Payment failed", content=content)
                else:
                    return PaymentMutation(status="failed", message="request failed", content=content)
            else:
                raise Exception('Unauthorized request!')


class TransactionMutation(graphene.Mutation):
    message = graphene.String()
    transaction_id = graphene.String()
    invoice_number = graphene.String()
    payment_status = graphene.String()

    class Arguments:
        transaction_info = graphene.NonNull(TransactionInput)
        payment_status = graphene.NonNull(PaymentStatusEnum)

    @staticmethod
    def mutate(root, info, **kwargs):
        # user = info.context.user
        transaction_info = kwargs["transaction_info"]
        payment_status = kwargs["payment_status"]
        invoice_number = transaction_info.invoice_number

        try:
            payment_info = PaymentInfo.objects.filter(invoice_number=invoice_number, payment_status='INITIATED')[0]
        except Exception:
            payment_info = None

        if payment_info and payment_status:
            if payment_status == "SUCCESS":
                payment_id = transaction_info.payment_id
                payment_id = payment_id if payment_id == payment_info.payment_id else None
                transaction_id = transaction_info.transaction_id

                if payment_id and transaction_id:
                    payment_info.transaction_id = transaction_id
                    payment_info.payment_status = "SUCCESS"
                    payment_info.save()
                    invoice = InvoiceInfo.objects.get(invoice_number=invoice_number)
                    invoice.paid_status = True
                    invoice.transaction_id = transaction_id
                    invoice.paid_on = timezone.now()
                    invoice.save()
                    return TransactionMutation(transaction_id=transaction_id,
                                               invoice_number=invoice_number,
                                               payment_status=payment_status,
                                               message="transaction_id stored successfully")
                else:
                    return TransactionMutation(message="invalid information")
            elif payment_status == "CANCELLED":
                payment_info.payment_status = "CANCELLED"
                payment_info.save()
                return TransactionMutation(invoice_number=invoice_number,
                                           payment_status=payment_status,
                                           message="transaction cancelled by user")
            elif payment_status == "FAILED":
                payment_info.payment_status = "FAILED"
                payment_info.save()
                return TransactionMutation(invoice_number=invoice_number,
                                           payment_status=payment_status,
                                           message="transaction failed")
            else:
                return TransactionMutation(message="invalid information")
        else:
            return TransactionMutation(message="invalid information")


class Mutation(graphene.ObjectType):
    create_order = CreateOrder.Field()
    send_email = SendEmail.Field()
    payment = PaymentMutation.Field()
    store_transaction_info = TransactionMutation.Field()
