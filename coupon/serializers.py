from django.utils import timezone
from rest_framework import serializers

from coupon.models import CouponCode, CouponSettings


class CouponListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = CouponCode
        fields = ['coupon_code', 'expiry_date', 'discount_percent', 'discount_amount_limit',
                  'status', 'minimum_purchase_limit', 'max_usage_count']

    def get_status(self, obj):
        if obj.max_usage_count == 0:
            return "Used"
        return "Available"


class ReferralCouponSerializer(serializers.ModelSerializer):
    gift_coupon = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CouponCode
        fields = ['coupon_code', 'discount_percent', 'expiry_date', 'discount_amount_limit',
                  'minimum_purchase_limit', 'max_usage_count', 'gift_coupon']

    def get_gift_coupon(self, obj):
        gift_coupon = CouponCode.objects.filter(coupon_code_type='GC1',
                                                expiry_date__gte=timezone.now(),
                                                created_by=obj.created_by).values('coupon_code',
                                                                                  'discount_percent',
                                                                                  'expiry_date')

        return gift_coupon[0] if gift_coupon else None


class CouponPageSerializer(serializers.ModelSerializer):
    discount_coupon_percent = serializers.SerializerMethodField()
    successful_share_count = serializers.SerializerMethodField()

    class Meta:
        model = CouponCode
        fields = ['coupon_code', 'expiry_date', 'discount_percent', 'discount_amount_limit',
                  'minimum_purchase_limit', 'max_usage_count',
                  'discount_coupon_percent', 'successful_share_count']

    def get_discount_coupon_percent(self, obj):
        discount = CouponSettings.objects.get(coupon_type='DC').discount_percent
        return discount

    def get_successful_share_count(self, obj):
        referral_discount = CouponSettings.objects.get(coupon_type='RC').max_usage_count
        return referral_discount - obj.max_usage_count
