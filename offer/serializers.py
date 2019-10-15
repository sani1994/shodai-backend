from rest_framework import serializers
from offer.models import Offer, OfferProduct

class OfferSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        # print(validated_data)
        instance.offer_name = validated_data.get('offer_name',instance.offer_name)
        instance.offer_img = validated_data.get('offer_img',instance.offer_img)
        instance.offer_details = validated_data.get('offer_details',instance.offer_details)
        # instance.modified_by = validated_data.pop('user')
        instance.save()
        return instance

    class Meta:
        model = Offer
        fields = '__all__'


class OfferProductSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        # product = self.context['product']
        # offer = self.context['offer']
        product = self.validated_data.pop('product')
        offer = self.validated_data.pop('offer')
        instance.offer_product_balance = self.validated_data.get('offer_product_balance',instance.offer_product_balance)
        instance.offer_price =  self.validated_data.get('offer_price',instance.offer_price)
        instance.product = product
        instance.offer = offer
        instance.save()
        return instance

    class Meta:
        model = OfferProduct
        fields = '__all__'



