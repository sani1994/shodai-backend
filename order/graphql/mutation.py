import json
import uuid

import geocoder
import graphene
import requests
from bases.views import checkAuthentication
from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone

from graphene_django import DjangoObjectType
from graphql_relay.utils import unbase64

from offer.models import OfferProduct
from utility.notification import email_notification, send_sms
from .queries import OrderType, OrderProductType
from ..models import Order, OrderProduct, PaymentInfo, DeliveryCharge, InvoiceInfo, TimeSlot
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
    Dhanmondi = 'Dhanmondi'
    Mohammadpur = 'Mohammadpur'
    Adabar = 'Adabar'


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
                order_instance = Order(user=user,
                                       created_by=user,
                                       delivery_date_time=input.delivery_date_time,
                                       delivery_place=input.delivery_place,
                                       total_vat=input.total_vat,
                                       order_total_price=input.net_pay_able_amount,
                                       lat=input.lat,
                                       long=input.long,
                                       order_status="OD",
                                       order_type=input.order_type,
                                       contact_number=input.contact_number if input.contact_number else user.mobile_number
                                       )
                order_instance.address = Address.objects.get(id=input.address)
                order_instance.payment_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.bill_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.save()

                product_list = input.products
                product_list_detail = []
                for p in product_list:
                    product_id = from_global_id(p.product_id)
                    product = Product.objects.get(id=product_id)
                    OrderProduct.objects.create(product=product,
                                                order=Order.objects.get(pk=order_instance.pk),
                                                order_product_price=product.product_price,
                                                order_product_qty=p.order_product_qty, )
                    product_list_detail.append(product.product_name + " " + product.product_unit.product_unit + "*"
                                               + str(p.order_product_qty) + "\n")

                # Create InvoiceInfo Instance
                billing_person_name = user.first_name + " " + user.last_name
                delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
                invoice = InvoiceInfo.objects.create(invoice_number=order_instance.invoice_number,
                                                     billing_person_name=billing_person_name,
                                                     billing_person_email=user.email,
                                                     billing_person_mobile_number=user.mobile_number,
                                                     delivery_contact_number=order_instance.contact_number,
                                                     delivery_address=order_instance.address.road,
                                                     delivery_date_time=order_instance.delivery_date_time,
                                                     delivery_charge=delivery_charge,
                                                     net_payable_amount=input.net_pay_able_amount,
                                                     payment_method=input.payment_method,
                                                     order_number=order_instance,
                                                     user=user,
                                                     created_by=user)
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
            place = str(order_instance.delivery_place) + ', Dhaka'
            print(place)
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
            product_list_detail = []
            matrix = []
            price_without_offer = 0

            for p in product_list:
                today = timezone.now()
                offer_product = OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                                            offer__offer_ends_in__gte=today, product=p.product)

                if offer_product:
                    is_offer = True
                    total_by_offer = float(offer_product[0].offer_price) * p.order_product_qty
                    col = [p.product.product_name, p.product.product_price, offer_product[0].offer_price,
                           p.order_product_qty, total_by_offer]
                    total_with_vat = float(p.product.product_price_with_vat) * p.order_product_qty
                    price_without_offer += total_with_vat
                    matrix.append(col)
                else:
                    total = float(p.product.product_price) * p.order_product_qty
                    col = [p.product.product_name, p.product.product_price, "--",
                           p.order_product_qty, total]
                    total_with_vat = float(p.product.product_price_with_vat) * p.order_product_qty
                    price_without_offer += total_with_vat
                    matrix.append(col)
                product_list_detail.append(p.product.product_name + " " + p.product.product_unit.product_unit + "*"
                                           + str(p.order_product_qty) + "\n")

            text_content = 'Your Order (#' + str(order_instance.pk) + ') has been confirmed'
            htmly = get_template('email.html')

            time_slot = TimeSlot.objects.get(id=input.time_slot_id)
            delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
            sub_total = order_instance.order_total_price - delivery_charge
            client_name = user.first_name + " " + user.last_name

            d = {'user_name': client_name,
                 'order_id': order_instance.pk,
                 'shipping_address': order_instance.address.road + " " + order_instance.address.city + " " + order_instance.address.zip_code,
                 'mobile_no': order_instance.contact_number,
                 'order_date': order_instance.created_on.date(),
                 'delivery_date_time': str(
                     order_instance.delivery_date_time.date()) + " ( " + time_slot.slot + " )",
                 'sub_total': sub_total,
                 'vat': order_instance.total_vat,
                 'delivery_charge': delivery_charge,
                 'total': order_instance.order_total_price,
                 'order_details': matrix,
                 'is_offer': is_offer,
                 'price_without_offer': float(round(price_without_offer))
                 }

            subject = 'Your shodai order (#' + str(order_instance.pk) + ') summary'
            subject, from_email, to = subject, 'noreply@shod.ai', user.email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            """
            To send notification to admin
            """
            sub = "Order Placed"
            body = f"Dear Concern,\r\nUser phone number :{user.mobile_number} \r\nUser type: {user.user_type} " \
                   f"posted an order from shodai website with the following details" \
                   f" \r\nOrder id: {order_instance.pk}." \
                   f" \r\nOrdered product list with quantity:\n {' '.join(product_list_detail)}" \
                   f" \r\nOrder delivery date and time: {order_instance.delivery_date_time}." \
                   f" \r\nOrder delivery area: {order_instance.delivery_place}." \
                   f" \r\nOrder delivery address: {order_instance.address}." \
                   f" \r\nOrder Sub total price: {order_instance.order_total_price - order_instance.total_vat - delivery_charge}." \
                   f" \r\nOrder vat amount: {order_instance.total_vat}." \
                   f" \r\nOrder delivery charge: {delivery_charge}." \
                   f" \r\nOrder net payable amount: {order_instance.order_total_price}." \
                   f" \r\nOrder payment method: {invoice.payment_method}." \
                   f"\r\n \r\nThanks and Regards\r\nShodai "
            print(is_offer)
            email_notification(sub, body)

            # # send sms to user
            # sms_body = f"Dear " + client_name + \
            #            ",\r\n\nYour order #" + str(order_instance.pk) + \
            #            " has been placed. Your total payable amount is " + \
            #            str(order_instance.order_total_price) + " and preferred delivery slot is " \
            #            + str(order_instance.delivery_date_time.date()) + " (" + time_slot.slot + ")" + \
            #            ". \n\nThank you for shopping with shodai "
            # sms_flag = send_sms(mobile_number=user.mobile_number, sms_content=sms_body)

            return SendEmail(msg="email sent successfully")


class CreateOrderProduct(graphene.Mutation):
    class Arguments:
        input = OrderProductInputA(required=True)

    order_product = graphene.Field(OrderProductType)

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if checkAuthentication(user, info):
            if user.user_type == 'CM':
                product_id = from_global_id(input.product_id)
                product = Product.objects.get(id=product_id)
                print(product.product_name)
                order_product_instance = OrderProduct(product=product,
                                                      order=Order.objects.get(pk=input.order_id),
                                                      order_product_price=product.product_price,
                                                      order_product_price_with_vat=product.price_with_vat,
                                                      vat_amount=product.product_meta.vat_amount,
                                                      order_product_qty=input.order_product_qty, )
                order_product_instance.save()
                return CreateOrderProduct(order_product=order_product_instance)
            else:
                raise Exception('Unauthorized request!')


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
                print(body)
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
        user = info.context.user
        transaction_info = kwargs["transaction_info"]
        payment_status = kwargs["payment_status"]
        invoice_number = transaction_info.invoice_number

        try:
            payment_info = PaymentInfo.objects.get(invoice_number=invoice_number, payment_status='INITIATED')
        except PaymentInfo.DoesNotExist as e:
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
    create_order_product = CreateOrderProduct.Field()
    payment = PaymentMutation.Field()
    store_transaction_info = TransactionMutation.Field()


def from_global_id(global_id):
    """
    Takes the "global ID" created by toGlobalID, and returns ID
    used to create it.
    """
    unbased_global_id = unbase64(global_id)
    _type, _id = unbased_global_id.split(':', 1)
    return _id
