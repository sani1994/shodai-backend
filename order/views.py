from xxlimited import Null

from django.shortcuts import render
from rest_framework.generics import get_object_or_404

from order.serializers import OrderSerializer, OrderProductSerializer, VatSerializer, OrderProductReadSerializer, \
    DeliveryChargeSerializer
from order.models import OrderProduct, Order, Vat, DeliveryCharge

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework import permissions

# Create your views here.
from retailer.models import AcceptedOrder
from sodai.utils.permission import GenericAuth
from utility.notification import email_notification


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
        if request.data['contact_number'] == "":
            request.POST._mutable =True
            request.data['contact_number'] = request.user.mobile_number
            request.POST._mutable = False
        serializer = OrderSerializer(data=request.data,many=isinstance(request.data,list),context={'request': request})
        if serializer.is_valid():
            serializer.save(user = request.user,created_by = request.user)
            """
            To send notification to admin 
            """
            sub = "Order Placed"
            body = f"Dear Concern,\r\n User phone number :{request.user.mobile_number} \r\nUser type: {request.user.user_type} posted an order Order id: {serializer.data['id']}.\r\n \r\nThanks and Regards\r\nShodai"
            email_notification(sub,body)
            """
            Notification code ends here
            """
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):

    permission_classes = [GenericAuth]

    def get_order_object(self,id):
        obj = Order.objects.filter(id = id).first()
        return obj

    def get(self,request,id):
        obj = self.get_order_object(id)
        # if obj.user == request.user or request.user == 'SF':
        serializer = OrderSerializer(obj)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

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
            serializer = OrderProductReadSerializer(queryset,many=True,context={'request': request})
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
                serializer = OrderProductSerializer(data=data,context={'request': request.data})
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
            serializer = OrderProductReadSerializer(obj)
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


class OrderdProducts(APIView): # this view returns all the products in a order. this has been commented out as it has marged with "Orderdetail" view in get function.

    permission_classes = [GenericAuth]

    # def get_order_object(self,id):
    #     obj = Order.objects.get(id = id)
    #     return obj

    def get(self,request,id):
        obj = get_object_or_404(Order,id=id)
        if obj.user == request.user or request.user.user_type == 'SF' or request.user.user_type == 'RT':
            orderProducts = []
            orderProductList = obj.orderproduct_set.all()  # get all orderd products of individual product
            orderProductSerializer = OrderProductReadSerializer(orderProductList, many=True)
            orderSerializer = OrderSerializer(obj)
            if orderProductSerializer and orderSerializer:
                orderProductLists = orderProductSerializer.data
                for orderProduct in orderProductLists:
                    orderProduct['product']['product_unit']= orderProduct['product']['product_unit']['product_unit']
                    orderProduct['product']['product_meta'] = orderProduct['product']['product_meta']['name']
                    # orderProduct['product'].pop('created_by')
                    # orderProduct['product'].pop('modified_by')
                    product = orderProduct['product']
                    product['order_price']= orderProduct['order_product_price']
                    product['order_qty'] = orderProduct['order_product_qty']
                    # product['product_unit'] = orderProduct['product']['product_unit'].product_unit
                    # print(orderProduct['product']['product_unit']['product_unit'])
                    orderProducts.append(product)
                order = orderSerializer.data
                order['orderProducts']=orderProducts
                return Response(order, status=status.HTTP_200_OK)
            else:
                return Response({orderProductSerializer.errors + orderSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class OrderStatusUpdate(APIView):

    permission_classes = [GenericAuth]

    def get_acceptedOrder_obj(self,id):
        obj = AcceptedOrder.objects.get(id=id)
        return obj

    def get_oder_obj(self,id):
        obj = Order.objects.get(id=id)
        return obj

    def post(self,request,id):
        if request.user.user_type== 'RT':
            obj = self.get_acceptedOrder_obj(id)
            if obj.user_id == request.user.id:
                ordr_id = obj.order_id
                order_obj = self.get_oder_obj(ordr_id)
                if not order_obj.order_status== 'OD':
                    setattr(order_obj,'order_status',request.data['order_status'])
                    order_obj.save()
                    return Response({'Order status set to': order_obj.order_status},status=status.HTTP_200_OK)
                return Response('Cannot update order status',status=status.HTTP_400_BAD_REQUEST )
            return Response({"status": "User Don't have permission to update status"}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.user_type == 'CM':
            order_obj = get_object_or_404(Order,id = id)
            if order_obj.user == request.user:
                setattr(order_obj,'order_status',request.data['order_status'])  #set status in order
                order_obj.save()
                return Response({'Order status set to': order_obj.order_status}, status=status.HTTP_200_OK)
            return Response('Cannot update order status', status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class DeliverChargeList(APIView):

    def get(self,request):
        queryset = DeliveryCharge.objects.all()
        if queryset:
            serializer = DeliveryChargeSerializer(queryset,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response('{No data found}', status=status.HTTP_204_NO_CONTENT)


class VatDeliveryChargeList(APIView):
    '''
    this view returns vat and delivery charge as objects in return
    '''

    def get(self,request):
        vatqueryset = Vat.objects.all()
        vat_serializer = VatSerializer(vatqueryset,many=True)
        delivery_queryset = DeliveryCharge.objects.all()
        delivery_serializer = DeliveryChargeSerializer(delivery_queryset,many=True)
        list = []
        data = {
            'vat':vat_serializer.data[0]['vat_amount'],
            'delivery_charge': delivery_serializer.data[0]['delivery_charge_inside_dhaka']
        }
        list.append(data)
        return Response(list,status=status.HTTP_200_OK)

