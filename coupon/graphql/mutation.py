import graphene
from django.utils import timezone

from bases.views import checkAuthentication, from_global_id
from offer.models import OfferProduct
from product.models import Product
from ..models import CouponCode, CouponUser


def coupon_checker(coupon_code, user, products):
    coupon_is_valid = False
    is_using = None
    total_price_regular_product = sub_total = 0
    for p in products:
        product_id = from_global_id(p.product_id)
        product = Product.objects.get(id=product_id)
        total = float(product.product_price) * p.order_product_qty
        sub_total += total
        today = timezone.now()
        offer_product = OfferProduct.objects.filter(product=product,
                                                    is_approved=True,
                                                    offer__is_approved=True,
                                                    offer__offer_starts_in__lte=today,
                                                    offer__offer_ends_in__gte=today)
        if not offer_product:
            total_price_regular_product += total
    coupon = CouponCode.objects.filter(coupon_code=coupon_code, expiry_date__gte=timezone.now())
    if coupon:
        coupon = coupon[0]
        if sub_total >= coupon.minimum_purchase_limit:
            coupon_type = coupon.coupon_code_type
            if coupon_type == 'RC':
                if coupon.created_by != user:
                    is_using = CouponUser.objects.filter(coupon_code=coupon, created_for=user)
                    if is_using:
                        is_using = is_using[0]
                        if is_using.remaining_usage_count > 0 and coupon.max_usage_count > 0:
                            coupon_is_valid = True
                    elif coupon.max_usage_count > 0:
                        coupon_is_valid = True
                        is_using = CouponUser.objects.create(coupon_code=coupon,
                                                             created_for=user,
                                                             remaining_usage_count=1,
                                                             created_by=user,
                                                             created_on=timezone.now())
            elif coupon_type == 'DC':
                is_using = CouponUser.objects.filter(coupon_code=coupon, created_for=user,
                                                     remaining_usage_count__gt=0)
                if is_using:
                    is_using = is_using[0]
                    coupon_is_valid = True
            elif coupon_type == 'PC':
                is_using = CouponUser.objects.filter(coupon_code=coupon, created_for=user)
                if is_using:
                    is_using = is_using[0]
                    if is_using.remaining_usage_count > 0:
                        coupon_is_valid = True
                else:
                    coupon_is_valid = True
                    is_using = CouponUser.objects.create(coupon_code=coupon,
                                                         created_for=user,
                                                         remaining_usage_count=1,
                                                         created_by=user,
                                                         created_on=timezone.now())

    return coupon_is_valid, coupon, is_using, total_price_regular_product


class ProductIdInput(graphene.InputObjectType):
    product_id = graphene.String(required=True)
    order_product_qty = graphene.Float(required=True)


class CouponInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    total_price = graphene.Float(required=True)
    products = graphene.List(ProductIdInput)


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
            coupon_is_valid, coupon, _, total_price = coupon_checker(input.code, user, input.products)
            if input.total_price >= coupon.minimum_purchase_limit:
                if coupon_is_valid:
                    if coupon.discount_type == 'DP':
                        discount_amount = round(total_price * (coupon.discount_percent / 100))
                        if discount_amount > coupon.discount_amount_limit:
                            discount_amount = coupon.discount_amount_limit
                    elif coupon.discount_type == 'DA':
                        discount_amount = coupon.discount_amount
                    return ApplyCoupon(msg="Code applied successfully.",
                                       discount_amount=discount_amount,
                                       coupon_code=coupon.coupon_code)
                return ApplyCoupon(msg="Invalid Code!")
            else:
                msg = "Total Price Must Be {} Or More" .format(str(coupon.minimum_purchase_limit))
                return ApplyCoupon(msg=msg)


class Mutation(graphene.ObjectType):
    apply_coupon = ApplyCoupon.Field()
