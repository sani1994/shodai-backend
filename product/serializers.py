from rest_framework import serializers
from product.models import ShopCategory, ProductCategory, ProductMeta, Product


class ShopCategorySerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.type_of_shop = validated_data.get('type_of_shop', instance.type_of_shop)
        instance.save()
        return instance

    class Meta:
        model = ShopCategory
        fields = ['id','type_of_shop']


class ProductCategorySerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.type_of_product = validated_data.get('type_of_product', instance.type_of_product)
        instance.img = validated_data.get('img',instance.img)
        instance.save()
        return instance

    class Meta:
        model = ProductCategory
        # fields = ['id', 'img','type_of_product']
        fields = '__all__'


class ProductMetaSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        shop_category = validated_data.pop('shop_category')
        product_category=validated_data.pop('product_category')
        instance.name = validated_data.get('name', instance.name)
        instance.img = validated_data.get('img',instance.img)
        instance.product_category = product_category
        instance.shop_category = shop_category
        instance.save()
        return instance

    class Meta:
        model = ProductMeta
        fields = [ 'id','name', 'img', 'product_category', 'shop_category']
        # fields = '__all__'
        depth = 1


class ProductSerializer(serializers.ModelSerializer):


    def create(self, validated_data):
        product_meta = validated_data.pop('product_meta')
        product_meta_instance = ProductMeta.objects.get(pk=product_meta)
        return Product.objects.create(**validated_data,product_meta=product_meta_instance)

    def update(self, instance, validated_data):
        product_meta = validated_data.pop('product_meta')
        product_meta_instance = ProductMeta.objects.filter(id = product_meta).first()

        instance.product_name = validated_data.get('product_name', instance.product_name)
        instance.product_unit = validated_data.get('product_unit', instance.product_unit)
        instance.product_price = validated_data.get('product_price', instance.product_price)
        instance.product_image = validated_data.get('product_image',instance.product_image)
        instance.product_meta = product_meta_instance
        instance.save()
        return instance
    
    class Meta:
        model = Product
        fields = [ 'id','product_name', 'product_image', 'product_unit', 'product_price','product_meta']
        depth = 1
