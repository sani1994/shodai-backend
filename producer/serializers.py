from producer.models import ProducerProduct, ProducerFarm
from rest_framework import serializers


class ProducerFarmSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.land_amount = validated_data.get('land_amount', instance.land_amount)
        instance.type_of_crops_produce = validated_data.get('type_of_crops_produce', instance.type_of_crops_produce)
        instance.product_photo = validated_data.get('product_photo', instance.product_photo)
        instance.address = validated_data.pop('address')
        instance.save()
        return instance

    class Meta:
        model = ProducerFarm
        fields = ['land_amount', 'type_of_crops_produce', 'product_photo', 'address']


class ProducerProductSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.product_name = validated_data.get('product_name',instance.product_name)
        instance.product_image =  validated_data.get('product_image',instance.product_image)
        instance.product_category = validated_data.pop('product_category')
        instance.production_time = validated_data.get('production_time',instance.production_time)
        instance.unit_price = validated_data.get('unit_price',instance.unit_price)
        instance.delivery_amount = validated_data.get('delivery_amount',instance.delivery_amount)
        instance.modified_by = validated_data.get('modified_by')
        instance.save()

    class Meta:
         model = ProducerProduct
         fields = ('id','product_name','product_category','production_time','unit_price','delivery_amount')


