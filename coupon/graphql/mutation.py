import graphene
from django.utils import timezone

from bases.views import checkAuthentication, from_global_id
from offer.models import OfferProduct
from product.models import Product
from ..models import CouponCode, CouponUser


def coupon_checker(coupon_code, products, user):
    coupon_is_valid = is_under_limit = False
    is_using = discount_amount = None
    total_price_regular_product = sub_total = 0
    today = timezone.now()

    for p in products:
        product_id = from_global_id(p.product_id)
        product = Product.objects.filter(id=product_id, is_approved=True)
        if product:
            product = product[0]
            total = float(product.product_price) * p.order_product_qty
            sub_total += total
            offer_product = OfferProduct.objects.filter(product=product,
                                                        is_approved=True,
                                                        offer__is_approved=True,
                                                        offer__offer_starts_in__lte=today,
                                                        offer__offer_ends_in__gte=today)
            if not offer_product:
                total_price_regular_product += total

    coupon = CouponCode.objects.filter(coupon_code=coupon_code, expiry_date__gte=today)
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
                                                             created_on=today)
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
                                                         created_on=today)
        else:
            is_under_limit = True

        if coupon_is_valid:
            if coupon.discount_type == 'DP':
                discount_amount = round(total_price_regular_product * (coupon.discount_percent / 100))
                if discount_amount > coupon.discount_amount_limit:
                    discount_amount = coupon.discount_amount_limit
            elif coupon.discount_type == 'DA':
                if total_price_regular_product < coupon.discount_amount:
                    discount_amount = total_price_regular_product
                else:
                    discount_amount = coupon.discount_amount

    return discount_amount, coupon, is_using, is_under_limit


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
            discount_amount, coupon, _, is_under_limit = coupon_checker(input.code, input.products, user)
            if not is_under_limit:
                if discount_amount is not None:
                    return ApplyCoupon(status=True,
                                       msg="Code applied successfully.",
                                       discount_amount=discount_amount,
                                       coupon_code=coupon.coupon_code)
                return ApplyCoupon(status=False, msg="Invalid Code!")
            else:
                msg = "Total Price Must Be {} Or More".format(coupon.minimum_purchase_limit)
                return ApplyCoupon(status=False, msg=msg)


class Mutation(graphene.ObjectType):
    apply_coupon = ApplyCoupon.Field()
