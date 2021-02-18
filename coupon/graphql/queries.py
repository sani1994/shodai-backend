import graphene
from django.utils import timezone
from graphene_django import DjangoObjectType

from bases.views import checkAuthentication
from ..models import CouponCode, CouponUser


class CouponType(DjangoObjectType):
    class Meta:
        model = CouponCode


class Query(graphene.ObjectType):
    coupon_list = graphene.List(CouponType)

    def resolve_coupon_list(self, info):
        user = info.context.user
        if checkAuthentication(user, info):
            all_coupons = CouponCode.objects.filter(coupon_code_type='DC',
                                                    expiry_date__gte=timezone.now(),
                                                    discount_code__in=CouponUser.objects.filter(
                                                        remaining_usage_count__gt=0,
                                                        created_for=user))
            return all_coupons
