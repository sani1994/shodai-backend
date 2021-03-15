import graphene

from bases.views import checkAuthentication, coupon_checker


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
            discount_amount, coupon, _, is_under_limit = coupon_checker(input.code, input.products, user, False)
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


class Mutation(graphene.ObjectType):
    apply_coupon = ApplyCoupon.Field()
