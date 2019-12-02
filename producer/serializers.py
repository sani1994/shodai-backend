from producer.models import ProducerBulkRequest, ProducerFarm, BusinessType, ProducerBusiness, BulkOrderProducts, \
    BulkOrder, MicroBulkOrder, MicroBulkOrderProducts, BulkOrderReqConnector, CustomerMicroBulkOrderProductRequest
from rest_framework import serializers


class ProducerFarmSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = ProducerFarm.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

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


class ProducerBulkRequestSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj= ProducerBulkRequest.objects.create(**validated_data, user=user)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.product_name = validated_data.get('product_name',instance.product_name)
        instance.product_image =  validated_data.get('product_image',instance.product_image)
        instance.product_category = validated_data.pop('product_category')
        instance.production_time = validated_data.get('production_time',instance.production_time)
        instance.unit=validated_data.get('unit',instance.unit)
        instance.unit_price = validated_data.get('unit_price',instance.unit_price)
        instance.delivery_amount = validated_data.get('quantity',instance.quantity)
        instance.general_price=validated_data.get('general_price',instance.general_price)
        instance.general_qty=validated_data.get('general_qty',instance.general_qty)
        instance.general_unit=validated_data.get('general_unit',instance.general_unit)
        instance.offer_price=validated_data.get('offer_price',instance.offer_price)
        instance.offer_qty=validated_data.get('offer_qty',instance.offer_qty)
        instance.offer_unit=validated_data.get('offer_unit',instance.offer_unit)
        instance.modified_by = validated_data.get('modified_by')
        instance.is_approved = False
        instance.save()
        return instance

    class Meta:
         model = ProducerBulkRequest
         # fields = ('id','product_name','product_category','production_time','unit_price','delivery_amount','is_approved')
         fields =  '__all__'


class BusinessTypeSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = BusinessType.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

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

    def create(self, validated_data):
        user = self.context['request'].user
        obj = ProducerBusiness.objects.create(**validated_data,user=user)
        obj.created_by = user
        obj.save()
        return obj

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


class BulkOrderProductsSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = BulkOrderProducts.objects.create(**validated_data, user=user)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.product = validated_data.get('product',instance.product)
        instance.bulk_order = validated_data.get('bulk_order',instance.bulk_order)
        instance.general_price = validated_data.get('general_price',instance.general_price)
        instance.offer_price = validated_data.get('offer_price',instance.offer_price)
        instance.target_qty = validated_data.get('target_qty',instance.target_qty)
        instance.modified_by = validated_data.get('modified_by')
        # instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = BulkOrderProducts
        fields = '__all__'


class BulkOrderSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = BulkOrder.objects.create(**validated_data, user=user)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.expire_date = validated_data.get('expire_date', instance.expire_date)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.modified_by = validated_data.get('modified_by')
        # instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = BulkOrder
        fields = '__all__'


class MicroBulkOrderSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = MicroBulkOrder.objects.create(**validated_data,customer=user)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.bulk_order = validated_data.pop('bulk_order')
        instance.modified_by = validated_data.get('modified_by')
        # instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = MicroBulkOrder
        fields = '__all__'


class MicroBulkOrderProductsSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = MicroBulkOrderProducts.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.bulk_order_products = validated_data.pop('bulk_order_products')
        instance.bulk_order_products = validated_data.pop('micro_bulk_order')
        instance.qty = validated_data.get('qty', instance.qty)
        instance.order = validated_data.pop('order')
        instance.modified_by = validated_data.get('modified_by')
        # instance.is_approved = False
        instance.save()
        return instance


    class Meta:
        model = MicroBulkOrderProducts
        fields = '__all__'


class BulkOrderReqConntrSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = BulkOrderReqConnector.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.producer_bulk_request = validated_data.pop('producer_bulk_request')
        instance.bulk_order = validated_data.pop('bulk_order')
        instance.modified_by = validated_data.get('modified_by')
        # instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = BulkOrderReqConnector
        fields = '__all__'


class CustomerMicroBulkOrderProductRequestSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = CustomerMicroBulkOrderProductRequest.objects.create(**validated_data,customer=user)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.micro_bulk_order_product = validated_data.pop('micro_bulk_order_product')
        instance.qty = validated_data.get('qty',instance.qty)
        instance.modified_by = validated_data.get('modified_by')
        # instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = CustomerMicroBulkOrderProductRequest
        fields = '__all__'
        # depth = 3
