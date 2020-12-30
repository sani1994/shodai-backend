from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import HyperlinkedIdentityField

from offer.models import OfferProduct
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
    today = timezone.now()
    offer_price = serializers.SerializerMethodField()
    offer_name = serializers.SerializerMethodField()

    def get_offer_price(self, obj):
        offer_product = OfferProduct.objects.filter(product=obj,
                                                    is_approved=True,
                                                    offer__is_approved=True,
                                                    offer__offer_starts_in__lte=self.today,
                                                    offer__offer_ends_in__gte=self.today)
        if offer_product:
            return offer_product[0].offer_price
        else:
            return None

    def get_offer_name(self, obj):
        offer_product = OfferProduct.objects.filter(product=obj,
                                                    is_approved=True,
                                                    offer__is_approved=True,
                                                    offer__offer_starts_in__lte=self.today,
                                                    offer__offer_ends_in__gte=self.today)
        if offer_product:
            return offer_product[0].offer.offer_name
        else:
            return None

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_name_bn',
                  'product_image', 'product_unit', 'product_unit_name',
                  'product_price', 'product_meta', 'product_last_price',
                  'is_approved', 'product_description', 'product_description_bn',
                  'price_with_vat', 'offer_price', 'offer_name']
        read_only_fields = ['product_last_price', 'offer_price', 'offer_name']


##########
class RetailerProductSerializer(serializers.ModelSerializer):
    """Serializer for the Retailer Product Inventory"""

    # product_unit = ProductUnitSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'product_name', 'product_name_bn',
                  'product_description', 'product_description_bn',
                  'price_with_vat')


class ProductForCartSerializer(serializers.ModelSerializer):
    today = timezone.now()
    product_quantity = serializers.FloatField(default=1.0)
    product_unit = serializers.StringRelatedField()
    offer_price = serializers.SerializerMethodField()
    offer_name = serializers.SerializerMethodField()

    def get_offer_price(self, obj):
        offer_product = OfferProduct.objects.filter(product=obj,
                                                    is_approved=True,
                                                    offer__is_approved=True,
                                                    offer__offer_starts_in__lte=self.today,
                                                    offer__offer_ends_in__gte=self.today)
        if offer_product:
            return offer_product[0].offer_price
        else:
            return None

    def get_offer_name(self, obj):
        offer_product = OfferProduct.objects.filter(product=obj,
                                                    is_approved=True,
                                                    offer__is_approved=True,
                                                    offer__offer_starts_in__lte=self.today,
                                                    offer__offer_ends_in__gte=self.today)
        if offer_product:
            return offer_product[0].offer.offer_name
        else:
            return None

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_description', 'product_price',
                  'product_image', 'product_unit', 'product_quantity', 'product_last_price',
                  'product_name_bn', 'product_description_bn', 'price_with_vat',
                  "offer_name", "offer_price"]
