from rest_framework import serializers

from inventory.models import ShopInventory


class ShopInventorySerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = ShopInventory.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.incoming = validated_data.get('incoming',instance.incoming)
        instance.outgoing = validated_data.get('outgoing', instance.outgoing)
        instance.debit = validated_data.get('debit', instance.debit)
        instance.credit = validated_data.get('credit',instance.credit)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = ShopInventory
        fields = '__all__'
