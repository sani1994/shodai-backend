import graphene
from graphene_django.types import DjangoObjectType
from graphene_gis.converter import gis_converter

from userProfile.models import BlackListedToken
from ..models import Order, OrderProduct, Vat, DeliveryCharge, TimeSlot


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


class OrderProductType(DjangoObjectType):
    class Meta:
        model = OrderProduct


class VatType(DjangoObjectType):
    class Meta:
        model = Vat


class DeliveryChargeType(DjangoObjectType):
    class Meta:
        model = DeliveryCharge


class TimeSlotType(DjangoObjectType):
    class Meta:
        model = TimeSlot


class Query(graphene.ObjectType):
    order_list = graphene.List(OrderType)
    order_list_of_user = graphene.List(OrderType)
    order_by_id = graphene.Field(OrderType, order_id=graphene.Int())
    order_product_list_by_order = graphene.List(OrderProductType, order_id=graphene.Int())
    vat_by_product_meta = graphene.Field(VatType, product_meta_id=graphene.Int())
    delivery_charge = graphene.Field(DeliveryChargeType)
    delivery_time_slots = graphene.List(TimeSlotType)

    def resolve_order_list(self, info):
        return Order.objects.all()

    def resolve_order_list_of_user(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in to see order details')
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
                return Order.objects.filter(user=user)

    def resolve_order_by_id(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in to see order')
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
                order_id = kwargs.get('order_id')
                return Order.objects.get(pk=order_id, user=user)

    def resolve_order_product_list_by_order(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in to see order')
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
                order_id = kwargs.get('order_id')
                return OrderProduct.objects.filter(order=order_id)

    def resolve_vat_by_product_meta(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in!')
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
                product_meta = kwargs.get('product_meta_id')
                return Vat.objects.get(product_meta=product_meta)

    def resolve_delivery_charge(self, info):
        return DeliveryCharge.objects.get()

    def resolve_delivery_time_slots(self, info):
        return TimeSlot.objects.all()