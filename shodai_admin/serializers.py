from django.shortcuts import get_object_or_404

from order.models import Order, InvoiceInfo, OrderProduct
from product.models import Product
from userProfile.models import UserProfile
from rest_framework import serializers


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = 'username', 'first_name', 'last_name', 'mobile_number', 'user_type', 'email'


class OrderListSerializer(serializers.ModelSerializer):
    customer_mobile_number = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id", "created_on", "delivery_date_time", "customer_mobile_number", "customer_name",
            "order_total_price", "order_status", "contact_number"
        )
        read_only_fields = ["customer_mobile_number", "customer_name"]

    def get_customer_mobile_number(self, obj):
        return obj.user.mobile_number

    def get_customer_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name


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
        invoice = get_object_or_404(InvoiceInfo, order_number=obj)
        return InvoiceSerializer(invoice).data

    def get_products(self, obj):
        order_product = get_object_or_404(OrderProduct, order=obj)
        return OrderProductReadSerializer(order_product, many=True).data
