from django.utils import timezone
from rest_framework import serializers

from offer.models import OfferProduct, Offer, CartOffer
from order.models import Order, InvoiceInfo, OrderProduct, TimeSlot, DiscountInfo
from product.models import Product
from userProfile.models import UserProfile

all_order_status = {
    'OD': 'Ordered',
    'OA': 'Order Accepted',
    'RE': 'Order Ready',
    'OAD': 'Order At Delivery',
    'COM': 'Order Completed',
    'CN': 'Order Cancelled',
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

    class Meta:
        model = Order
        fields = ["id", "order_number", "created_on", "order_total_price",
                  "customer_name", "customer_mobile_number", "order_status"]
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
        return all_order_status[obj.order_status]


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

    class Meta:
        model = InvoiceInfo
        fields = (
            "invoice_number", "delivery_charge", "discount_amount",
            "paid_status", "payment_method", "offer_id"
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
    customer = CustomerSerializer(source='user')
    invoice = serializers.SerializerMethodField(read_only=True)
    products = OrderProductReadSerializer(read_only=True, many=True)
    order_status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "order_number", "created_on", "delivery_date_time", "delivery_time_slot", "order_total_price",
            "order_status", "total_vat", "contact_number", "delivery_address", "note", "customer", "invoice", "products"
        )

    def get_delivery_time_slot(self, obj):
        time = TimeSlot.objects.filter(time=timezone.localtime(obj.delivery_date_time).time())
        if time:
            return time[0].id
        else:
            return TimeSlot.objects.get(id=1).id

    def get_invoice(self, obj):
        invoice = InvoiceInfo.objects.filter(invoice_number=obj.invoice_number)[0]
        return InvoiceSerializer(invoice).data

    def get_order_status(self, obj):
        return all_order_status[obj.order_status]


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
