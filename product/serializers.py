from rest_framework import serializers
from product.models import ShopCategory, ProductCategory, ProductMeta, Product


class ShopCategorySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return ShopCategory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.type_of_shop = validated_data.get('type_of_shop', instance.type_of_shop)
        instance.save()
        return instance

    class Meta:
        model = ShopCategory
        fields = ['id','type_of_shop']

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'img','type_of_product']

    def create(self,validated_data):
        return ProductCategory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.type_of_product = validated_data.get('type_of_product', instance.type_of_product)
        instance.save()
        return instance



class ProductMetaSerializer(serializers.ModelSerializer):
    # name= serializers.CharField(max_length=100)
    # product_category = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='product_category'
    # )    # foreignKey
    # shop_category = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='shop_category'
    # )    # foreignKey
    shop_category = serializers.CharField()
    product_category=serializers.CharField()

    def create(self, validated_data):
        shop_category = validated_data.pop('shop_category')
        product_category=validated_data.pop('product_category')
        # shop_category_instance, created=ShopCategory.objects.get_or_create(type_of_shop =shop_category)
        # print("productmataserializer-> create: ", shop_category_instance)
        # product_category_instance, created=ProductCategory.objects.get_or_create(type_of_product=product_category)
        # print("productmataserializer-> create: ", product_category_instance)
        shop_category_instance=ShopCategory.objects.get(pk=shop_category)
        product_category_instance=ProductCategory.objects.get(pk=product_category)
        return ProductMeta.objects.create(**validated_data,shop_category=shop_category_instance,product_category=product_category_instance)

    def update(self, instance, validated_data):
        shop_category = validated_data.pop('shop_category')
        product_category=validated_data.pop('product_category')
        shop_category_instance=ShopCategory.objects.filter(id=shop_category).first()
        product_category_instance=ProductCategory.objects.filter(id=product_category).first()

        instance.name = validated_data.get('name', instance.name)
        # instance.product_category = validated_data.get("product_category", instance.product_category)
        # instance.shop_category = validated_data.get('shop_category', instance.shop_category)
        instance.product_category = product_category_instance
        instance.shop_category = shop_category_instance
        instance.save()
        return instance
    
    
    class Meta:
        model = ProductMeta
        fields = [ 'id','name', 'img', 'product_category', 'shop_category']


class ProductSerializer(serializers.ModelSerializer):
    # product_name= serializers.CharField(max_length=100)
    # product_unit = serializers.CharField(max_length=3)
    # product_price = serializers.IntegerField()
    # product_meta = serializers.RelatedField(
    #     many=True,
    #     read_only=True
    #     # view_name='product_meta'
    # ) # foreignKey
    product_meta = serializers.CharField()
    def create(self, validated_data):
        product_meta = validated_data.pop('product_meta')
        product_meta_instance = ProductMeta.objects.get(pk=product_meta)
        return Product.objects.create(**validated_data,product_meta=product_meta_instance)

    def update(self, instance, validated_data):
        prodcut_meta = validated_data.pop('product_meta')
        prodcut_meta_instance = ProductMeta.objects.filter(id = prodcut_meta).first()

        instance.product_name = validated_data.get('product_name', instance.product_name)
        instance.product_unit = validated_data.get('product_unit', instance.product_unit)
        instance.product_price = validated_data.get('product_price', instance.product_price)
        # instance.product_meta = validated_data.get('product_meta', instance.product_meta)
        instance.product_meta = prodcut_meta_instance
        instance.save()
        return instance
    
    
    
    class Meta:
        model = Product
        fields = [ 'id','product_name', 'product_image', 'product_unit', 'product_price','product_meta']

