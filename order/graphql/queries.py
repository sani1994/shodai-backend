import graphene
from django.db.models import Sum
from django.utils import timezone
from graphene_django.types import DjangoObjectType
from graphene_gis.converter import gis_converter  # noqa

from base.views import checkAuthentication
from producer.graphql.queries import ProducerProductType  # noqa
from order.models import Order, OrderProduct, Vat, DeliveryCharge, TimeSlot, InvoiceInfo, DiscountInfo, \
    PreOrderSetting, PreOrder


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


class InvoiceInfoType(DjangoObjectType):
    class Meta:
        model = InvoiceInfo

    coupon_discount = graphene.Float()
    delivery_charge_discount = graphene.Float()

    def resolve_coupon_discount(self, info):
        discount = DiscountInfo.objects.filter(discount_type='CP', invoice=self)
        if discount:
            return discount[0].discount_amount
        else:
            return None

    def resolve_delivery_charge_discount(self, info):
        discount = DiscountInfo.objects.filter(discount_type='DC', invoice=self)
        if discount:
            return discount[0].discount_amount
        else:
            return None


class PreOrderProductListType(DjangoObjectType):
    class Meta:
        model = PreOrderSetting
        fields = ['id', 'producer_product', 'discounted_price', 'slug']

    product_price = graphene.Int()
    product_unit = graphene.String()

    def resolve_product_price(self, info):
        return self.product.product_price

    def resolve_product_unit(self, info):
        return self.product.product_unit.product_unit


class PreOrderProductDetailType(DjangoObjectType):
    class Meta:
        model = PreOrderSetting
        exclude = ('product', 'start_date', 'slug', 'is_approved',
                   'created_by', 'modified_by', 'created_on', 'modified_on')

    product_price = graphene.Int()
    product_unit = graphene.String()
    remaining_quantity = graphene.Int()

    def resolve_product_price(self, info):
        return self.product.product_price

    def resolve_product_unit(self, info):
        return self.product.product_unit.product_unit

    def resolve_remaining_quantity(self, info):
        pre_orders = PreOrder.objects.filter(pre_order_setting=self)
        if pre_orders:
            total_purchased = pre_orders.aggregate(Sum('product_quantity')).get('product_quantity__sum')
            return self.target_quantity - total_purchased
        else:
            return self.target_quantity


class PreOrderListType(DjangoObjectType):
    class Meta:
        model = PreOrder
        fields = ['id', 'pre_order_number', 'is_cancelled']

    delivery_date = graphene.String()

    def resolve_delivery_date(self, info):
        return self.pre_order_setting.delivery_date


class PreOrderDetailType(DjangoObjectType):
    class Meta:
        model = PreOrder
        fields = ['id', 'pre_order_number', 'is_cancelled', 'product_quantity']

    product_name = graphene.String()
    product_image = graphene.String()
    product_unit = graphene.String()
    discounted_product_price = graphene.Float()

    def resolve_product_name(self, info):
        return self.pre_order_setting.producer_product.product_name

    def resolve_product_image(self, info):
        return self.pre_order_setting.producer_product.product_image

    def resolve_product_unit(self, info):
        return self.pre_order_setting.product.product_unit.product_unit

    def resolve_discounted_product_price(self, info):
        return self.pre_order_setting.discounted_price


class Query(graphene.ObjectType):
    order_list = graphene.List(OrderType)
    order_list_of_user = graphene.List(OrderType)
    order_by_id = graphene.Field(OrderType, order_id=graphene.Int())
    order_product_list_by_order = graphene.List(OrderProductType, order_id=graphene.Int())
    vat_by_product_meta = graphene.Field(VatType, product_meta_id=graphene.Int())
    delivery_charge = graphene.Field(DeliveryChargeType)
    delivery_time_slots = graphene.List(TimeSlotType)
    invoice_by_order = graphene.Field(InvoiceInfoType, order_id=graphene.Int())
    pre_order_product_list = graphene.List(PreOrderProductListType)
    pre_order_product_detail = graphene.List(PreOrderProductDetailType, pre_order_product_id=graphene.Int())
    pre_order_list = graphene.List(PreOrderListType)
    pre_order_detail = graphene.List(PreOrderDetailType, pre_order_id=graphene.Int())

    def resolve_order_list(self, info):
        return Order.objects.all()

    def resolve_order_list_of_user(self, info):
        user = info.context.user
        if checkAuthentication(user, info):
            return Order.objects.filter(user=user).order_by('-created_on')

    def resolve_order_by_id(self, info, **kwargs):
        user = info.context.user
        if checkAuthentication(user, info):
            order_id = kwargs.get('order_id')
            return Order.objects.get(pk=order_id, user=user)

    def resolve_order_product_list_by_order(self, info, **kwargs):
        user = info.context.user
        if checkAuthentication(user, info):
            order_id = kwargs.get('order_id')
            return OrderProduct.objects.filter(order=order_id)

    def resolve_vat_by_product_meta(self, info, **kwargs):
        user = info.context.user
        if checkAuthentication(user, info):
            product_meta = kwargs.get('product_meta_id')
            return Vat.objects.get(product_meta=product_meta)

    def resolve_delivery_charge(self, info):
        return DeliveryCharge.objects.get()

    def resolve_delivery_time_slots(self, info):
        return TimeSlot.objects.filter(allow=True).order_by('time')

    def resolve_invoice_by_order(self, info, **kwargs):
        user = info.context.user
        if checkAuthentication(user, info):
            order_id = kwargs.get('order_id')
            invoice = Order.objects.get(id=order_id).invoice_number
            return InvoiceInfo.objects.get(invoice_number=invoice, user=user)

    def resolve_pre_order_product_list(self, info):
        time_now = timezone.now()
        return PreOrderSetting.objects.filter(is_approved=True,
                                              start_date__lte=time_now,
                                              end_date__gte=time_now)

    def resolve_pre_order_product_detail(self, info, **kwargs):
        time_now = timezone.now()
        pre_order_setting_id = kwargs.get('pre_order_product_id')
        return PreOrderSetting.objects.filter(id=pre_order_setting_id,
                                              is_approved=True,
                                              start_date__lte=time_now,
                                              end_date__gte=time_now).first()

    def resolve_pre_order_list(self, info):
        user = info.context.user
        if checkAuthentication(user, info):
            return PreOrder.objects.filter(order=None, customer=user).order_by('-created_on')

    def resolve_pre_order_detail(self, info, **kwargs):
        user = info.context.user
        if checkAuthentication(user, info):
            pre_order_id = kwargs.get('pre_order_id')
            return PreOrder.objects.filter(id=pre_order_id,
                                           order=None,
                                           customer=user).first()
