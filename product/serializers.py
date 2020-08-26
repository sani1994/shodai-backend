from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import HyperlinkedIdentityField

from product.models import ShopCategory, ProductCategory, ProductMeta, Product
from utility.serializers import ProductUnitSerializer
from utility.models import ProductUnit


class ShopCategorySerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='product_detail',
        lookup_field='id'
    )

    def update(self, instance, validated_data):
        instance.type_of_shop = validated_data.get('type_of_shop', instance.type_of_shop)
        instance.modified_by = validated_data.pop('modified_by')
        instance.save()
        return instance

    class Meta:
        model = ShopCategory
        fields = ('id', 'type_of_shop', 'url')
        # fields = '__all__'


class ProductCategorySerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.type_of_product = validated_data.get('type_of_product', instance.type_of_product)
        instance.img = validated_data.get('img', instance.img)
        instance.modified_by = validated_data.pop('modified_by')
        instance.save()
        return instance

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductMetaSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        shop_category = validated_data.pop('shop_category')
        product_category = validated_data.pop('product_category')
        instance.name = validated_data.get('name', instance.name)
        instance.img = validated_data.get('img', instance.img)
        instance.product_category = product_category
        instance.shop_category = shop_category
        instance.modified_by = validated_data.pop('modified_by')
        instance.save()
        return instance

    class Meta:
        model = ProductMeta
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    # def update(self, instance, validated_data):
    #     product_meta = validated_data.pop('product_meta')
    #
    #     instance.product_name = validated_data.get('product_name', instance.product_name)
    #     instance.product_unit = validated_data.get('product_unit', instance.product_unit)
    #     instance.product_price = validated_data.get('product_price', instance.product_price)
    #     instance.product_image = validated_data.get('product_image',instance.product_image)
    #     instance.product_meta = product_meta
    #     instance.modified_by = validated_data.pop('modified_by')
    #     instance.save()
    #     return instance

    # product_unit = ProductUnitSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_name_bn', 'product_image',
                  'product_unit', 'product_price', 'product_meta',
                  'product_last_price', 'is_approved',
                  'product_description', 'product_description_bn',
                  'price_with_vat']
        read_only = 'product_last_price'


class LatestProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_name_bn',
                  'product_image', 'product_unit', 'product_unit_name',
                  'product_price', 'product_meta', 'product_last_price',
                  'is_approved', 'product_description', 'product_description_bn',
                  'price_with_vat']
        read_only = 'product_last_price'


##########
class RetailerProductSerializer(serializers.ModelSerializer):
    """Serializer for the Retailer Product Inventory"""

    # product_unit = ProductUnitSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'product_name', 'product_name_bn',
                  'product_description', 'product_description_bn',
                  'price_with_vat')
        read_only = ('id')


class ProductForCartSerializer(serializers.ModelSerializer):
    product_quantity = serializers.FloatField(default=1.0)
    product_unit = serializers.CharField(default="")

    def get_product_unit(self, obj):
        return get_object_or_404(ProductUnit, id=obj.product_unit.id)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_description', 'product_price',
                  'product_image', 'product_unit', 'product_quantity', 'product_last_price',
                  'product_name_bn', 'product_description_bn', 'price_with_vat']
