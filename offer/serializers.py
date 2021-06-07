from rest_framework import serializers
from offer.models import Offer, OfferProduct
from product.models import Product
from utility.models import Banner


class OfferSerializer(serializers.ModelSerializer):
    offer_img = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Offer
        fields = '__all__'

    def get_offer_img(self, obj):
        banner = Banner.objects.filter(offer=obj, is_approved=True).first()
        return banner.banner_img.url if banner else None


class OfferProductSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        product = self.validated_data.pop('product')
        offer = self.validated_data.pop('offer')
        instance.offer_product_balance = self.validated_data.get('offer_product_balance',
                                                                 instance.offer_product_balance)
        instance.offer_price = self.validated_data.get('offer_price', instance.offer_price)
        instance.product = product
        instance.offer = offer
        instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = OfferProduct
        fields = '__all__'


class OfferProductReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferProduct
        fields = ('id', 'offer_price', 'offer_product_balance', 'offer', 'product')
        depth = 1


class ProductReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'product_name', 'product_name_bn', 'product_image',
                  'product_unit_name', 'product_price', 'product_meta_name',
                  'product_last_price', 'is_approved',
                  'product_description', 'product_description_bn',
                  'price_with_vat',)


class OfferProductListSerializer(serializers.ModelSerializer):
    offer_name = serializers.StringRelatedField(source='offer')
    product = ProductReadSerializer(read_only=True)
    offer_price_with_vat = serializers.SerializerMethodField()

    def get_offer_price_with_vat(self, obj):
        return round(float(obj.offer_price) +
                     (float(obj.offer_price) * obj.product.product_meta.vat_amount) / 100)

    class Meta:
        model = OfferProduct
        fields = ('id', 'offer_price', 'offer_price_with_vat', 'offer_name', 'product')
