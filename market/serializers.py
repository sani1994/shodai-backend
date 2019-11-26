from rest_framework import serializers

from market.models import WholeSellRate, KitchenMarket, CommissionRate


class WholeSellRateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = WholeSellRate.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.product = validated_data.pop('product')
        instance.unit = validated_data.pop('unit')
        instance.location = validated_data.pop('location')
        instance.producer_price = validated_data.get('producer_price',instance.producer_price)
        instance.qty = validated_data.get('qty',instance.qty)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = WholeSellRate
        fields = '__all__'


class KitchenMarketSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = KitchenMarket.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.product = validated_data.pop('product')
        instance.unit = validated_data.pop('unit')
        instance.location = validated_data.pop('location')
        instance.polygon = validated_data.pop('polygon')
        instance.whole_sell_price = validated_data.get('whole_sell_price',instance.whole_sell_price)
        instance.whole_sell_qty = validated_data.get('whole_sell_qty',instance.whole_sell_qty)
        instance.qty = validated_data.get('qty', instance.qty)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = KitchenMarket
        fields = '__all__'


class CommissionRateSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = CommissionRate.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.product = validated_data.pop('product')
        instance.percentage = validated_data.get('percentage',instance.percentage)
        instance.polygon = validated_data.pop('polygon')
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model=CommissionRate
        fields='__all__'
