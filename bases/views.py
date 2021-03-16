from decouple import config
from django.utils import timezone
from graphql_relay.utils import unbase64
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from userProfile.models import BlackListedToken
from offer.models import OfferProduct
from product.models import Product
from coupon.models import CouponCode, CouponUser


def checkAuthentication(user, info):
    if user.is_anonymous:
        raise Exception('Must Log In!')
    else:
        token = info.context.headers['Authorization'].split(' ')[1]
        try:
            token = BlackListedToken.objects.get(token=token)
        except BlackListedToken.DoesNotExist:
            token = None
        if token:
            raise Exception('Invalid or expired token!')
        else:
            # checks if user mobile number verified (has frontend dependency)
            # if not user.pin_verified:
            #     raise Exception('mobile number not verified')
            return True


def field_validation(fields, data):
    if isinstance(data, dict) and all(key in data for key in fields):
        return True
    else:
        return False


def type_validation(items, typ):
    for val in items:
        if not isinstance(val, typ):
            return False
    return True


def from_global_id(global_id):
    """
    Takes the "global ID" created by toGlobalID, and returns ID
    used to create it.
    """
    unbased_global_id = unbase64(global_id)
    _type, _id = unbased_global_id.split(':', 1)
    return _id


def coupon_checker(coupon_code, products, user, is_graphql=False, is_used=False):
    coupon_is_valid = is_under_limit = False
    is_using = discount_amount = None
    total_price = sub_total = 0
    allow_offer_product = config("APPLY_DISCOUNT_ON_OFFER", cast=bool)
    today = timezone.now()

    for p in products:
        if is_graphql:
            product_id = from_global_id(p.product_id)
            product_quantity = p.order_product_qty
        else:
            product_id = p['product_id']
            product_quantity = p['product_quantity']
        product = Product.objects.filter(id=product_id, is_approved=True)
        if product:
            product = product[0]
            total = float(product.product_price) * product_quantity
            sub_total += total
            if allow_offer_product:
                total_price = sub_total
            else:
                offer_product = OfferProduct.objects.filter(product=product,
                                                            is_approved=True,
                                                            offer__is_approved=True,
                                                            offer__offer_starts_in__lte=today,
                                                            offer__offer_ends_in__gte=today)
                if not offer_product:
                    total_price += total

    if not is_used:
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
    else:
        coupon = CouponCode.objects.get(coupon_code=coupon_code)
        if sub_total >= coupon.minimum_purchase_limit:
            coupon_is_valid = True
            is_using = CouponUser.objects.get(coupon_code=coupon, created_for=user)
        else:
            is_under_limit = True

    if coupon_is_valid:
        if coupon.discount_type == 'DP':
            discount_amount = round(total_price * (coupon.discount_percent / 100))
            if discount_amount > coupon.discount_amount_limit:
                discount_amount = coupon.discount_amount_limit
        elif coupon.discount_type == 'DA':
            if total_price < coupon.discount_amount:
                discount_amount = total_price
            else:
                discount_amount = coupon.discount_amount

    return discount_amount, coupon, is_using, is_under_limit


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({'page': self.page.number,
                         'page_size': self.page.paginator.per_page,
                         'count': self.page.paginator.count,
                         'results': data})
