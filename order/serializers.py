from order.models import Order, OrderProduct, Vat
from rest_framework import serializers


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    user_id= serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='user_id'
    ) # foreignKey
    delivery_date_time = serializers.DateTimeField()
    delivery_place = serializers.CharField(max_length=100)
    
    # ORDERED = 'OD'              # ORDER COLLECT FROM CUSTOMER
    # ORDER_READY = 'RE'          # ORDER IS READY FOR DELIVERY PERSON
    # ORDER_AT_DELIVERY = 'OAD'   # ORDER IS WITH DELIVERY PEROSN
    # ORDER_COMPLETED = 'COM'      # ORDER IS DELIVERED TO CUSTOMER
    # ORDER_CANCELLED = 'CN'      # ORDER IS CANCEL BY CUSTOMER
    # ORDER_STATUS = [
    #     (ORDERED, 'Ordered'),
    #     (ORDER_READY, 'Order Ready'),
    #     (ORDER_AT_DELIVERY, 'Order At Delivery'),
    #     (ORDER_COMPLETED, 'Order Completed'),
    #     (ORDER_CANCELLED, 'Order Cancelled'),
    # ]
    order_status = serializers.CharField(max_length=100)
    home_delivery = serializers.BooleanField(default=True)

    def create(self, validated_data):
        return Order(**validated_data)
 
    def update(self, instance, validated_data):
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.delivery_date_time = validated_data.get('delivery_date_time', instance.delivery_date_time)
        instance.delivery_place = validated_data.get('delivery_place', instance.delivery_place)
        instance.order_status = validated_data.get('order_status', instance.order_status)
        instance.home_delivery  = validated_data.get('home_delivery', instance.home_delivery)
        return instance
    
    class Meta:
        model = Order
        fields = ['id', 'delivery_date_time', 'delivery_place', 'order_status', 'home_delivery', 'user_id']
        # fields = ['user_id', 'delivery_date_time', 'delivery_place', 'order_status', 'home_delivery']


class OrderProductSerializer(serializers.HyperlinkedModelSerializer):
    product_id= serializers.HyperlinkedRelatedField(
        # many=True,
        read_only=True,
        view_name='product_id'
    ) # foreignKey
    order_id = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='order_id'
    ) # foreignKey
    

    def create(self, validated_data):
        return OrderProduct(**validated_data)
 
    def update(self, instance, validated_data):
        instance.product_id = validated_data.get('product_id', instance.product_id)
        instance.order_id = validated_data.get('order_id', instance.order_id)
        return instance
    
    class Meta:
        model = OrderProduct
        fields = ['product_id', 'order_id']

class VatSerializer(serializers.HyperlinkedModelSerializer):
    product_meta= serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='product_meta'
    ) # foreignKey
    vat_amount = serializers.IntegerField(default=True)
    

    def create(self, validated_data):
        return Vat(**validated_data)
 
    def update(self, instance, validated_data):
        instance.product_meta = validated_data.get('product_meta', instance.product_meta)
        instance.vat_amount = validated_data.get('vat_amount', instance.vat_amount)
        return instance
    
    class Meta:
        model = Vat
        fields = ['product_meta', 'vat_amount']