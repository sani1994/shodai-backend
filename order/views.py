import datetime
from django.db.models import Q
from notifications.signals import notify
from rest_framework.generics import get_object_or_404
from order.serializers import OrderSerializer, OrderProductSerializer, VatSerializer, OrderProductReadSerializer, \
    DeliveryChargeSerializer, PaymentInfoDetailSerializer, PaymentInfoSerializer, OrderDetailSerializer, \
    OrderDetailPaymentSerializer #TimeSlotSerializer
from order.models import OrderProduct, Order, Vat, DeliveryCharge, PaymentInfo, #TimeSlot
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from retailer.models import AcceptedOrder
from sodai.utils.permission import GenericAuth
from utility.notification import email_notification



class OrderList(APIView):
    permission_classes = [GenericAuth]

    def get(self, request):
        if request.user.user_type == 'CM':
            user_id = request.user.id
            orderList = Order.objects.filter(user_id=user_id)
            serializer = OrderSerializer(orderList, many=True)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        queryset = Order.objects.all()
        if queryset:
            serializer = OrderSerializer(queryset, many=True, context={'request': request})
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)


    # def post(self, request, *args, **kwargs):
    #     # print(request.data['order_total_price'])
    #     # vat = Vat.objects.get(id=1).vat_amount
    #     delivery_charge = DeliveryCharge.objects.get(id=1).delivery_charge_inside_dhaka

    #     datetime = request.data['delivery_date_time'].split('||')
    #     slot = datetime[0]
    #     date = datetime[1]
    #     time = TimeSlot.objects.filter(slot=slot)

    #     for t in time:
    #         # print(t.time)
    #         year = date.split('-')[2]
    #         month = date.split('-')[1]
    #         day = date.split('-')[0]
    #         date = year + '-' + month + '-' +  day
    #         request.POST._mutable = True
    #         request.data['delivery_date_time'] = date + ' ' + str(t.time)
    #         request.POST._mutable = False

    #     # print(request.data['delivery_date_time'])

    #     if request.data['contact_number'] == "":
    #         request.POST._mutable = True
    #         request.data['contact_number'] = request.user.mobile_number
    #         request.POST._mutable = False
    #     # print(request.data['delivery_date_time'])
        
    #     total = float(request.data['order_total_price'])
    #     # order_vat = (total * vat) / 100 
    #     if total > 0.0 and delivery_charge > 0:
    #         request.POST._mutable = True
    #         request.data['order_total_price'] =  total + delivery_charge #total +  order_vat 
    #         request.POST._mutable = False

    #     serializer = OrderSerializer(data=request.data, many=isinstance(request.data, list),
    #                                  context={'request': request})
    #     if serializer.is_valid():

    #         serializer.save(user=request.user, created_by=request.user)
    #         """
    #         To send notification to admin 
    #         """
    #         sub = "Order Placed"
    #         body = f"Dear Concern,\r\n User phone number :{request.user.mobile_number} \r\nUser type: {request.user.user_type} posted an order Order id: {serializer.data['id']}.\r\n \r\nThanks and Regards\r\nShodai"
    #         email_notification(sub, body)
    #         """
    #         Notification code ends here
    #         """
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class OrderList(APIView):
#     permission_classes = [GenericAuth]

#     def get(self, request):
#         if request.user.user_type == 'CM':
#             user_id = request.user.id
#             orderList = Order.objects.filter(user_id=user_id)
#             serializer = OrderSerializer(orderList, many=True)
#             if serializer:
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         queryset = Order.objects.all()
#         if queryset:
#             serializer = OrderSerializer(queryset, many=True, context={'request': request})
#             if serializer:
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)



   
    # def post(self, request, *args, **kwargs):
    #     now = datetime.datetime.now()
    #     year = now.year
    #     month = now.month
    #     day = now.day
    #     day_range = day + 6
    #     hour = now.hour 

    #     if day_range > 30 :
    #         day_range = day_range - 30
        
    #     if request.data['contact_number'] == "":
    #         request.POST._mutable = True
    #         request.data['contact_number'] = request.user.mobile_number
    #         request.POST._mutable = False

    #     date = request.data['delivery_date_time']
    #     delivery_year = int(date[:4])
    #     delivery_month = int(date[5:7])
    #     delivery_day = int(date[8:10])
    #     delivery_hour = int(date[11:13])
    #     # if year == delivery_year and month == delivery_month 

    #     bad_time = [1, 2, 3, 4, 5, 6, 7, 22, 23, 24]

    #     if day_range >= delivery_day:

    #         if delivery_hour not in bad_time:

    #             serializer = OrderSerializer(data=request.data, many=isinstance(request.data, list),
    #                                         context={'request': request})
    #             if serializer.is_valid():
        
    #                 serializer.save(user=request.user, created_by=request.user)
    #                 # print(serializer.data['delivery_date_time'])

    #                 """
    #                 To send notification to admin 
    #                 """
    #                 sub = "Order Placed"
    #                 body = f"Dear Concern,\r\n User phone number :{request.user.mobile_number} \r\nUser type: {request.user.user_type} posted an order Order id: {serializer.data['id']}.\r\n \r\nThanks and Regards\r\nShodai"
    #                 email_notification(sub, body)
    #                 """
    #                 Notification code ends here
    #                 """
    #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
    #             else:
    #                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #         else:
    #             return Response({"status": "This is not a vaild delivery time, Please Select a vaild time."}, status=status.HTTP_204_NO_CONTENT)
        
    #     else:
    #         return Response({"status": f"Select a vaild date from {day} to {day_range}"}, status=status.HTTP_204_NO_CONTENT)
            

class OrderDetail(APIView):
    permission_classes = [GenericAuth]

    def get_order_object(self, id):
        obj = Order.objects.filter(id=id).first()
        return obj

    def get(self, request, id):
        obj = self.get_order_object(id)
        # if obj.user == request.user or request.user == 'SF':
        serializer = OrderSerializer(obj)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        obj = self.get_order_object(id)
        if obj:
            serializer = OrderSerializer(obj, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, id):
        obj = self.get_order_object(id)
        if obj:
            obj.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

class OrderProductList(APIView):
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = OrderProduct.objects.all()
        if queryset:
            serializer = OrderProductReadSerializer(queryset, many=True, context={'request': request})
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializable data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        if request.user.user_type == 'CM':
            response = {
                'rspns',
                'status_code',
            }
            responses = []

            for data in request.data:
                serializer = OrderProductSerializer(data=data, context={'request': request.data})
                if serializer.is_valid():
                    # print(serializer.data)
                    serializer.save()
                    response = {'rspns': serializer.data, 'status_code': status.HTTP_200_OK}
                    responses.append(response)
                else:
                    response = {'rspns': serializer.errors, 'status_code': status.HTTP_400_BAD_REQUEST}
                    responses.append(response)
            return Response(responses)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

class OrderProductDetail(APIView):
    permission_classes = [GenericAuth]

    def get_orderproduct_obj(self, id):
        obj = OrderProduct.objects.filter(id=id).first()
        return obj

    def get(self, request, id):
        obj = self.get_orderproduct_obj(id)
        if obj:
            serializer = OrderProductReadSerializer(obj)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id):
        obj = self.get_orderproduct_obj(id)
        if obj:
            serializer = OrderProductSerializer(obj, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, id):
        obj = self.get_orderproduct_obj(id)
        if obj:
            obj.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

class VatList(APIView):
    permission_classes = [GenericAuth]

    def get(self, request):
        queryset = Vat.objects.all()
        if queryset:
            serializer = VatSerializer(queryset, many=True)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        serializer = VatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VatDetail(APIView):
    permission_classes = [GenericAuth]

    def get_vat_object(self, id):
        obj = Vat.objects.filter(id=id).first()
        return obj

    def get(self, request, id):
        obj = self.get_vat_object(id)
        if obj:
            serializer = VatSerializer(obj)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id):
        obj = self.get_vat_object(id)
        if obj:
            serializer = VatSerializer(obj, data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, requst, id):
        obj = self.get_vat_object(id)
        if obj:
            obj.delete()
            return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)


class OrderdProducts(APIView):  # this view returns all the products in a order. this has been commented out as it has marged with "Orderdetail" view in get function.

    permission_classes = [GenericAuth]

    # def get_order_object(self,id):
    #     obj = Order.objects.get(id = id)
    #     return obj

    def get(self, request, id):
        obj = get_object_or_404(Order, id=id)
        # print(obj)
        if obj.user == request.user or request.user.user_type == 'SF' or request.user.user_type == 'RT':
            orderProducts = []
            # orderProductList = obj.orderproduct_set.all()  # get all orderd products of individual product
            orderProductList = OrderProduct.objects.filter(order_id=obj.id) # get all orderd products of individual product
            orderProductSerializer = OrderProductReadSerializer(orderProductList, many=True)
            orderSerializer = OrderSerializer(obj)
            if orderProductSerializer and orderSerializer:
                orderProductLists = orderProductSerializer.data
                for orderProduct in orderProductLists:
                    orderProduct['product']['product_unit'] = orderProduct['product']['product_unit']['product_unit']
                    orderProduct['product']['product_meta'] = orderProduct['product']['product_meta']['name']
                    # orderProduct['product'].pop('created_by')
                    # orderProduct['product'].pop('modified_by')
                    product = orderProduct['product']
                    product['order_price'] = orderProduct['order_product_price']
                    product['order_qty'] = orderProduct['order_product_qty']
                    # product['product_unit'] = orderProduct['product']['product_unit'].product_unit
                    # print(orderProduct['product']['product_unit']['product_unit'])
                    orderProducts.append(product)
                order = orderSerializer.data
                order['orderProducts'] = orderProducts
                return Response(order, status=status.HTTP_200_OK)
            else:
                return Response({orderProductSerializer.errors + orderSerializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class OrderStatusUpdate(APIView):
    permission_classes = [GenericAuth]

    def post(self, request, id):
        if request.user.user_type == 'RT':
            obj = get_object_or_404(AcceptedOrder, id=id)
            if obj.user_id == request.user.id:
                order_obj = get_object_or_404(Order, id=obj.order_id)
                if not order_obj.order_status == 'OD':
                    setattr(order_obj, 'order_status', request.data['order_status'])
                    order_obj.save()
                    recipient = order_obj.user
                    notify.send(recipient=recipient, sender=request.user,
                                verb=f"Your is now in {order_obj.order_status} state.")
                    return Response({'Order status set to': order_obj.order_status}, status=status.HTTP_200_OK)
                return Response('Cannot update order status', status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "User Don't have permission to update status"}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.user_type == 'CM':
            order_obj = get_object_or_404(Order, id=id)
            if order_obj.user == request.user:
                setattr(order_obj, 'order_status', request.data['order_status'])  # set status in order
                order_obj.save()
                return Response({'Order status set to': order_obj.order_status}, status=status.HTTP_200_OK)
            return Response('Cannot update order status', status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)


class DeliverChargeList(APIView):

    def get(self, request):
        queryset = DeliveryCharge.objects.all()
        if queryset:
            serializer = DeliveryChargeSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response('{No data found}', status=status.HTTP_204_NO_CONTENT)


class VatDeliveryChargeList(APIView):
    '''
    this view returns vat and delivery charge as objects in return
    '''

    def get(self, request):
        vatqueryset = Vat.objects.all()
        vat_serializer = VatSerializer(vatqueryset, many=True)
        delivery_queryset = DeliveryCharge.objects.all()
        delivery_serializer = DeliveryChargeSerializer(delivery_queryset, many=True)
        list = []
        data = {
            'vat': vat_serializer.data[0]['vat_amount'],
            'delivery_charge': delivery_serializer.data[0]['delivery_charge_inside_dhaka']
        }
        list.append(data)
        return Response(list, status=status.HTTP_200_OK)


import json
import requests

class PaymentInfoListCreate(APIView):
    """ Check Order Using bill_id """

    def get(self, request):

        queryset = Order.objects.all().order_by('-id')

        if queryset:
            query = self.request.GET.get("bill_id")
            query_invoice = self.request.GET.get("invoice_number")

            if query or query_invoice:
                # queryset = Order.objects.filter(bill_id__exact=query)
                queryset_invoice = Order.objects.filter(invoice_number__exact=query_invoice)

                # if queryset:
                #     serializer = OrderDetailPaymentSerializer(queryset, many=True, context={'request': request})

                #     if serializer:
                #         # d = json.dumps(serializer.data)
                #         # d = json.loads(d)
                #         payment = serializer.data[0]
                #         year = payment['created_on']

                  
                #         data = {
                #             'status': "success",
                #             'payment_id': payment['payment_id'],
                #             'bill_id': payment['bill_id'],
                #             'total_amount': payment['order_total_price'],
                #             'currency': payment['currency'],
                #             'created_by': payment['user']["username"],
                #             'created_on': year,
                #             'bill_info':  {
                #                             "type": "product_purchase",
                #                             'order_products': payment['products']
                #             }
                #         }
                #         return Response(data, status=status.HTTP_200_OK)
                #     else:
                #         return Response({"status": "Not serializble data"}, status=status.HTTP_200_OK)
    

            
                if queryset_invoice:
                    serializer = OrderDetailPaymentSerializer(queryset_invoice, many=True, context={'request': request})

                    if serializer:
                        # d = json.dumps(serializer.data)
                        # d = json.loads(d)
                        payment = serializer.data[0]
                        year = payment['created_on']

                  
                        data = {
                            'status': "success",
                            # 'payment_id': payment['payment_id'],
                            # 'bill_id': payment['bill_id'],
                            'total_amount': payment['order_total_price'],
                            "currency": "BDT" ,
                            'created_on': year,
                            # 'created_by': payment['user']["username"],
                            "invoice_details": {
                            "type": "order_payment",
                            "user_id": str(payment['user']["id"]),
                            "order_id": str(payment["id"]),
                            "order_products": payment['products']
                            
                        }
                    }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response({"status": "Not serializble data"}, status=status.HTTP_200_OK)
                else:
                    data = {
                        "status": "failed",
                        "message": "invalid invoice number"
                    }
                    return Response(data, status=status.HTTP_200_OK)


            
            else:
                serializer = OrderDetailSerializer(queryset, many=True, context={'request': request})
                if serializer:
                    data = {
                        "status": "success",
                        # "data": serializer.data,
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Not serializble data"}, status=status.HTTP_200_OK)

        return Response({"status": "No content"}, status=status.HTTP_200_OK)


class OrderLatest(APIView):
    """Get the latest `order` than get all require data and send a post to ssl,
       If Post status is `success` than create a PaymentInfo object.
    """
    permission_classes = [GenericAuth]

    def get(self, request):
        user_id = request.user.id
      
        order = Order.objects.filter(user=request.user, order_status='OD').order_by('-id')[:1]

        if order:
            # product = OrderProduct.objects.filter(order=order)
   
            # orderproduct = OrderProductSerializer(product, many=True, context={'request': request}).data
        
            serializer = OrderDetailSerializer(order, many=True, context={'request': request})

            if serializer and serializer.data[0]["id"]:
                # d = json.dumps(serializer.data)
                # d = json.loads(d)
                d = serializer.data       

                products = []
                for product in d[0]['products']:
                    products.append(product)
                # serializer.data[0]["invoice_number"]
           
                category = [c["product_category"] for c in [p["product"]["product_meta"] for p in products]]

                product_name = [p["product"]["product_name"] for p in products]
                # d[0]["invoice_number"]
                body = { 
                    "project_id": "shodai", 
                    "project_secret": "5h0d41p4ym3n7",
                    "bill_id": d[0]["bill_id"], 
                    "user_id": str(d[0]["user"]['id']),  
                    "product_name": ' '.join(product_name) if product_name else "None",  
                    "product_category":  str(category[0]) if category else "None",  
                    "product_profile": "general",  
                    "invoice_number":d[0]["invoice_number"], 
                    "customer_name": d[0]["user"]['username'] if d[0]["user"]['username'] else 'None',
                    "customer_email":  d[0]["user"]['email'] if d[0]["user"]['email'] else 'None',
                    "customer_mobile":  d[0]["user"]["mobile_number"],
                    "customer_address": d[0]["delivery_place"], 
                    "customer_city": d[0]['address']["city"] if d[0]['address'] else 'Dhaka', 
                    "customer_country": d[0]['address']["country"] if d[0]['address'] else 'BD'
                }
                # print(body)
                data=json.dumps(body)
                # data = json.loads(data)
                response = requests.post("http://dev.finder-lbs.com:8009/online_payment/ssl", data=data)
                content = response.json()
                # print(content)

                if response.status_code == 200:
                    if content["status"]=="success":

                        payment_id = content["payment_id"]

                        order_id = int(serializer.data[0]["id"])
                        order = Order.objects.get(id=order_id)
                        bill_id = serializer.data[0]["bill_id"]
                        invoice_number = serializer.data[0]["invoice_number"]
                        payment = PaymentInfo(
                                payment_id=payment_id, 
                                order_id=order, 
                                bill_id=bill_id, 
                                invoice_number=invoice_number,
                                payment_status="INITIATED" 
                            )
                        payment.save()

                return Response(content, status=status.HTTP_200_OK)

            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "No content"}, status=status.HTTP_200_OK)


        return Response({"status": "Unauthorized request"}, status=status.HTTP_200_OK)


# class TimeSlotList(APIView):

#     def get(self, request):
        
#         queryset = TimeSlot.objects.filter(allow=True)
#         if queryset:
#             serializer = TimeSlotSerializer(queryset, many=True)
#             if serializer:
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
        
