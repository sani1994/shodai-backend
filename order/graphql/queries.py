import graphene
from decouple import config
from django.db.models import Q, Sum
from django.utils import timezone
from graphene_django.types import DjangoObjectType
from graphene_gis.converter import gis_converter  # noqa

from base.views import checkAuthentication
from producer.graphql.queries import ProducerProductType  # noqa
from order.models import Order, OrderProduct, Vat, DeliveryCharge, TimeSlot, InvoiceInfo, DiscountInfo, \
    PreOrderSetting, PreOrder
from utility.models import QurbaniProductCriteria
from utility.views import order_status_all


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
        fields = ['id', 'producer_product', 'end_date', 'discounted_price',
                  'delivery_date', 'unit_quantity', 'target_quantity', 'slug']

    product_price = graphene.Int()
    product_unit = graphene.String()
    remaining_quantity = graphene.Int()

    def resolve_product_price(self, info):
        return self.product.product_price

    def resolve_product_unit(self, info):
        return self.product.product_unit.product_unit

    def resolve_remaining_quantity(self, info):
        pre_orders = PreOrder.objects.filter(pre_order_setting=self).exclude(pre_order_status='CN')
        if pre_orders:
            total_purchased = pre_orders.aggregate(Sum('product_quantity')).get('product_quantity__sum')
            remaining_quantity = self.target_quantity - total_purchased
            return remaining_quantity if remaining_quantity > 0 else 0
        else:
            return self.target_quantity


class PreOrderProductDetailType(DjangoObjectType):
    class Meta:
        model = PreOrderSetting
        fields = ['id', 'producer_product', 'end_date', 'discounted_price',
                  'delivery_date', 'unit_quantity', 'target_quantity']

    product_price = graphene.Int()
    product_unit = graphene.String()
    remaining_quantity = graphene.Int()
    total_pre_orders = graphene.Int()

    def resolve_product_price(self, info):
        return self.product.product_price

    def resolve_product_unit(self, info):
        return self.product.product_unit.product_unit

    def resolve_remaining_quantity(self, info):
        pre_orders = PreOrder.objects.filter(pre_order_setting=self).exclude(pre_order_status='CN')
        if pre_orders:
            total_purchased = pre_orders.aggregate(Sum('product_quantity')).get('product_quantity__sum')
            remaining_quantity = self.target_quantity - total_purchased
            return remaining_quantity if remaining_quantity > 0 else 0
        else:
            return self.target_quantity

    def resolve_total_pre_orders(self, info):
        pre_orders_count = PreOrder.objects.filter(pre_order_setting=self).exclude(pre_order_status='CN').count()
        return pre_orders_count


class PreOrderListType(DjangoObjectType):
    class Meta:
        model = PreOrder
        fields = ['id', 'pre_order_number']

    delivery_date = graphene.String()
    pre_order_status = graphene.String()

    def resolve_delivery_date(self, info):
        return self.pre_order_setting.delivery_date

    def resolve_pre_order_status(self, info):
        return order_status_all[self.pre_order_status]


class PreOrderDetailType(DjangoObjectType):
    class Meta:
        model = PreOrder
        fields = ['id', 'pre_order_number', 'product_quantity']

    product_name = graphene.String()
    product_image = graphene.String()
    product_unit = graphene.String()
    discounted_product_price = graphene.Float()
    pre_order_status = graphene.String()

    def resolve_product_name(self, info):
        return self.pre_order_setting.producer_product.product_name

    def resolve_product_image(self, info):
        return self.pre_order_setting.producer_product.product_image

    def resolve_product_unit(self, info):
        return self.pre_order_setting.product.product_unit.product_unit

    def resolve_discounted_product_price(self, info):
        return self.pre_order_setting.discounted_price

    def resolve_pre_order_status(self, info):
        return order_status_all[self.pre_order_status]


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
    pre_order_qurbani_product_list = graphene.List(PreOrderProductListType,
                                                   category=graphene.String(),
                                                   subcategory=graphene.String(),
                                                   breed=graphene.String(),
                                                   color=graphene.String(),
                                                   teeth=graphene.Int())
    pre_order_product_detail = graphene.Field(PreOrderProductDetailType, pre_order_product_id=graphene.Int())
    pre_order_list = graphene.List(PreOrderListType)
    pre_order_detail = graphene.Field(PreOrderDetailType, pre_order_id=graphene.Int())

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
                                              is_processed=False,
                                              start_date__lte=time_now,
                                              end_date__gte=time_now)

    # for temporary use
    def resolve_pre_order_qurbani_product_list(self, info, **kwargs):
        query = Q()
        for field, value in kwargs.items():
            if value:
                query = query & Q(**{field: value})
        time_now = timezone.now()
        return PreOrderSetting.objects.filter(is_approved=True,
                                              is_processed=False,
                                              start_date__lte=time_now,
                                              end_date__gte=time_now,
                                              producer_product__producer__mobile_number=config("QURBANI_PRODUCT_PRODUCER"),
                                              qurbani_products__in=QurbaniProductCriteria.objects.filter(query))

    def resolve_pre_order_product_detail(self, info, **kwargs):
        time_now = timezone.now()
        pre_order_setting_id = kwargs.get('pre_order_product_id')
        return PreOrderSetting.objects.filter(id=pre_order_setting_id,
                                              is_approved=True,
                                              is_processed=False,
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
