from producer.models import ProducerProduct, ProducerFarm
from rest_framework import serializers


class ProducerProductSerializer(serializers.HyperlinkedModelSerializer):
    # product= serializers.HyperlinkedRelatedField(
    #     # many=True,
    #     read_only=True,
    #     view_name='product'
    # ) # foreignKey
    # product_time = serializers.DateTimeField()
    # amount_of_product = serializers.IntegerField()
    
    def create(self, validated_data):
        return ProducerProduct(**validated_data)

    def update(self, instance, validated_data):
        instance.product = validated_data.get('product', instance.product)
        instance.product_time = validated_data.get('product_time', instance.product_time)
        instance.amount_of_product = validated_data.get('amount_of_product', instance.amount_of_product)
        return instance
    
    
    class Meta:
        model = ProducerProduct
        fields = ['product', 'product_time', 'amount_of_product']


class ProducerFarmSerializer(serializers.HyperlinkedModelSerializer):
    land_amount= serializers.CharField(max_length=30)
    type_of_crops_produce = serializers.CharField(max_length=30)
    product_photo = serializers.ImageField()
    address = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='product'
    ) # foreignKey

    def create(self, validated_data):
        return ProducerFarm(**validated_data)
 
    def update(self, instance, validated_data):
        instance.land_amount = validated_data.get('land_amount', instance.land_amount)
        instance.type_of_crops_produce = validated_data.get('type_of_crops_produce', instance.type_of_crops_produce)
        instance.product_photo = validated_data.get('product_photo', instance.product_photo)
        instance.address = validated_data.get('address', instance.address)
        return instance
    
    
    class Meta:
        model = ProducerFarm
        fields = ['land_amount', 'type_of_crops_produce', 'product_photo', 'address']