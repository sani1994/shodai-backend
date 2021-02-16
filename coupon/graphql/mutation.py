import graphene
from django.utils import timezone

from bases.views import checkAuthentication
from ..models import CouponCode, CouponUser


class CouponInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    total_price = graphene.Float(required=True)


class ApplyCoupon(graphene.Mutation):
    class Arguments:
        input = CouponInput(required=True)

    msg = graphene.String()
    discount_amount = graphene.Float()
    coupon_code = graphene.String()

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if checkAuthentication(user, info):
            coupon = CouponCode.objects.filter(coupon_code=input.code, expiry_date__gte=timezone.now())
            if coupon:
                coupon = coupon[0]
                coupon_type = coupon.coupon_code_type
                coupon_is_valid = False
                if coupon_type == 'RC':
                    is_using = CouponUser.objects.filter(coupon_code=coupon, created_for=user)
                    if is_using:
                        if is_using[0].remaining_usage_count > 0 and coupon.max_usage_count > 0:
                            coupon_is_valid = True
                    elif coupon.max_usage_count > 0:
                        coupon_is_valid = True
                        CouponUser.objects.create(coupon_code=coupon,
                                                  created_for=user,
                                                  remaining_usage_count=1)
                elif coupon_type == 'DC':
                    is_using = CouponUser.objects.filter(coupon_code=coupon, created_for=user,
                                                         remaining_usage_count__gt=0)
                    if is_using:
                        coupon_is_valid = True
                elif coupon_type == 'PC':
                    is_using = CouponUser.objects.filter(coupon_code=coupon, created_for=user)
                    if is_using:
                        if is_using[0].remaining_usage_count > 0:
                            coupon_is_valid = True
                    else:
                        coupon_is_valid = True
                        CouponUser.objects.create(coupon_code=coupon,
                                                  created_for=user,
                                                  remaining_usage_count=1)
                if coupon_is_valid:
                    discount_type = coupon.discount_type
                    if discount_type == 'DP':
                        discount_amount = round(input.total_price * (coupon.discount_percent / 100))
                        if discount_amount > coupon.discount_amount_limit:
                            discount_amount = coupon.discount_amount_limit
                    elif discount_type == 'DA':
                        discount_amount = coupon.discount_amount
                    return ApplyCoupon(msg="Code applied successfully.",
                                       discount_amount=discount_amount,
                                       coupon_code=coupon.coupon_code)

            return ApplyCoupon(msg="Invalid Code!")


class Mutation(graphene.ObjectType):
    apply_coupon = ApplyCoupon.Field()
