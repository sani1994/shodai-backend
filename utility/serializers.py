from rest_framework import serializers
from utility.models import Area, CityCountry, ProductUnit, Remarks, Location


class AreaSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = Area.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.area_name = validated_data.get('area_name',instance.area_name)
        instance.polygon = validated_data.get('polygon',instance.polygon)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = Area
        fields = '__all__'

class CityCountrySerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = CityCountry.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.tire_city = validated_data.get('tire_city',instance.tire_city)
        instance.tire_country = validated_data.get('tire_country',instance.tire_country)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = CityCountry
        fields = '__all__'


class LocationSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = Location.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.geo_loc = validated_data.get('geo_loc',instance.geo_loc)
        instance.loc_name = validated_data.get('loc_name',instance.loc_name)
        instance.city_country = validated_data.get('city_country', instance.city_country)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = Location
        fields='__all__'


class ProductUnitSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = ProductUnit.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.product_unit = validated_data.get('product_unit',instance.product_unit)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = ProductUnit
        fields = ('id','product_unit')


class RemarksSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        obj = Remarks.objects.create(**validated_data)
        obj.created_by = user
        obj.save()
        return obj

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.remark = validated_data.get('remark',instance.remark)
        instance.modified_by = user
        instance.save()
        return instance

    class Meta:
        model = Remarks
        fields = '__all__'


