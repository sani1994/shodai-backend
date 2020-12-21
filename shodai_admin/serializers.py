from order.models import Order
from userProfile.models import UserProfile
from rest_framework import serializers


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = 'username', 'first_name', 'last_name', 'mobile_number', 'user_type', 'email'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id", "created_on", "modified_on", "invoice_number", "delivery_date_time",
            "delivery_place", "order_total_price", "order_status", "contact_number",
            "created_by", "modified_by", "user", "address", "paid_status"
        )
