import json
import uuid
from datetime import timedelta

# import geocoder
import graphene
import requests

from decouple import config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.template.loader import get_template
from django.utils import timezone
from django_q.tasks import async_task
from graphene_django import DjangoObjectType

from base.views import checkAuthentication, from_global_id, coupon_checker
from coupon.models import CouponCode, CouponUsageHistory, CouponSettings
from order.models import Order, OrderProduct, PaymentInfo, DeliveryCharge, InvoiceInfo, TimeSlot, DiscountInfo, PreOrder, \
    PreOrderSetting
from product.models import Product
from user.models import Address


class OrderStatusEnum(graphene.Enum):
    ORDERED = "OD"  # ORDER PLACED BY CUSTOMER
    ORDER_ACCEPTED = "OA"  # ORDER ACCEPTED BY RETAILER OR PRODUCER
    ORDER_READY = "RE"  # ORDER IS READY FOR DELIVERY PERSON
    ORDER_AT_DELIVERY = "OAD"  # ORDER IS WITH DELIVERY PEROSN
    ORDER_COMPLETED = "COM"  # ORDER IS DELIVERED TO CUSTOMER
    ORDER_CANCELLED = "CN"  # ORDER IS CANCELLED BY CUSTOMER


# class AreaChoicesEnum(graphene.Enum):
#     Dhaka = 'Dhaka'


class PaymentMethodEnum(graphene.Enum):
    ONLINE = 'SSLCOMMERZ'
    COD = 'CASH_ON_DELIVERY'


class PlatformEnum(graphene.Enum):
    WEB = 'WB'
    APP = 'AP'


class PaymentStatusEnum(graphene.Enum):
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class PaymentInfoType(DjangoObjectType):
    class Meta:
        model = PaymentInfo


class OrderProductInput(graphene.InputObjectType):
    product_id = graphene.String(required=True)
    product_quantity = graphene.Int(required=True)


class OrderInput(graphene.InputObjectType):
    delivery_date_time = graphene.DateTime(required=True)
    address = graphene.String(required=True)
    products = graphene.List(OrderProductInput, required=True)
    payment_method = graphene.NonNull(PaymentMethodEnum)
    platform = graphene.NonNull(PlatformEnum)
    contact_number = graphene.String()
    note = graphene.String()
    code = graphene.String()
    # delivery_place = graphene.NonNull(AreaChoicesEnum)
    # lat = graphene.Float(required=True)
    # long = graphene.Float(required=True)


class TransactionInput(graphene.InputObjectType):
    transaction_id = graphene.String()
    invoice_number = graphene.String()
    payment_id = graphene.String()


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    order_id = graphene.ID()

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if checkAuthentication(user, info):
            if user.user_type == 'CM':
                pre_order = True if len(input.products) == 1 and input.products[0].product_id.isdigit() else False
                address = Address.objects.get(id=int(input.address))
                contact_number = input.contact_number if input.contact_number else user.mobile_number
                note = input.note[:500] if input.note else ""
                if not pre_order:
                    order_instance = Order.objects.create(platform=input.platform,
                                                          delivery_date_time=input.delivery_date_time,
                                                          delivery_place='Dhaka',
                                                          lat=23.777176,
                                                          long=90.399452,
                                                          contact_number=contact_number,
                                                          address=address,
                                                          note=note,
                                                          user=user,
                                                          created_by=user)

                    product_list = input.products
                    sub_total_without_offer = total_vat = sub_total = 0
                    for p in product_list:
                        product_id = from_global_id(p.product_id)
                        product = Product.objects.get(id=product_id)
                        op = OrderProduct.objects.create(product=product,
                                                         order=order_instance,
                                                         order_product_qty=p.product_quantity)
                        sub_total_without_offer += float(op.product_price) * op.order_product_qty
                        sub_total += float(op.order_product_price) * op.order_product_qty
                        total_vat += float(
                            op.order_product_price_with_vat - op.order_product_price) * op.order_product_qty

                    coupon_discount_amount = 0
                    if input.code:
                        discount_amount, coupon, is_using, _ = coupon_checker(input.code, product_list, user, True)
                        if discount_amount:
                            coupon_discount_amount = discount_amount
                            is_using.remaining_usage_count -= 1
                            is_using.save()
                            coupon.max_usage_count -= 1
                            coupon.save()

                    delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
                    order_instance.total_vat = total_vat
                    order_instance.order_total_price = sub_total + total_vat + delivery_charge - coupon_discount_amount
                    order_instance.save()

                    referral_discount_settings = CouponSettings.objects.get(coupon_type='RC')
                    if referral_discount_settings.is_active:
                        referral_coupon = CouponCode.objects.filter(coupon_code_type='RC',
                                                                    created_by=order_instance.user).order_by('-created_on')
                        if referral_coupon:
                            referral_coupon = referral_coupon[0]
                            if referral_coupon.expiry_date < timezone.now():
                                referral_coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
                                                                            name="Referral Coupon",
                                                                            discount_percent=referral_discount_settings.discount_percent,
                                                                            discount_amount=referral_discount_settings.discount_amount,
                                                                            max_usage_count=referral_discount_settings.max_usage_count,
                                                                            minimum_purchase_limit=referral_discount_settings.minimum_purchase_limit,
                                                                            discount_amount_limit=referral_discount_settings.discount_amount_limit,
                                                                            expiry_date=timezone.now() + timedelta(
                                                                                days=referral_discount_settings.validity_period),
                                                                            discount_type=referral_discount_settings.discount_type,
                                                                            coupon_code_type='RC',
                                                                            created_by=order_instance.user)

                            if referral_coupon.max_usage_count > 0:
                                if not settings.DEBUG:
                                    async_task('coupon.tasks.send_coupon_sms',
                                               referral_coupon,
                                               order_instance.user.mobile_number)
                                async_task('coupon.tasks.send_coupon_email',
                                           referral_coupon,
                                           order_instance.user)

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
                                                          created_by=user)
                    if not settings.DEBUG:
                        async_task('order.tasks.send_order_email',
                                   order_instance,
                                   False)

                    return CreateOrder(success=True,
                                       message='Order placed successfully.',
                                       order_id=order_instance.id)
                else:
                    pre_order_setting = PreOrderSetting.objects.filter(producer_product__id=input.products[0].product_id).first()
                    pre_orders = PreOrder.objects.filter(pre_order_setting=pre_order_setting).exclude(pre_order_status='CN')
                    remaining_quantity = pre_order_setting.target_quantity
                    if pre_orders:
                        total_purchased = pre_orders.aggregate(Sum('product_quantity')).get('product_quantity__sum')
                        remaining_quantity = pre_order_setting.target_quantity - total_purchased
                    new_remaining_quantity = remaining_quantity - input.products[0].product_quantity
                    if not pre_order_setting or remaining_quantity == 0 or new_remaining_quantity < 0:
                        return CreateOrder(success=False,
                                           message='Invalid request!')

                    pre_order = PreOrder.objects.create(platform=input.platform,
                                                        product_quantity=input.products[0].product_quantity,
                                                        pre_order_setting=pre_order_setting,
                                                        pre_order_number="PO" + str(uuid.uuid4())[:6].upper(),
                                                        delivery_address=address,
                                                        contact_number=contact_number,
                                                        note=note,
                                                        customer=user,
                                                        created_by=user)
                    if not settings.DEBUG:
                        async_task('order.tasks.send_pre_order_email',
                                   pre_order)
                    return CreateOrder(success=True,
                                       message='Pre-order placed successfully.',
                                       order_id=pre_order.id)
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
                category = [p.product_category.type_of_product for p in products]

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
    payment = PaymentMutation.Field()
    store_transaction_info = TransactionMutation.Field()
