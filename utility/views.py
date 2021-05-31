from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shodai.permissions import GenericAuth, ServiceAPIAuth
from order.models import Order, OrderProduct, InvoiceInfo
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


class AreaList(APIView):                #get area list and create area
    permission_classes = [GenericAuth]

    def get(self,request):
        queryset = Area.objects.all()
        serializer = AreaSerializer(queryset,many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        serializer = AreaSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class AreaDetails(APIView):         # area object get, update and delete
    permission_classes = [GenericAuth]

    def get_area_obj(self,id):
        return get_object_or_404(Area,id=id)

    def get(self,request,id):
        obj = self.get_area_obj(id)
        serializer = AreaSerializer(obj)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,id):
        obj = self.get_area_obj(id)
        serializer = AreaSerializer(obj,data=request.data,context={'request',request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if request.user.is_staff:
            obj = self.get_area_obj(id)
            obj.delete()
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class ProductUnitList(APIView):         # product unit list get and create
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
        return Response({'Duplicat data: '+ str(request.data['product_unit'])}, status=status.HTTP_400_BAD_REQUEST)


class ProductUnitDetails(APIView):          #product unit object get, update and delete
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


class RemarksList(APIView):             #get remarks list and create area

    permission_classes = [GenericAuth]

    def get(self,request):
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


class RemarksDetails(APIView):              #remarks unit object get, update and delete
    permission_classes = [GenericAuth]

    def get_remarks_obj(self,id):
        return get_object_or_404(Remarks,id=id)

    def get(self,request,id):
        obj = self.get_remarks_obj(id)
        serializer = RemarksSerializer(obj)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,id):
        obj = self.get_remarks_obj(id)
        serializer = RemarksSerializer(obj,data=request.data,context={'request',request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

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
