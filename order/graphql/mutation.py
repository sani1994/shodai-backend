import json

import graphene
import requests
from decouple import config

from graphene_django import DjangoObjectType
from graphql_relay.utils import unbase64

from utility.notification import email_notification
from .queries import OrderType, OrderProductType
from ..models import Order, OrderProduct, PaymentInfo, DeliveryCharge
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
    delivery_place = graphene.String(required=True)
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
        if user.is_anonymous:
            raise Exception('Must Log In!')
        else:
            token = info.context.headers['Authorization'].split(' ')[1]
            print(token)
            try:
                token = BlackListedToken.objects.get(token=token)
            except BlackListedToken.DoesNotExist as e:
                token = None
            if token:
                raise Exception('Invalid or expired token!')
            else:
                if user.user_type == 'CM':
                    order_instance = Order(user=user,
                                           delivery_date_time=input.delivery_date_time,
                                           delivery_place=input.delivery_place,
                                           order_total_price=input.net_pay_able_amount,
                                           lat=input.lat,
                                           long=input.long,
                                           order_status="OD",
                                           order_type=input.order_type,
                                           contact_number=input.contact_number if input.contact_number else user.mobile_number
                                           )
                    order_instance.address = Address.objects.get(id=input.address)
                    order_instance.save()
                    datetime = order_instance.delivery_date_time.strftime("%m/%d/%Y, %H:%M:%S")

                    product_list = input.products
                    print(product_list)
                    product_list_detail = []
                    for p in product_list:
                        product_id = from_global_id(p.product_id)
                        product = Product.objects.get(id=product_id)
                        OrderProduct.objects.create(product=product,
                                                    order=Order.objects.get(pk=order_instance.pk),
                                                    order_product_price=product.product_price,
                                                    order_product_price_with_vat=product.price_with_vat,
                                                    vat_amount=product.product_meta.vat_amount,
                                                    order_product_qty=p.order_product_qty, )
                        product_list_detail.append(product.product_name + " " + product.product_unit.product_unit + "*"
                                                   + str(p.order_product_qty) + "\n")

                    print(product_list_detail)
                    sub = "Order Placed"
                    body = f"Dear Concern,\r\nUser phone number :{user.mobile_number} \r\nUser type: {user.user_type} " \
                           f"posted an order with the following details" \
                           f" \r\nOrder id: {order_instance.pk}." \
                           f" \r\nOrdered product list with quantity:\n {' '.join(product_list_detail)}" \
                           f" \r\nOrder delivery date and time: {datetime}." \
                           f" \r\nOrder delivery area: {order_instance.delivery_place}." \
                           f" \r\nOrder delivery address: {order_instance.address}." \
                           f" \r\nOrder total price: {order_instance.order_total_price}." \
                           f" \r\nOrder vat amount: {input.total_vat}." \
                           f" \r\nOrder delivery charge: {DeliveryCharge.objects.get()}." \
                           f" \r\nOrder net payable amount: {input.net_pay_able_amount}." \
                           f"\r\n \r\nThanks and Regards\r\nShodai "
                    email_notification(sub, body)
                    return CreateOrder(order=order_instance)
                else:
                    raise Exception('Unauthorized request!')


class CreateOrderProduct(graphene.Mutation):
    class Arguments:
        input = OrderProductInputA(required=True)

    order_product = graphene.Field(OrderProductType)

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Must Log In!')
        else:
            token = info.context.headers['Authorization'].split(' ')[1]
            print(token)
            try:
                token = BlackListedToken.objects.get(token=token)
            except BlackListedToken.DoesNotExist as e:
                token = None
            if token:
                raise Exception('Invalid or expired token!')
            else:
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
        if user.is_anonymous:
            raise Exception('Must Log In!')
        else:
            token = info.context.headers['Authorization'].split(' ')[1]
            print(token)
            try:
                token = BlackListedToken.objects.get(token=token)
            except BlackListedToken.DoesNotExist as e:
                token = None
            if token:
                raise Exception('Invalid or expired token!')
            else:
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
                    print(content)
                    if response.status_code == 200:
                        if content["status"] == "success":
                            payment_id = content["payment_id"]
                            order_id = obj.pk
                            bill_id = obj.bill_id
                            invoice_number = obj.invoice_number
                            print(invoice_number)
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
