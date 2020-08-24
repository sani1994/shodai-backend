from order.models import (
    Order,
    OrderProduct,
    Vat,
    DeliveryCharge,
    PaymentInfo,
    TimeSlot
)
from rest_framework import serializers

from userProfile.models import Address
from userProfile.serializers import AddressSerializer
from userProfile.serializers import UserProfileSerializer


class OrderSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        user = self.context['request'].user

        instance.delivery_date_time = validated_data.get('delivery_date_time', instance.delivery_date_time)
        instance.delivery_place = validated_data.get('delivery_place', instance.delivery_place)
        instance.order_status = validated_data.get('order_status', instance.order_status)
        instance.home_delivery = validated_data.get('home_delivery', instance.home_delivery)
        instance.user = user
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = Order
        fields = (
            "id", "created_on", "modified_on", "payment_id", "invoice_number",
            "bill_id", "currency", "delivery_date_time", "delivery_place", "order_total_price",
            "lat", "long", "order_geopoint", "order_status", "home_delivery", "order_type",
            "contact_number", "created_by", "modified_by", "user", "address", "paid_status",
        )

        read_only = ('id', "paid_status")


class OrderSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only = ('id',)
        depth = 2


class OrderProductSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        product = self.validated_data.pop('product')
        order = self.validated_data.pop('order')

        instance.orderproduct_qty = self.validated_data.get('orderproduct_qty', instance.orderproduct_qty)
        instance.product = product
        instance.order = order
        instance.save()
        return instance

    class Meta:
        model = OrderProduct
        fields = ('id', 'order_product_price', 'order_product_qty', 'product', 'order',)
        read_only = ('id',)


class OrderProductReadSerializer(
    serializers.ModelSerializer):  # this serializer has been used to get all the details including foreign key id... this duplication has been made as 'depth=1' is not working for post request in serializer.

    class Meta:
        model = OrderProduct
        fields = ('id', 'order_product_price', 'order_product_qty', 'product', 'order')
        depth = 2


class VatSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        product_meta = self.validated_data.pop('product_meta')

        instance.vat_amount = self.validated_data.get('vat_amount', instance.vat_amount)
        instance.product_meta = product_meta
        instance.save()
        return instance

    class Meta:
        model = Vat
        fields = '__all__'


class DeliveryChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCharge
        fields = '__all__'


class OrderProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ('id', 'order_product_price', 'order_product_qty', 'product')
        depth = 2


class OrderDetailSerializer(serializers.ModelSerializer):
    # order = OrderSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)
    # products = OrderProductSerializer(read_only=True, many=True)
    products = OrderProductDetailsSerializer(read_only=True, many=True)
    address = AddressSerializer(read_only=True)
    created_on = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    # delivery_date_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Order
        fields = '__all__'
        # depth = 2


class OrderDetailPaymentSerializer(serializers.ModelSerializer):
    """Create serializer for Order Details"""
    # order = OrderSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)
    products = OrderProductSerializer(read_only=True, many=True)
    created_on = serializers.DateTimeField(format=None)

    class Meta:
        model = Order
        fields = '__all__'


class PaymentInfoSerializer(serializers.ModelSerializer):
    """Create serializer for PaymentInfo object"""

    class Meta:
        model = PaymentInfo
        fields = ('__all__')
        read_only = ('id',)


class PaymentInfoDetailSerializer(serializers.ModelSerializer):
    """Create serializer for PaymentInfo object"""

    # order = OrderProductReadSerializer(read_only=True)
    # order_set = OrderSerializer(read_only=True, many=True)

    class Meta:
        model = PaymentInfo
        fields = ('__all__')
        read_only = ('id',)


class TimeSlotSerializer(serializers.ModelSerializer):
    """Create serializer for TimeSlot object"""

    class Meta:
        model = TimeSlot
        fields = ('slot',)
