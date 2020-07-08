from .models import CustomerQuery
from rest_framework import serializers


class CustomerQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerQuery
        fields = '__all__'
