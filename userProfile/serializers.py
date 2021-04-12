import uuid
from datetime import timedelta
from django.utils import timezone
from django_q.tasks import async_task
from httplib2 import Response
from random import randint

from coupon.models import CouponCode, CouponSettings, CouponUser
from shodai import settings
from userProfile.models import UserProfile, Address
from rest_framework import serializers

from utility.notification import email_notification


class UserProfileSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.mobile_number = validated_data.get('mobile_number', instance.mobile_number)
        instance.user_image = validated_data.get('user_image', instance.user_image)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.ref_code = validated_data.get('ref_code', instance.ref_code)
        instance.pin_code = validated_data.get('pin_code', instance.pin_code)
        instance.password = validated_data.get('password', instance.password)
        instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = UserProfile
        fields = '__all__'

    # def create(self,validated_data):
    #     user = UserProfile.objects.create(
    #     user_type = validated_data['user_type'],
    #     mobile_number=validated_data['mobile_number'],
    #     first_name = validated_data['first_name'],
    #     last_name = validated_data['last_name'],
    #     email = validated_data['email']
    #     )
    #     if user:
    #         user.set_password(validated_data['password'])
    #         user.save()
    #     return user


class AddressSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user.id
        user_instance = UserProfile.objects.filter(id=user).first()
        return Address.objects.create(**validated_data, user=user_instance)

    def update(self, instance, validated_data):
        instance.road = validated_data.get('road', instance.road)
        instance.city = validated_data.get('city', instance.city)
        instance.district = validated_data.get('district', instance.district)
        instance.country = validated_data.get('country', instance.country)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.user = validated_data.get('user', instance.user)
        instance.is_approved = False
        instance.save()
        return instance

    class Meta:
        model = Address
        fields = ['id', 'road', 'city', 'district', 'country', 'zip_code', 'user_id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        if not validated_data:
            return Response({'Error': "Invalid Data"})
        user = UserProfile.objects.create(
            user_type=validated_data['user_type'],
            mobile_number=validated_data['mobile_number'],
            first_name=validated_data['first_name'],
            last_name="",
            email=validated_data['email'],
            username=validated_data['mobile_number'],
            verification_code=randint(100000, 999999),
            code_valid_till=timezone.now() + timedelta(minutes=5)
        )
        if user:
            user.set_password(validated_data['password'])
            user.save()

            referral_discount_settings = CouponSettings.objects.get(coupon_type='RC')
            if referral_discount_settings.is_active:
                coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
                                                   name="Referral Coupon",
                                                   discount_percent=referral_discount_settings.discount_percent,
                                                   discount_amount=referral_discount_settings.discount_amount,
                                                   max_usage_count=referral_discount_settings.max_usage_count,
                                                   minimum_purchase_limit=referral_discount_settings.minimum_purchase_limit,
                                                   discount_amount_limit=referral_discount_settings.discount_amount_limit,
                                                   expiry_date=timezone.now() + timedelta(
                                                       days=referral_discount_settings.validity_period),
                                                   discount_type=referral_discount_settings.discount_type,
                                                   coupon_code_type='RC',
                                                   created_by=user)
                if not settings.DEBUG:
                    async_task('coupon.tasks.send_coupon_sms',
                               coupon,
                               user.mobile_number)
                async_task('coupon.tasks.send_coupon_email',
                           coupon,
                           user)

            gift_discount_settings = CouponSettings.objects.get(coupon_type='GC1')
            if gift_discount_settings.is_active:
                gift_coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
                                                        name="Sign Up Coupon",
                                                        discount_percent=gift_discount_settings.discount_percent,
                                                        discount_amount=gift_discount_settings.discount_amount,
                                                        max_usage_count=gift_discount_settings.max_usage_count,
                                                        minimum_purchase_limit=gift_discount_settings.minimum_purchase_limit,
                                                        discount_amount_limit=gift_discount_settings.discount_amount_limit,
                                                        expiry_date=timezone.now() + timedelta(
                                                            days=gift_discount_settings.validity_period),
                                                        discount_type=gift_discount_settings.discount_type,
                                                        coupon_code_type='GC1',
                                                        created_by=user)
                CouponUser.objects.create(coupon_code=gift_coupon,
                                          created_for=user,
                                          remaining_usage_count=1,
                                          created_by=user)
                if not settings.DEBUG:
                    async_task('coupon.tasks.send_coupon_sms',
                               gift_coupon,
                               user.mobile_number)
                async_task('coupon.tasks.send_coupon_email',
                           gift_coupon,
                           user)

            if user.user_type == 'PD':
                sub = "Approval Request"
                body = f"Dear Concern,\r\n User phone number :{user.mobile_number} \r\nUser type: {user.user_type} \r\nis requesting your approval.\r\n \r\nThanks and Regards\r\nShodai"
                email_notification(sub, body)
        return user

    class Meta:
        model = UserProfile
        fields = ('user_type', 'mobile_number', 'first_name', 'last_name',
                  'email', 'password')


class RetailerRegistrationSreializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        if not validated_data:
            return Response({'Error': "Invalid Data"})
        user = UserProfile.objects.create(
            user_type=validated_data['user_type'],
            mobile_number=validated_data['mobile_number'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            user_NID=validated_data['user_NID'],
            username=validated_data['mobile_number']
        )
        if user:
            user.set_password(validated_data['password'])
            user.save()
        return user

    class Meta:
        model = UserProfile
        fields = ('id', 'user_type', 'mobile_number', 'first_name', 'last_name', 'email', 'user_NID', 'password')
