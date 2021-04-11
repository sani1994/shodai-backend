import graphene
from django.db.models import Q
from django.utils import timezone

from bases.views import checkAuthentication, coupon_checker
from coupon.models import CouponCode, CouponUser


class ProductListInput(graphene.InputObjectType):
    product_id = graphene.String(required=True)
    order_product_qty = graphene.Float(required=True)


class CouponInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    products = graphene.List(ProductListInput)


class ApplyCoupon(graphene.Mutation):
    class Arguments:
        input = CouponInput(required=True)

    msg = graphene.String()
    discount_amount = graphene.Float()
    coupon_code = graphene.String()
    status = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if checkAuthentication(user, info):
            discount_amount, coupon, _, is_under_limit = coupon_checker(input.code, input.products, user, True)
            if not is_under_limit:
                if discount_amount:
                    return ApplyCoupon(status=True,
                                       msg="Code applied successfully.",
                                       discount_amount=discount_amount,
                                       coupon_code=coupon.coupon_code)
                elif discount_amount == 0:
                    msg = "Coupon Discount Is Not Applicable On Products With Offer"
                    return ApplyCoupon(status=False, msg=msg)
                return ApplyCoupon(status=False, msg="Invalid Code!")
            else:
                msg = "Total Price Must Be {} Or More".format(coupon.minimum_purchase_limit)
                return ApplyCoupon(status=False, msg=msg)


class CouponCount(graphene.Mutation):
    status = graphene.Boolean()
    count = graphene.Int()

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if checkAuthentication(user, info):
            count = CouponCode.objects.filter(Q(coupon_code_type='DC') |
                                              Q(coupon_code_type='GC1') | Q(coupon_code_type='GC2'),
                                              expiry_date__gte=timezone.now(),
                                              max_usage_count__gt=0,
                                              discount_code__in=CouponUser.objects.filter(
                                                  created_for=user)).count()
            if count:
                return CouponCount(status=True,
                                   count=count)
            else:
                return CouponCount(status=False,
                                   count=0)


class Mutation(graphene.ObjectType):
    apply_coupon = ApplyCoupon.Field()
    coupon_count = CouponCount.Field()
