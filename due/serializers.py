from rest_framework import serializers

from due.models import UserDues


class UserDuesSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = UserDues.objects.create(**validated_data,user=user)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.shop = validated_data.pop('shop')
        instance.debit = validated_data.get('debit', instance.debit)
        instance.credit = validated_data.get('credit',instance.credit)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = UserDues
        fields = '__all__'