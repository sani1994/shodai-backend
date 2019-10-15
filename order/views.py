from django.shortcuts import render
from order.serializers import OrderSerializer,OrderProductSerializer
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
        queryset = Order.objects.all()
        # print(queryset)
        if queryset:
            serializer = OrderSerializer(queryset,many=True,context={'request': request})
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        serializer = OrderSerializer(data=request.data,context={'request': request})
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
            serializer = OrderSerializer(obj,context={'request': request})
            if serializer:
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def put(self,request,id):
        obj = self.get_order_object(id)
        if obj:
            serializer = OrderSerializer(obj,data=request.data,context={'request': request.data})
            if serializer.is_valid():
                serializer.save(modified_by= request.user)
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
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def post(self,request):
        serializer =  OrderProductSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status= status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


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
        print(obj)
        if obj:
            obj.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)