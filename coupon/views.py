from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bases.views import field_validation, coupon_checker, type_validation
from coupon.models import CouponUser, CouponCode
from coupon.serializers import CouponListSerializer
from product.models import Product
from shodai.utils.permission import GenericAuth


class VerifyCoupon(APIView):
    permission_classes = [GenericAuth]

    def post(self, request):
        data = request.data
        user = request.user
        required_fields = ['coupon_code',
                           'products']
        is_valid = field_validation(required_fields, data)
        products = data['products']

        if is_valid and isinstance(products, list) and products:
            required_fields = ['product_id', 'product_quantity']
            product_list = []
            for item in products:
                is_valid = field_validation(required_fields, item)
                if is_valid:
                    integer_fields = [item['product_id'],
                                      item['product_quantity']]
                    is_valid = type_validation(integer_fields, int)
                if is_valid and item['product_id']:
                    if item['product_id'] not in product_list:
                        product_list.append(item['product_id'])
                        product_exist = Product.objects.filter(id=item['product_id'], is_approved=True)
                        if not product_exist or not item['product_quantity']:
                            is_valid = False
                    else:
                        is_valid = False
                else:
                    is_valid = False
                if not is_valid:
                    break
        else:
            is_valid = False

        if not is_valid or not isinstance(data['coupon_code'], str) or not data['coupon_code']:
            return Response({
                "status": "failed",
                "message": "Invalid request!"}, status=status.HTTP_400_BAD_REQUEST)

        discount_amount, coupon, _, is_under_limit = coupon_checker(data['coupon_code'], products, user)
        if not is_under_limit:
            if discount_amount:
                return Response({'status': 'success',
                                 "discount_amount": discount_amount,
                                 "coupon_code": coupon.coupon_code}, status=status.HTTP_200_OK)
            elif discount_amount == 0:
                msg = "Discount is not applicable on products with offer."
                return Response({'status': 'failed',
                                 'message': msg}, status=status.HTTP_200_OK)
            return Response({'status': 'failed',
                             'message': "Invalid coupon!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            msg = "Total price must be {} or more.".format(coupon.minimum_purchase_limit)
            return Response({'status': 'failed',
                             'message': msg}, status=status.HTTP_200_OK)


class CouponList(APIView):
    permission_class = [GenericAuth]

    def get(self, request):
        queryset = CouponCode.objects.filter(Q(coupon_code_type='DC') |
                                             Q(coupon_code_type='GC1') | Q(coupon_code_type='GC2'),
                                             expiry_date__gte=timezone.now(),
                                             discount_code__in=CouponUser.objects.filter(
                                                 created_for=request.user))

        serializer = CouponListSerializer(queryset, many=True)
        if serializer:
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReferralCoupon(APIView):
    permission_class = [GenericAuth]

    def get(self, request):
        queryset = CouponCode.objects.filter(coupon_code_type='RC',
                                             expiry_date__gte=timezone.now() - timedelta(days=7),
                                             created_by=request.user)

        if queryset:
            serializer = CouponListSerializer(queryset[0])
            if serializer:
                return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "failed", 'data': {
            "coupon_code": "",
            "expiry_date": "",
            "discount_percent": "",
            "discount_amount_limit": "",
            "status": "",
            "minimum_purchase_limit": "",
            "max_usage_count": ""
        }}, status=status.HTTP_200_OK)


class ReferralCouponOne(APIView):
    permission_class = [GenericAuth]

    def get(self, request):
        queryset = CouponCode.objects.filter(coupon_code_type='RC',
                                             expiry_date__gte=timezone.now() - timedelta(days=7),
                                             created_by=request.user)
        if queryset:
            serializer = CouponListSerializer(queryset[0])
            if serializer and not request.user.is_customer:
                request.user.is_customer = True
                request.user.save()
                return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "failed", 'data': {
            "coupon_code": "",
            "expiry_date": "",
            "discount_percent": "",
            "discount_amount_limit": "",
            "status": "",
            "minimum_purchase_limit": "",
            "max_usage_count": ""
        }}, status=status.HTTP_200_OK)
