import uuid
from datetime import timedelta

import graphene
from django.db.models import Q
from django.utils import timezone
from graphene_django import DjangoObjectType

from base.views import checkAuthentication
from ..models import CouponCode, CouponUser, CouponSettings


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


class CouponPageType(DjangoObjectType):
    class Meta:
        model = CouponCode
        fields = ['coupon_code', 'expiry_date', 'discount_percent', 'discount_amount_limit',
                  'discount_amount', 'minimum_purchase_limit', 'max_usage_count']

    discount_coupon_percent = graphene.Int()
    shared_coupon_count = graphene.Int()
    gift_coupon = graphene.Field(CouponType)

    def resolve_discount_coupon_percent(self, info):
        discount = CouponSettings.objects.get(coupon_type='DC').discount_percent
        return discount

    def resolve_shared_coupon_count(self, info):
        referral_discount = CouponSettings.objects.get(coupon_type='RC').max_usage_count
        return referral_discount - self.max_usage_count

    def resolve_gift_coupon(self, info):
        gift_coupon = CouponCode.objects.filter(coupon_code_type='GC1',
                                                expiry_date__gte=timezone.now(),
                                                created_by=self.created_by)
        return gift_coupon[0] if gift_coupon else None


class Query(graphene.ObjectType):
    coupon_list = graphene.List(CouponType)
    referral_code = graphene.Field(CouponType)
    coupon_page = graphene.Field(CouponPageType)

    def resolve_coupon_list(self, info):
        user = info.context.user
        if checkAuthentication(user, info):
            all_coupons = CouponCode.objects.filter(Q(coupon_code_type='DC') |
                                                    Q(coupon_code_type='GC1') | Q(coupon_code_type='GC2'),
                                                    discount_code__in=CouponUser.objects.filter(
                                                        created_for=user)).order_by('-created_on')
            return all_coupons

    def resolve_referral_code(self, info):
        user = info.context.user
        if checkAuthentication(user, info):
            referral_code = CouponCode.objects.filter(coupon_code_type='RC',
                                                      expiry_date__gte=timezone.now() - timedelta(days=7),
                                                      created_by=user).order_by('-created_on')
            return referral_code[0] if referral_code else None

    def resolve_coupon_page(self, info):
        user = info.context.user
        if checkAuthentication(user, info):
            referral_code = CouponCode.objects.filter(coupon_code_type='RC',
                                                      expiry_date__gte=timezone.now(),
                                                      max_usage_count__gt=0,
                                                      created_by=user).order_by('-created_on')
            if referral_code:
                return referral_code[0]
            else:
                referral_discount_settings = CouponSettings.objects.get(coupon_type='RC')
                if referral_discount_settings.is_active:
                    referral_coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
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
                    return referral_coupon
                else:
                    return None
