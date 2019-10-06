from django.shortcuts import render
from order.serializers import OrderProductSerializer, OrderSerializer
from order.models import OrderProduct, Order, Vat

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework import permissions

# Create your views here.
from sodai.utils.permission import GenericAuth


class OrderList(APIView):
    # """ List of all order from customer
    #     """
    permission_classes = [GenericAuth]
    def get(self, request, format=None):
        is_staff = request.user.is_staff
        order = Order.objects.all()
        print(order)
        if is_staff:
            order = Order.objects.all()
        else:
            user_type = request.user.user_type
            if user_type=='CM':  # Customer = CM
                order = Order.objects.filter(created_by=request.user)
            elif user_type=='RT': # Retailer = RT
                order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            elif user_type== 'PD': # Producer = PD
                order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            elif user_type== 'SF': # Staff = SF
                order = Order.objects.filter(created_by=request.user)
            
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
            serializer = OrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)





class OrderDetail(APIView):
    """
    Retrieve, update and delete Orders
    """
    def get_object(self, request, pk):
        is_staff = request.user.is_staff
        try:
            if is_staff:
                return Order.objects.get(pk=pk)
            else:
                user_type = request.user.user_type
                if user_type=='CM':  # Customer = CM
                    return Order.objects.get(pk=pk, created_by=request.user)
                elif user_type=='RT': # Retailer = RT
                    return Order.objects.get(pk=pk, created_by=request.user)
                    # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                elif user_type== 'PD': # Producer = PD
                    return Order.objects.get(pk=pk, created_by=request.user)
                     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                return Order.objects.get(pk=pk, created_by=request.user)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        order = self.get_object(request, pk)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        order = self.get_object(request, pk)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        order = self.get_object(request, pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)