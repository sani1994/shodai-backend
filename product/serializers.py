from rest_framework import serializers
from product.models import ShopCategory, ProductCategory, ProductMeta, Product


class ShopCategorySerializer(serializers.HyperlinkedModelSerializer):
    type_of_shop= serializers.CharField(max_length=89)

    def create(self, validated_data):
        return ShopCategory(**validated_data)

    def update(self, instance, validated_data):
        instance.type_of_shop = validated_data.get('type_of_shop', instance.type_of_shop)
        return instance
    
    
    class Meta:
        model = ShopCategory
        fields = ['type_of_shop']


class ProductCategorySerializer(serializers.HyperlinkedModelSerializer):
    type_of_product= serializers.CharField(max_length=89)

    def create(self, validated_data):
        return ProductCategory(**validated_data)

    def update(self, instance, validated_data):
        instance.type_of_product = validated_data.get('type_of_product', instance.type_of_product)
        return instance
    
    
    class Meta:
        model = ProductCategory
        fields = [ 'type_of_product']


class ProductMetaSerializer(serializers.HyperlinkedModelSerializer):
    name= serializers.CharField(max_length=100)
    product_category = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='product_category'
    )    # foreignKey
    shop_category = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='shop_category'
    )    # foreignKey

    def create(self, validated_data):
        return ProductMeta(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.product_category = validated_data.get('product_category', instance.product_category)
        instance.shop_category = validated_data.get('shop_category', instance.shop_category)
        return instance
    
    
    class Meta:
        model = ProductMeta
        fields = [ 'name', 'product_category', 'shop_category']


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    product_name= serializers.CharField(max_length=100)
    product_unit = serializers.CharField(max_length=3)
    product_price = serializers.IntegerField()
    product_meta = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='product_meta'
    ) # foreignKey
    def create(self, validated_data):
        return Product(**validated_data)

    def update(self, instance, validated_data):
        instance.product_name = validated_data.get('product_name', instance.product_name)
        instance.product_unit = validated_data.get('product_unit', instance.product_unit)
        instance.product_price = validated_data.get('product_price', instance.product_price)
        instance.product_meta = validated_data.get('product_meta', instance.product_meta)
        return instance
    
    
    
    class Meta:
        model = Product
        fields = [ 'product_name', 'product_unit', 'product_price', 'product_meta']
