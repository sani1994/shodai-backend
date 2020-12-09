from userProfile.models import UserProfile
from rest_framework import serializers


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = 'username', 'first_name', 'last_name', 'mobile_number', 'user_type', 'email'
