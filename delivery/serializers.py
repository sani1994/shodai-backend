from rest_framework import serializers

from delivery.models import DeliveryCheckList, DeliveryCheckListItem, DeliveryCheckListTemplate


class DeliveryCheckListSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = DeliveryCheckList.objects.create(**validated_data,assigned_user=user)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.produecer_bulk_request = validated_data.pop('produecer_bulk_request')
        instance.retailer_accept_order = validated_data.pop('retailer_accept_order')
        instance.name = validated_data.get('name', instance.name)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = DeliveryCheckList
        fields = '__all__'


class DeliveryCheckListItemSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = DeliveryCheckListItem.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.product = validated_data.pop('product')
        instance.handed_over_to = validated_data.pop('handed_over_to')
        instance.delivery_check_list = validated_data.pop('delivery_check_list')
        instance.name = validated_data.get('name', instance.name)
        instance.is_checked = validated_data.get('is_checked', instance.is_checked)
        instance.image = validated_data.get('image', instance.image)
        instance.is_approved = validated_data.get('is_approved', instance.is_approved)
        instance.first_level_qty = validated_data.get('first_level_qty', instance.first_level_qty)
        instance.second_level_qty = validated_data.get('second_level_qty', instance.second_level_qty)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = DeliveryCheckListItem
        fields = '__all__'


class DeliveryCheckListTemplateSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = DeliveryCheckListTemplate.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.delivery_check_list = validated_data.pop('delivery_check_list')
        instance.product = validated_data.pop('product')
        instance.name = validated_data.get('name', instance.name)
        instance.is_checked = validated_data.get('is_checked', instance.is_checked)
        instance.image = validated_data.get('image', instance.image)
        instance.is_approved = validated_data.get('is_approved', instance.is_approved)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = DeliveryCheckListTemplate
        fields = '__all__'

