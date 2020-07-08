import datetime
from django.db.models import Q
from decouple import config
from notifications.signals import notify
from rest_framework.generics import get_object_or_404
from order.serializers import OrderSerializer, OrderProductSerializer, VatSerializer, OrderProductReadSerializer, \
    DeliveryChargeSerializer, PaymentInfoDetailSerializer, PaymentInfoSerializer, OrderDetailSerializer, \
    OrderDetailPaymentSerializer, TimeSlotSerializer
from order.models import OrderProduct, Order, Vat, DeliveryCharge, PaymentInfo, TimeSlot
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from retailer.models import AcceptedOrder
from sodai.utils.permission import GenericAuth
from utility.notification import email_notification


class TimeSlotList(APIView):
    """`Get` time slot that are allowed"""
    def get(self, request):
        queryset = TimeSlot.objects.filter(allow=True)
        if queryset:
            serializer = TimeSlotSerializer(queryset, many=True)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)


class OrderList(APIView):
    """Here customer can `get` and `post` order"""
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

    def post(self, request, *args, **kwargs):
        delivery_charge = DeliveryCharge.objects.get(id=1).delivery_charge_inside_dhaka

        datetime = request.data['delivery_date_time'].split('||')
        slot = datetime[0]
        date = datetime[1]
        
        time = TimeSlot.objects.filter(slot=slot.replace(' ', ''))
        for t in time:
            year = date.split('-')[2]
            month = date.split('-')[1]
            day = date.split('-')[0]
            date = year + '-' + month + '-' +  day
            request.POST._mutable = True
            request.data['delivery_date_time'] = date + ' ' + str(t.time)
            request.POST._mutable = False

        if request.data['contact_number'] == "":
            request.POST._mutable = True
            request.data['contact_number'] = request.user.mobile_number
            request.POST._mutable = False

        total = float(request.data['order_total_price'])

        if total > 0.0 and delivery_charge > 0:
            request.POST._mutable = True
            request.data['order_total_price'] =  total + delivery_charge 
            request.POST._mutable = False

        serializer = OrderSerializer(data=request.data, many=isinstance(request.data, list),
                                     context={'request': request})
        if serializer.is_valid():

            serializer.save(user=request.user, created_by=request.user)
            """
            To send notification to admin
            """
            sub = "Order Placed"
            body = f"Dear Concern,\r\n User phone number :{request.user.mobile_number} \r\nUser type: {request.user.user_type} posted an order Order id: {serializer.data['id']}.\r\n \r\nThanks and Regards\r\nShodai"
            email_notification(sub, body)
            """
            Notification code ends here
            """
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):
    """Here customer can `get` a order user by id then can `put`, and `delete` a order"""
    permission_classes = [GenericAuth]

    def get_order_object(self, id):
        obj = Order.objects.filter(id=id).first()
        return obj

    def get(self, request, id):
        obj = self.get_order_object(id)
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
    """Here customer can `get` and `post` order product"""
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
    """Here customer can see order product detail by product id"""
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


class OrderdProducts(APIView):  
    """this view returns all the products in a order. this has been commented out as
       it has marged with "Orderdetail" view in get function.
    """
    permission_classes = [GenericAuth]

    def get(self, request, id):
        obj = get_object_or_404(Order, id=id)
        if obj.user == request.user or request.user.user_type == 'SF' or request.user.user_type == 'RT':
            orderProducts = []
            # orderProductList = obj.orderproduct_set.all()  # get all orderd products of individual product
            orderProductList = OrderProduct.objects.filter(
                order_id=obj.id)  # get all orderd products of individual product
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
                queryset_invoice = Order.objects.filter(invoice_number__exact=query_invoice)

                if queryset_invoice:
                    serializer = OrderDetailPaymentSerializer(queryset_invoice, many=True, context={'request': request})

                    if serializer:
                      
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

                body = {
                    "project_id": config("PAYMENT_PROJECT_ID", None),
                    "project_secret": config("PAYMENT_PROJECT_SECRET", None),
                    "invoice_number": d[0]["invoice_number"],
                    "product_name": ' '.join(product_name) if product_name else "None",
                    "product_category": str(category[0]) if category else "None",
                    "product_profile": "general",
                    "customer_name": d[0]["user"]['username'] if d[0]["user"]['username'] else 'None',
                    "customer_email": d[0]["user"]['email'] if d[0]["user"]['email'] else 'None',
                    "customer_mobile": d[0]["user"]["mobile_number"],
                    "customer_address": d[0]["delivery_place"],
                    "customer_city": d[0]['address']["city"] if d[0]['address'] else 'Dhaka',
                    "customer_country": d[0]['address']["country"] if d[0]['address'] else 'BD'
                }

                data = json.dumps(body)
            
                response = requests.post(config("PAYMENT_PROJECT_URL", None), data=data)
                content = response.json()

                if response.status_code == 200:
                    if content["status"] == "success":
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


class TimeSlotList(APIView):

    def get(self, request):

        queryset = TimeSlot.objects.filter(allow=True)
        if queryset:
            serializer = TimeSlotSerializer(queryset, many=True)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not serializble data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
