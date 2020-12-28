from rest_framework import serializers

from order.models import Order, InvoiceInfo, OrderProduct
from userProfile.models import UserProfile


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = 'username', 'first_name', 'last_name', 'mobile_number', 'user_type', 'email'


class OrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_mobile_number = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "created_on", "order_total_price",
                  "customer_name", "customer_mobile_number", "order_status"]
        read_only_fields = ["customer_name", "customer_mobile_number", "order_status"]

    def get_customer_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            customer_name = obj.user.first_name + " " + obj.user.last_name
        else:
            customer_name = obj.user.username
        return customer_name

    def get_customer_mobile_number(self, obj):
        return obj.user.mobile_number

    def get_order_status(self, obj):
        all_order_status = {
            'OD': 'Ordered',
            'OA': 'Order Accepted',
            'RE': 'Order Ready',
            'OAD': 'Order At Delivery',
            'COM': 'Order Completed',
            'CN': 'Order Cancelled',
        }
        return all_order_status[obj.order_status]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceInfo
        fields = (
            "invoice_number", "billing_person_name", "billing_person_email",
            "billing_person_mobile_number", "delivery_charge",
            "discount_amount", "paid_status", "payment_method"
        )


class OrderProductReadSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)
    product_price_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ('product_name', 'order_product_price', 'order_product_qty', 'product_price_total')

    def get_product_name(self, obj):
        return obj.product.product_name

    def get_product_price_total(self, obj):
        return obj.order_product_price * obj.order_product_qty


class OrderDetailSerializer(serializers.ModelSerializer):
    invoice = serializers.SerializerMethodField(read_only=True)
    products = OrderProductReadSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = (
            "id", "created_on", "delivery_date_time", "order_total_price", "total_vat",
            "contact_number", "invoice", "products"
        )

    def get_invoice(self, obj):
        invoice = InvoiceInfo.objects.filter(order_number=obj).order_by('-created_on')[0]
        return InvoiceSerializer(invoice).data
