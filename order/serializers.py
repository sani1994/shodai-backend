from order.models import Order, OrderProduct, Vat
from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):

    def update(self,instance,validated_data):
        user = self.context['request'].user

        instance.delivery_date_time = validated_data.get('delivery_date_time',instance.delivery_date_time)
        instance.delivery_place =  validated_data.get('delivery_place',instance.delivery_place)
        instance.order_status = validated_data.get('order_status',instance.order_status)
        instance.home_delivery = validated_data.get('home_delivery',instance.home_delivery)
        instance.user = user
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = Order
        fields = '__all__'


class OrderProductSerializer(serializers.ModelSerializer):

    def update(self,instance,validated_data):
        product = self.validated_data.pop('product')
        order = self.validated_data.pop('order')

        instance.orderproduct_qty = self.validated_data.get('orderproduct_qty',instance.orderproduct_qty)
        instance.product = product
        instance.order = order
        instance.save()
        return instance

    class Meta:
        model = OrderProduct
        fields = ('id','order_product_price','order_product_qty','product','order')


class OrderProductReadSerializer(serializers.ModelSerializer): # this serializer has been used to get all the details including foreign key id... this duplication has been made as 'depth=1' is not working for post request in serializer.

    class Meta:
        model = OrderProduct
        fields = ('id','order_product_price','order_product_qty','product','order')
        depth = 2


class VatSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        product_meta = self.validated_data.pop('product_meta')

        instance.vat_amount = self.validated_data.get('vat_amount',instance.vat_amount)
        instance.product_meta = product_meta
        instance.save()
        return instance

    class Meta:
        model = Vat
        fields = '__all__'
        depth = 1
