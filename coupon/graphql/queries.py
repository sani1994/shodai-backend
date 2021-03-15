from datetime import timedelta

import graphene
from django.utils import timezone
from graphene_django import DjangoObjectType

from bases.views import checkAuthentication
from ..models import CouponCode, CouponUser


class CouponType(DjangoObjectType):
    class Meta:
        model = CouponCode
        fields = ['coupon_code', 'expiry_date', 'discount_percent', 'discount_amount_limit',
                  'discount_amount', 'minimum_purchase_limit', 'max_usage_count']

    coupon_status = graphene.String()

    def resolve_coupon_status(self, info):
        if self.expiry_date < timezone.now():
            return "Expired"
        elif self.max_usage_count == 0:
            return "Used"
        return "Available"


class Query(graphene.ObjectType):
    coupon_list = graphene.List(CouponType)
    referral_code = graphene.Field(CouponType)

    def resolve_coupon_list(self, info):
        user = info.context.user
        if checkAuthentication(user, info):
            all_coupons = CouponCode.objects.filter(coupon_code_type='DC',
                                                    discount_code__in=CouponUser.objects.filter(
                                                        created_for=user))
            return all_coupons

    def resolve_referral_code(self, info):
        user = info.context.user
        if checkAuthentication(user, info):
            referral_code = CouponCode.objects.filter(coupon_code_type='RC',
                                                      expiry_date__gte=timezone.now() - timedelta(days=7),
                                                      created_by=user)
            return referral_code[0] if referral_code else None
