from rest_framework import serializers

from coupon.models import CouponCode


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
