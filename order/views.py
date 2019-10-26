from django.shortcuts import render
from order.serializers import OrderSerializer,OrderProductSerializer,VatSerializer
from order.models import OrderProduct, Order, Vat

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework import permissions

# Create your views here.
from sodai.utils.permission import GenericAuth

# NB.
# No authorization has been set yet, after completing we will set authorization


# class OrderList(APIView):
#     # """ List of all order from customer
#     #     """
#     permission_classes = [GenericAuth]
#     def get(self, request, format=None):
#         is_staff = request.user.is_staff
#         order = Order.objects.all()
#         print(order)
#         if is_staff:
#             order = Order.objects.all()
#         else:
#             user_type = request.user.user_type
#             if user_type=='CM':  # Customer = CM
#                 order = Order.objects.filter(created_by=request.user)
#             elif user_type=='RT': # Retailer = RT
#                 order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#             elif user_type== 'PD': # Producer = PD
#                 order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#             elif user_type== 'SF': # Staff = SF
#                 order = Order.objects.filter(created_by=request.user)
#
#         serializer = OrderSerializer(order, context={'request': request})
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#             serializer = OrderSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(created_by=request.user)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
#
#
#
# class OrderDetail(APIView):
#     """
#     Retrieve, update and delete Orders
#     """
#     def get_object(self, request, pk):
#         is_staff = request.user.is_staff
#         try:
#             if is_staff:
#                 return Order.objects.get(pk=pk)
#             else:
#                 user_type = request.user.user_type
#                 if user_type=='CM':  # Customer = CM
#                     return Order.objects.get(pk=pk, created_by=request.user)
#                 elif user_type=='RT': # Retailer = RT
#                     return Order.objects.get(pk=pk, created_by=request.user)
#                     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#                 elif user_type== 'PD': # Producer = PD
#                     return Order.objects.get(pk=pk, created_by=request.user)
#                      # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
#                 return Order.objects.get(pk=pk, created_by=request.user)
#         except Order.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         order = self.get_object(request, pk)
#         serializer = OrderSerializer(order, data=request.data)
#         if serializer.is_valid():
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#     def put(self, request, pk, format=None):
#         order = self.get_object(request, pk)
#         serializer = OrderSerializer(order, data=request.data)
#         if serializer.is_valid():
#             serializer.save(modified_by=request.user)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         order = self.get_object(request, pk)
#         order.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class OrderList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        if request.user.user_type == 'CM':
            user_id = request.user.id
            orderList = Order.objects.filter(user_id=user_id)
            serializer = OrderSerializer(orderList,many=True)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        # elif request.user.user_type == 'RT':
        #     user_id = request.user.id
        #     orderList = Order.objects.filter(user_id=user_id)
        #     serializer = OrderSerializer(orderList,many=True)
        #     if serializer:
        #         return Response(serializer.data,status=status.HTTP_200_OK)
        #     return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        queryset = Order.objects.all()
        if queryset:
            serializer = OrderSerializer(queryset,many=True,context={'request': request})
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def post(self,request,*args,**kwargs):
        if request.data['contact_number'] == '':
            request.POST._mutable =True
            request.data['contact_number'] = request.user.mobile_number
            request.POST._mutable = False
        serializer = OrderSerializer(data=request.data,many=isinstance(request.data,list),context={'request': request})
        print(serializer)
        if serializer.is_valid():
            serializer.save(user = request.user,created_by = request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):

    permission_classes = [GenericAuth]

    def get_order_object(self,id):
        obj = Order.objects.filter(id = id).first()
        return obj

    def get(self,request,id):
        obj = self.get_order_object(id)
        if obj:
            serializer = OrderSerializer(obj)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        obj = self.get_order_object(id)
        if obj:
            serializer = OrderSerializer(obj,data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def delete(self,request,id):
        obj = self.get_order_object(id)
        if obj:
            obj.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)


class OrderProductList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        queryset = OrderProduct.objects.all()
        if queryset:
            serializer = OrderProductSerializer(queryset,many=True,context={'request': request})
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializable data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        if request.user.user_type== 'CM':
            response = {
                'rspns',
                'status_code',
            }
            responses = []
            for data in request.data:
                serializer = OrderProductSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    response= {'rspns': serializer.data,'status_code': status.HTTP_200_OK}
                    responses.append(response)
                else:
                    response = {'rspns': serializer.errors,'status_code': status.HTTP_400_BAD_REQUEST}
                    responses.append(response)
            return Response(responses)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class OrderProductDetail(APIView):

    permission_classes = [GenericAuth]

    def get_orderproduct_obj(self,id):
        obj = OrderProduct.objects.filter(id = id).first()
        return obj

    def get(self,request,id):
        obj = self.get_orderproduct_obj(id)
        if obj:
            serializer = OrderProductSerializer(obj)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        obj = self.get_orderproduct_obj(id)
        if obj:
            serializer = OrderProductSerializer(obj,data=request.data,context={'request':request})
            if serializer.is_valid():
                serializer.save(modified_by = request.user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)


    def delete(self,request,id):
        obj = self.get_orderproduct_obj(id)
        if obj:
            obj.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)


class VatList(APIView):

    permission_classes = [GenericAuth]

    def get(self,request):
        queryset = Vat.objects.all()
        if queryset:
            serializer = VatSerializer(queryset,many=True)
            if serializer:
                return Response (serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        serializer = VatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by = request.user)
            return Response (serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VatDetail(APIView):

    permission_classes = [GenericAuth]

    def get_vat_object(self,id):
        obj = Vat.objects.filter(id=id).first()
        return obj

    def get(self,request,id):
        obj = self.get_vat_object(id)
        if obj:
            serializer =  VatSerializer(obj)
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        obj = self.get_vat_object(id)
        if obj:
            serializer = VatSerializer(obj,data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by = request.user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def delete(self,requst,id):
        obj = self.get_vat_object(id)
        if obj:
            obj.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)


class OrderDeatils(APIView):

    permission_classes = [GenericAuth]

    def get(self,request,id):
        obj = Order.objects.filter(id=id).first()
        orderProductList = obj.orderproduct_set.all()
        serializer = OrderProductSerializer(orderProductList,many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)