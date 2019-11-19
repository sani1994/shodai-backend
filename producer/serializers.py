from producer.models import ProducerProduct, ProducerFarm, BusinessType, ProducerBusiness
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
        instance.is_approved = False
        instance.save()
        return instance

    class Meta:
         model = ProducerProduct
         fields = ('id','product_name','product_category','production_time','unit_price','delivery_amount','is_approved')


class BusinessTypeSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.business_type = self.validated_data.get('business_type',instance.business_type)
        instance.modified_by = validated_data.get('modified_by')
        instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = BusinessType
        fields = ('id','business_type','is_approved')


class ProducerBusinessSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.business_image = validated_data.get('business_image',instance.business_image)
        instance.business_type = validated_data.get('business_type',instance.business_type)
        instance.total_employees = validated_data.get('total_employees',instance.total_employees)
        instance.land_amount = validated_data.get('land_amount',instance.land_amount)
        instance.lat = validated_data.get('lat',instance.lat)
        instance.long = validated_data.get('long',instance.long)
        instance.address = validated_data.get('address',instance.address)
        instance.modified_by = validated_data.get('modified_by')
        instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = ProducerBusiness
        fields = ('id','business_image','business_type','total_employees','land_amount','lat','long','address','is_approved')



