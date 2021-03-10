from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bases.views import field_validation, coupon_checker, type_validation
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
            for item in products:
                is_valid = field_validation(required_fields, item)
                if is_valid:
                    integer_fields = [item['product_id'],
                                      item['product_quantity']]
                    is_valid = type_validation(integer_fields, int)
                if is_valid and item['product_id']:
                    product_exist = Product.objects.filter(id=item['product_id'], is_approved=True)
                    if not product_exist or not item['product_quantity']:
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

        discount_amount, coupon, _, is_under_limit = coupon_checker(data['coupon_code'], products, user, True)
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
