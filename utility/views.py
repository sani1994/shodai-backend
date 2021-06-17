import math
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from base.views import field_validation, coupon_checker
from product.models import Product
from shodai.permissions import GenericAuth, ServiceAPIAuth
from order.models import Order, OrderProduct, InvoiceInfo, DiscountInfo
from shodai_admin.views import all_order_status
from utility.models import Area, ProductUnit, Remarks
from utility.serializers import AreaSerializer, ProductUnitSerializer, RemarksSerializer

# Create your views here.

order_status_all = {
    'OD': 'Ordered',
    'OA': 'Order Accepted',
    'RE': 'Order Ready',
    'OAD': 'Order at Delivery',
    'COM': 'Order Completed',
    'CN': 'Order Cancelled',
}


class AreaList(APIView):  # get area list and create area
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = Area.objects.all()
        serializer = AreaSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = AreaSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AreaDetails(APIView):  # area object get, update and delete
    permission_classes = [GenericAuth]

    def get_area_obj(self, id):
        return get_object_or_404(Area, id=id)

    def get(self, request, id):
        obj = self.get_area_obj(id)
        serializer = AreaSerializer(obj)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        obj = self.get_area_obj(id)
        serializer = AreaSerializer(obj, data=request.data, context={'request', request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if request.user.is_staff:
            obj = self.get_area_obj(id)
            obj.delete()
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductUnitList(APIView):  # product unit list get and create
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = ProductUnit.objects.all()

        serializer = ProductUnitSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.user.is_staff:
            if not ProductUnit.objects.filter(ProductUnit_Item__contains=request.data):
                serializer = ProductUnitSerializer(data=request.data)
                if serializer.is_valid():
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)
        return Response({'Duplicat data: ' + str(request.data['product_unit'])}, status=status.HTTP_400_BAD_REQUEST)


class ProductUnitDetails(APIView):  # product unit object get, update and delete
    permission_classes = [GenericAuth]

    def get_productunit_obj(self, id):
        obj = get_object_or_404(ProductUnit, id=id)
        return obj

    def get(self, request, id):
        if request.user.is_staff:
            obj = self.get_productunit_obj(id)
            serializer = ProductUnitSerializer(obj)
            if serializer:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, id):
        if request.user.is_staff:
            obj = self.get_productunit_obj(id)
            serializer = ProductUnitSerializer(obj, data=request.data)
            if serializer:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        if request.user.is_staff:
            obj = self.get_productunit_obj(id)
            if obj:
                obj.delete()
            return Response({
                "Status": "No content",
                "details": "Content not available"
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class RemarksList(APIView):  # get remarks list and create area

    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = Remarks.objects.all()
        serializer = RemarksSerializer(queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = RemarksSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemarksDetails(APIView):  # remarks unit object get, update and delete
    permission_classes = [GenericAuth]

    def get_remarks_obj(self, id):
        return get_object_or_404(Remarks, id=id)

    def get(self, request, id):
        obj = self.get_remarks_obj(id)
        serializer = RemarksSerializer(obj)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        obj = self.get_remarks_obj(id)
        serializer = RemarksSerializer(obj, data=request.data, context={'request', request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if request.user.is_staff:
            obj = self.get_remarks_obj(id)
            obj.delete()
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class OrderData(APIView):
    permission_classes = [ServiceAPIAuth]

    def get(self, request):
        order_number = request.query_params.get('data')

        is_valid = True
        if not order_number:
            is_valid = False
        if is_valid:
            order = Order.objects.filter(order_number=order_number)
            if not order:
                is_valid = False
        if is_valid:
            invoice = InvoiceInfo.objects.filter(invoice_number=order[0].invoice_number)
            if not invoice:
                is_valid = False

        if not is_valid:
            return Response({
                "status": "failed",
                "message": "Invalid request!"
            }, status=status.HTTP_400_BAD_REQUEST)

        order = order[0]
        invoice = invoice[0]
        order_data = {
            "order_number": order.order_number,
            "order_status": order_status_all[order.order_status],
            "placed_on": str(order.placed_on + timedelta(hours=6))[:16],
            "total_price": order.order_total_price,
            "delivery_charge": invoice.delivery_charge,
            "discount": invoice.discount_amount,
            "payment_status": "Paid" if invoice.paid_status else "Not Paid",
            "payment_method": "Cash on Delivery" if invoice.payment_method == 'CASH_ON_DELIVERY' else "Online Payment",
            "customer": {
                "name": order.user.first_name,
                "mobile_number": order.user.mobile_number,
                "email": order.user.email
            },
            "delivery_date_time": str(order.delivery_date_time + timedelta(hours=6))[:16],
            "delivery_address": invoice.delivery_address,
            "delivery_contact_number": order.contact_number,
            "ordered_products": []
        }
        order_products = OrderProduct.objects.filter(order=order)
        for product in order_products:
            product_data = {
                "product_id": product.id,
                "product_price": product.product_price,
                "product_quantity": product.order_product_qty,
                "product_name": product.product.product_name,
                "product_unit": product.product.product_unit.product_unit
            }
            order_data['ordered_products'].append(product_data)
        return Response({
            "status": "success",
            "data": order_data,
        }, status=status.HTTP_200_OK)


class OrderStatusUpdate(APIView):
    permission_classes = [ServiceAPIAuth]

    def patch(self, request):
        data = request.data

        order_number = data.get('order_number')
        if order_number:
            order = Order.objects.filter(order_number=order_number)
            if order:
                order = order[0]
                if order.order_status != 'COM' and order.order_status != 'CN':
                    order.order_status = 'COM'
                    order.save()
                    return Response({
                        "status": "success",
                        "message": 'Order status updated.'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "status": "failed",
                        "message": 'Order status update failed.'
                    }, status=status.HTTP_200_OK)
        return Response({
            "status": "failed",
            "message": "Invalid request!"
        }, status=status.HTTP_400_BAD_REQUEST)


class OrderUpdate(APIView):
    permission_classes = [ServiceAPIAuth]

    def patch(self, request):
        data = request.data
        order_number = request.query_params.get('order_number')
        required_fields = ['order_status',
                           'products']
        is_valid = field_validation(required_fields, data)
        if order_number:
            products = data['products']
            order = Order.objects.filter(order_number=order_number).first()
            if is_valid and order:
                all_order_products = OrderProduct.objects.filter(order=order)
                order_products = []
                order_product_list = []
                for item in all_order_products:
                    product_data = {'product_id': item.product.id,
                                    'product_quantity': item.order_product_qty}
                    order_product_list.append(item.product.id)
                    order_products.append(product_data)
            else:
                is_valid = False

            if is_valid and isinstance(products, list) and products:
                required_fields = ['product_id', 'product_quantity']

                product_list = []
                for item in products:
                    is_valid = field_validation(required_fields, item)
                    if is_valid and isinstance(item['product_id'], int):
                        if item['product_id'] not in product_list:
                            product_list.append(item['product_id'])
                            if item['product_id'] in order_product_list:
                                product_exist = Product.objects.filter(id=item['product_id'])
                            else:
                                product_exist = Product.objects.filter(id=item['product_id'], is_approved=True)
                            if not product_exist:
                                is_valid = False
                            if is_valid:
                                decimal_allowed = product_exist[0].decimal_allowed
                                if not decimal_allowed and not isinstance(item['product_quantity'], int) and \
                                        not item['product_quantity'] > 0:
                                    is_valid = False
                                elif decimal_allowed and not isinstance(item['product_quantity'], (float, int)) and \
                                        not item['product_quantity'] > 0:
                                    is_valid = False
                            if is_valid and decimal_allowed:
                                item['product_quantity'] = math.floor(item['product_quantity'] * 10 ** 3) / 10 ** 3
                        else:
                            is_valid = False
                    else:
                        is_valid = False
                    if not is_valid:
                        break
            else:
                is_valid = False
        else:
            is_valid = False

        if not is_valid or not isinstance(data['order_status'], str) or \
                order.order_status == 'COM' or order.order_status == 'CN' or \
                data['order_status'] not in ['Order Accepted', 'Order Completed', 'Order Cancelled']:
            return Response({
                "status": "failed",
                "message": "Invalid request!"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            products_updated = True
            if data['order_status'] == 'Order Completed' or data['order_status'] == 'Order Cancelled':
                products_updated = False

            if products_updated and len(order_products) == len(products):
                for i in products:
                    if i not in order_products:
                        break
                else:
                    products_updated = False

            if products_updated:
                invoice = InvoiceInfo.objects.filter(invoice_number=order.invoice_number).first()
                delivery_charge = invoice.delivery_charge
                coupon_discount_amount = additional_discount = 0

                is_coupon_discount = DiscountInfo.objects.filter(discount_type='CP', invoice=invoice).first()
                is_additional_discount = DiscountInfo.objects.filter(discount_type='AD', invoice=invoice).first()

                if is_additional_discount:
                    additional_discount = is_additional_discount.discount_amount

                if "-" in order.order_number:
                    x = order.order_number.split("-")
                    x[1] = int(x[1]) + 1
                    order_number = x[0] + "-" + str(x[1])
                else:
                    order_number = order.order_number + "-1"

                is_used = Order.objects.filter(order_number=order_number).count()
                if is_used:
                    return Response({
                        "status": "failed",
                        "message": "Invalid request!"
                    }, status=status.HTTP_400_BAD_REQUEST)

                existing_order = order.id
                order.order_status = 'CN'
                order.save()

                order = Order.objects.create(user=order.user,
                                             placed_on=order.placed_on,
                                             platform=order.platform,
                                             order_number=order_number,
                                             delivery_date_time=order.delivery_date_time,
                                             delivery_place=order.delivery_place,
                                             delivery_zone=order.delivery_zone,
                                             lat=order.lat,
                                             long=order.long,
                                             order_status="OA",
                                             address=order.address,
                                             contact_number=order.contact_number,
                                             created_by=request.user,
                                             note=order.note)

                total_vat = total = total_price = total_op_price = total_price_regular_product = 0
                for p in products:
                    product = Product.objects.get(id=p["product_id"])
                    is_op_unchanged = OrderProduct.objects.filter(product=product,
                                                                  order=existing_order)
                    if is_op_unchanged and is_op_unchanged[0].order_product_qty >= p["product_quantity"]:
                        op = OrderProduct.objects.create(product=product,
                                                         order=order,
                                                         order_product_price=is_op_unchanged[0].order_product_price,
                                                         product_price=is_op_unchanged[0].product_price,
                                                         order_product_qty=p["product_quantity"])
                    else:
                        op = OrderProduct.objects.create(product=product,
                                                         order=order,
                                                         order_product_qty=p["product_quantity"])
                    total_price += float(op.product_price) * op.order_product_qty
                    total_op_price += op.order_product_price * op.order_product_qty
                    total += float(op.order_product_price_with_vat) * op.order_product_qty
                    total_vat += float(op.order_product_price_with_vat - op.order_product_price) * op.order_product_qty
                    if op.product_price == op.order_product_price:
                        total_price_regular_product += float(op.product_price) * op.order_product_qty

                if is_coupon_discount:
                    coupon_discount_amount, _, _, _ = coupon_checker(is_coupon_discount.coupon.coupon_code,
                                                                     products, order.user, is_used=True)

                order.order_total_price = round(total + delivery_charge - coupon_discount_amount - additional_discount)
                order.total_vat = total_vat
                product_discount = total_price - total_op_price
                total_discount_amount = coupon_discount_amount + product_discount + additional_discount

                if order.user.first_name and order.user.last_name:
                    billing_person_name = order.user.first_name + " " + order.user.last_name
                elif order.user.first_name:
                    billing_person_name = order.user.first_name
                else:
                    billing_person_name = ""

                new_invoice = InvoiceInfo.objects.create(invoice_number=order.invoice_number,
                                                         billing_person_name=billing_person_name,
                                                         billing_person_email=order.user.email,
                                                         billing_person_mobile_number=order.user.mobile_number,
                                                         delivery_contact_number=order.contact_number,
                                                         delivery_address=invoice.delivery_address,
                                                         delivery_date_time=order.delivery_date_time,
                                                         delivery_charge=delivery_charge,
                                                         discount_amount=total_discount_amount,
                                                         net_payable_amount=order.order_total_price,
                                                         payment_method='CASH_ON_DELIVERY',
                                                         paid_status=False,
                                                         order_number=order,
                                                         user=order.user,
                                                         created_by=request.user)
                order.save()

                if coupon_discount_amount:
                    DiscountInfo.objects.create(discount_amount=coupon_discount_amount,
                                                discount_type='CP',
                                                discount_description=is_coupon_discount.coupon_discount_description,
                                                coupon=is_coupon_discount.coupon,
                                                invoice=new_invoice)

                if product_discount:
                    DiscountInfo.objects.create(discount_amount=product_discount,
                                                discount_type='PD',
                                                discount_description='Product Offer Discount',
                                                invoice=new_invoice)

                if additional_discount:
                    DiscountInfo.objects.create(discount_amount=additional_discount,
                                                discount_type='AD',
                                                discount_description='Additional Discount',
                                                invoice=new_invoice)
            else:
                if data['order_status'] == 'Order Completed' or data['order_status'] == 'Order Cancelled':
                    order.order_status = all_order_status[data['order_status']]
                    order.save()
                else:
                    return Response({
                        "status": "failed",
                        "message": "Invalid request!"
                    }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "status": "success",
                "message": "Order updated.",
                "order_id": order.id}, status=status.HTTP_200_OK)
