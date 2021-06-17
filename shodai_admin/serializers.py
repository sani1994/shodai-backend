from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from offer.models import OfferProduct, Offer, CartOffer
from order.models import Order, InvoiceInfo, OrderProduct, TimeSlot, DiscountInfo, PreOrderSetting, PreOrder
from producer.models import ProducerProductRequest
from product.models import Product, ProductMeta
from user.models import UserProfile
from utility.models import DeliveryZone

order_status_all = {
    'OD': 'Ordered',
    'OA': 'Order Accepted',
    'RE': 'Order Ready',
    'OAD': 'Order at Delivery',
    'COM': 'Order Completed',
    'CN': 'Order Cancelled',
}
platform_all = {
    'WB': 'Web',
    'AD': 'Admin',
    'AP': 'App'
}


class AdminUserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['username', 'name', 'email', 'mobile_number']

    def get_name(self, obj):
        if obj.first_name and obj.last_name:
            staff_name = obj.first_name + " " + obj.last_name
        elif obj.first_name:
            staff_name = obj.first_name
        else:
            staff_name = ""
        return staff_name


class OrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_mobile_number = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "order_number", "placed_on", "modified_on", "order_total_price",
                  "customer_name", "customer_mobile_number", "order_status", "platform"]
        read_only_fields = ["customer_name", "customer_mobile_number", "order_status"]

    def get_customer_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            customer_name = obj.user.first_name + " " + obj.user.last_name
        elif obj.user.first_name:
            customer_name = obj.user.first_name
        else:
            customer_name = ""
        return customer_name

    def get_customer_mobile_number(self, obj):
        return obj.user.mobile_number

    def get_order_status(self, obj):
        return order_status_all[obj.order_status]

    def get_platform(self, obj):
        return platform_all[obj.platform]


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "name", "mobile_number", "email"]
        read_only_fields = ["name", "mobile_number", "email"]

    def get_name(self, obj):
        if obj.first_name and obj.last_name:
            customer_name = obj.first_name + " " + obj.last_name
        elif obj.first_name:
            customer_name = obj.first_name
        else:
            customer_name = ""
        return customer_name


class InvoiceSerializer(serializers.ModelSerializer):
    payment_method = serializers.SerializerMethodField(read_only=True)
    offer_id = serializers.SerializerMethodField(read_only=True)
    coupon_discount = serializers.SerializerMethodField(read_only=True)
    additional_discount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InvoiceInfo
        fields = (
            "invoice_number", "delivery_charge", "discount_amount", "paid_status",
            "payment_method", "offer_id", "coupon_discount", "additional_discount"
        )
        read_only_fields = ["invoice_number", "discount_amount", "payment_method", "offer_id"]

    def get_payment_method(self, obj):
        return 'Cash on Delivery' if obj.payment_method == 'CASH_ON_DELIVERY' else 'Online Payment'

    def get_offer_id(self, obj):
        discount = DiscountInfo.objects.filter(discount_type='DC', invoice=obj)
        if discount:
            return discount[0].offer.id
        else:
            return None

    def get_coupon_discount(self, obj):
        discount = DiscountInfo.objects.filter(discount_type='CP', invoice=obj)
        if discount:
            return discount[0].discount_amount
        else:
            return None

    def get_additional_discount(self, obj):
        discount = DiscountInfo.objects.filter(discount_type='AD', invoice=obj)
        if discount:
            return discount[0].discount_amount
        else:
            return None


class OrderProductReadSerializer(serializers.ModelSerializer):
    decimal_allowed = serializers.SerializerMethodField(read_only=True)
    product_id = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    product_price = serializers.SerializerMethodField(read_only=True)
    product_price_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ['order_product_price', 'product_price', 'order_product_unit', 'order_product_qty',
                  'decimal_allowed', 'product_id', 'product_name', 'product_image', 'product_price_total']

    def get_decimal_allowed(self, obj):
        return obj.product.decimal_allowed

    def get_product_id(self, obj):
        return obj.product.id

    def get_product_name(self, obj):
        return obj.product.product_name

    def get_product_image(self, obj):
        return obj.product.product_image.url

    def get_product_price(self, obj):
        if obj.order_product_price != obj.product_price:
            return obj.product_price
        else:
            return None

    def get_product_price_total(self, obj):
        return obj.order_product_price * obj.order_product_qty


class OrderDetailSerializer(serializers.ModelSerializer):
    delivery_time_slot = serializers.SerializerMethodField(read_only=True)
    delivery_address = serializers.StringRelatedField(source='address')
    order_status = serializers.SerializerMethodField(read_only=True)
    platform = serializers.SerializerMethodField(read_only=True)
    zone = serializers.SerializerMethodField(read_only=True)
    customer = CustomerSerializer(source='user')
    invoice = serializers.SerializerMethodField(read_only=True)
    products = OrderProductReadSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = (
            "id", "order_number", "placed_on", "modified_on", "platform", "delivery_date_time",
            "delivery_time_slot", "order_total_price", "order_status", "total_vat", "remarks",
            "contact_number", "delivery_address", "note", "zone", "customer", "invoice", "products",
        )

    def get_delivery_time_slot(self, obj):
        time = TimeSlot.objects.filter(time=timezone.localtime(obj.delivery_date_time).time())
        if time:
            return time[0].id
        else:
            return TimeSlot.objects.filter(allow=True).order_by('time')[0].id

    def get_invoice(self, obj):
        invoice = InvoiceInfo.objects.filter(invoice_number=obj.invoice_number)[0]
        return InvoiceSerializer(invoice).data

    def get_order_status(self, obj):
        return order_status_all[obj.order_status]

    def get_platform(self, obj):
        return platform_all[obj.platform]

    def get_zone(self, obj):
        return obj.delivery_zone.id if obj.delivery_zone else None


class ProductSearchSerializer(serializers.ModelSerializer):
    offer_price = serializers.SerializerMethodField()

    def get_offer_price(self, obj):
        today = timezone.now()
        offer_product = OfferProduct.objects.filter(product=obj,
                                                    is_approved=True,
                                                    offer__is_approved=True,
                                                    offer__offer_starts_in__lte=today,
                                                    offer__offer_ends_in__gte=today)
        if offer_product:
            return offer_product[0].offer_price
        else:
            return None

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_price', 'product_image',
                  'product_unit_name', 'offer_price', 'decimal_allowed']
        read_only_fields = ['offer_price', ]


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ('id', 'slot', 'time')


class DeliveryChargeOfferSerializer(serializers.ModelSerializer):
    updated_delivery_charge = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ('id', 'offer_name', 'updated_delivery_charge')

    def get_updated_delivery_charge(self, obj):
        cart_offer = CartOffer.objects.filter(offer=obj)

        if cart_offer:
            return cart_offer[0].updated_delivery_charge
        else:
            return None


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    orders = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "name", "mobile_number", "email", "created_on",
                  "is_approved", "orders"]

    def get_name(self, obj):
        if obj.first_name and obj.last_name:
            customer_name = obj.first_name + " " + obj.last_name
        elif obj.first_name:
            customer_name = obj.first_name
        else:
            customer_name = ""
        return customer_name

    def get_orders(self, obj):
        return Order.objects.filter(user=obj).exclude(order_status='CN').count()


class ProductMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMeta
        fields = ['id', 'name']


class PreOrderSettingListSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PreOrderSetting
        fields = ['id', 'product_name', 'start_date', 'end_date',
                  'discounted_price', 'is_approved', 'is_processed']

    def get_product_name(self, obj):
        return obj.producer_product.product_name


class ProducerProductSerializer(serializers.ModelSerializer):
    producer = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProducerProductRequest
        fields = ['id', 'product_name', 'product_image', 'product_unit',
                  'product_price', 'product_quantity', 'producer']

    def get_producer(self, obj):
        return f"{obj.producer.first_name} [{obj.producer.mobile_number}]"


class PreOrderSettingDetailSerializer(serializers.ModelSerializer):
    pre_orders = None
    producer_product = ProducerProductSerializer(read_only=True)
    product_id = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    product_price = serializers.SerializerMethodField(read_only=True)
    product_unit = serializers.SerializerMethodField(read_only=True)
    remaining_quantity = serializers.SerializerMethodField(read_only=True)
    total_pre_orders = serializers.SerializerMethodField(read_only=True)
    total_pre_order_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PreOrderSetting
        fields = ['id', 'start_date', 'end_date', 'delivery_date', 'discounted_price', 'unit_quantity',
                  'target_quantity', 'remaining_quantity', 'is_approved', 'is_processed',
                  'product_id', 'product_name', 'product_image', 'product_unit', 'product_price',
                  'total_pre_orders', 'total_pre_order_amount', 'producer_product']

    def get_product_id(self, obj):
        return obj.product.id

    def get_product_name(self, obj):
        return obj.product.product_name

    def get_product_image(self, obj):
        return obj.product.product_image.url

    def get_product_price(self, obj):
        return obj.product.product_price

    def get_product_unit(self, obj):
        return obj.product.product_unit.product_unit

    def get_remaining_quantity(self, obj):
        pre_orders = PreOrder.objects.filter(pre_order_setting=obj).exclude(pre_order_status='CN')
        self.pre_orders = pre_orders
        if pre_orders:
            total_purchased = pre_orders.aggregate(Sum('product_quantity')).get('product_quantity__sum')
            remaining_quantity = obj.target_quantity - total_purchased
            return remaining_quantity if remaining_quantity > 0 else 0
        else:
            return obj.target_quantity

    def get_total_pre_orders(self, obj):
        return self.pre_orders.count()

    def get_total_pre_order_amount(self, obj):
        total_amount = 0
        for pre_order in self.pre_orders:
            total_amount += pre_order.pre_order_setting.discounted_price * pre_order.product_quantity
        return total_amount


class PreOrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField(read_only=True)
    customer_mobile_number = serializers.SerializerMethodField(read_only=True)
    pre_order_product = serializers.SerializerMethodField(read_only=True)
    is_processed = serializers.SerializerMethodField(read_only=True)
    pre_order_status = serializers.SerializerMethodField(read_only=True)
    platform = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PreOrder
        fields = ['id', 'pre_order_number', 'pre_order_status', 'created_on', 'customer_name',
                  'customer_mobile_number', 'is_processed', 'pre_order_product', 'platform']

    def get_customer_name(self, obj):
        return obj.customer.first_name

    def get_customer_mobile_number(self, obj):
        return obj.customer.mobile_number

    def get_pre_order_product(self, obj):
        return obj.pre_order_setting.id

    def get_is_processed(self, obj):
        return 'Yes' if obj.pre_order_setting.is_processed else 'No'

    def get_pre_order_status(self, obj):
        return order_status_all[obj.pre_order_status]

    def get_platform(self, obj):
        return platform_all[obj.platform]


class PreOrderDetailSerializer(serializers.ModelSerializer):
    pre_order_product = serializers.StringRelatedField(source='pre_order_setting')
    product_unit = serializers.SerializerMethodField(read_only=True)
    address = serializers.StringRelatedField(source='delivery_address')
    platform = serializers.SerializerMethodField(read_only=True)
    pre_order_status = serializers.SerializerMethodField(read_only=True)
    customer_details = CustomerSerializer(source='customer')
    unit_quantity = serializers.SerializerMethodField(read_only=True)
    remaining_quantity = serializers.SerializerMethodField(read_only=True)
    is_approved = serializers.SerializerMethodField(read_only=True)
    is_processed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PreOrder
        fields = ['id', 'pre_order_number', 'pre_order_product', 'product_quantity', 'product_unit', 'address',
                  'contact_number', 'note', 'platform', 'pre_order_status', 'order', 'customer_details',
                  'unit_quantity', 'remaining_quantity', 'is_approved', 'is_processed']

    def get_product_unit(self, obj):
        return obj.pre_order_setting.product.product_unit.product_unit

    def get_platform(self, obj):
        return platform_all[obj.platform]

    def get_pre_order_status(self, obj):
        return order_status_all[obj.pre_order_status]

    def get_unit_quantity(self, obj):
        return obj.pre_order_setting.unit_quantity

    def get_remaining_quantity(self, obj):
        pre_orders = PreOrder.objects.filter(pre_order_setting=obj.pre_order_setting).exclude(pre_order_status='CN')
        if pre_orders:
            total_purchased = pre_orders.aggregate(Sum('product_quantity')).get('product_quantity__sum')
            remaining_quantity = obj.pre_order_setting.target_quantity - total_purchased
            return remaining_quantity if remaining_quantity > 0 else 0
        else:
            return obj.pre_order_setting.target_quantity

    def get_is_approved(self, obj):
        return obj.pre_order_setting.is_approved

    def get_is_processed(self, obj):
        return obj.pre_order_setting.is_processed


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = ('id', 'zone')


class PreOrderSettingActiveListSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    product_price = serializers.SerializerMethodField(read_only=True)
    product_unit = serializers.SerializerMethodField(read_only=True)
    remaining_quantity = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PreOrderSetting
        fields = ['id', 'start_date', 'end_date', 'delivery_date', 'unit_quantity',
                  'target_quantity', 'remaining_quantity', 'product_name', 'product_image',
                  'product_unit', 'product_price', 'discounted_price']

    def get_product_name(self, obj):
        return obj.producer_product.product_name

    def get_product_image(self, obj):
        return obj.producer_product.product_image.url

    def get_product_price(self, obj):
        return obj.product.product_price

    def get_product_unit(self, obj):
        return obj.product.product_unit.product_unit

    def get_remaining_quantity(self, obj):
        pre_orders = PreOrder.objects.filter(pre_order_setting=obj).exclude(pre_order_status='CN')
        if pre_orders:
            total_purchased = pre_orders.aggregate(Sum('product_quantity')).get('product_quantity__sum')
            remaining_quantity = obj.target_quantity - total_purchased
            return remaining_quantity if remaining_quantity > 0 else 0
        else:
            return obj.target_quantity
