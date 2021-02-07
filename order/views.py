import csv
import datetime
import uuid

from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from decouple import config
from django.http import HttpResponse
from django.template.loader import get_template
from notifications.signals import notify
from rest_framework.generics import get_object_or_404
from order.serializers import OrderSerializer, OrderProductSerializer, VatSerializer, OrderProductReadSerializer, \
    DeliveryChargeSerializer, PaymentInfoDetailSerializer, PaymentInfoSerializer, OrderDetailSerializer, \
    OrderDetailPaymentSerializer, TimeSlotSerializer
from order.models import OrderProduct, Order, Vat, DeliveryCharge, PaymentInfo, TimeSlot, InvoiceInfo
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from retailer.models import AcceptedOrder
from sodai.utils.permission import GenericAuth
from utility.notification import email_notification, send_sms


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
        delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka

        datetime = request.data['delivery_date_time'].split('||')
        slot = datetime[0]
        date = datetime[1]

        year = date.split('-')[2]
        month = date.split('-')[1]
        day = date.split('-')[0]
        date = year + '-' + month + '-' + day

        time = TimeSlot.objects.filter(slot=slot)
        for t in time:
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
            request.data['order_total_price'] = total + delivery_charge  # total +  order_vat
            request.POST._mutable = False

        serializer = OrderSerializer(data=request.data, many=isinstance(request.data, list),
                                     context={'request': request})
        if serializer.is_valid():

            serializer.save(user=request.user, created_by=request.user)

            # Create InvoiceInfo Instance
            order_instance = Order.objects.get(id=serializer.data['id'])
            if order_instance:
                order_instance.payment_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.bill_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order_instance.save()
            if request.user.first_name and request.user.last_name:
                billing_person_name = request.user.first_name + " " + request.user.last_name
            else:
                billing_person_name = request.user.username
            if order_instance.address:
                if order_instance.address.road:
                    address = order_instance.address.road
            else:
                if order_instance.delivery_place:
                    address = order_instance.delivery_place

            InvoiceInfo.objects.create(invoice_number=order_instance.invoice_number,
                                       billing_person_name=billing_person_name,
                                       billing_person_email=request.user.email,
                                       billing_person_mobile_number=request.user.mobile_number,
                                       delivery_contact_number=order_instance.contact_number,
                                       delivery_address=address,
                                       delivery_date_time=order_instance.delivery_date_time,
                                       delivery_charge=delivery_charge,
                                       net_payable_amount=order_instance.order_total_price,
                                       payment_method='SSLCOMMERZ',
                                       order_number=order_instance,
                                       user=request.user,
                                       created_by=request.user)

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

    # def delete(self, request, id):
    #     obj = self.get_order_object(id)
    #     if obj:
    #         obj.delete()
    #         return Response({"status": "Delete successful..!!"}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)


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
            responses = []

            for data in request.data:
                time = data['time_slot'].split('||')
                slot = time[0]
                serializer = OrderProductSerializer(data=data, context={'request': request.data})
                if serializer.is_valid():
                    serializer.save()
                    response = {'rspns': serializer.data, 'status_code': status.HTTP_200_OK}
                    responses.append(response)
                else:
                    response = {'rspns': serializer.errors, 'status_code': status.HTTP_400_BAD_REQUEST}
                    responses.append(response)

            order_instance = Order.objects.filter(pk=serializer.data['order'])[0]
            invoice = InvoiceInfo.objects.filter(invoice_number=order_instance.invoice_number)[0]
            delivery_charge = invoice.delivery_charge

            if request.user.first_name and request.user.last_name:
                billing_person_name = request.user.first_name + " " + request.user.last_name
            else:
                billing_person_name = request.user.username
            if order_instance.address:
                if order_instance.address.road:
                    address = order_instance.address.road
            else:
                if order_instance.delivery_place:
                    address = order_instance.delivery_place

            product_list = OrderProduct.objects.filter(order__pk=serializer.data['order'])
            matrix = []
            is_offer = False
            total_price_without_offer = total_vat = 0
            for p in product_list:
                total = float(p.product_price) * p.order_product_qty
                total_price_without_offer += total
                total_vat += float(p.order_product_price_with_vat - p.order_product_price) * p.order_product_qty
                if p.order_product_price != p.product_price:
                    is_offer = True
                    total_by_offer = float(p.order_product_price) * p.order_product_qty
                    col = [p.product.product_name, p.product.product_unit, p.product_price,
                           p.order_product_price, int(p.order_product_qty), total_by_offer]
                else:
                    col = [p.product.product_name, p.product.product_unit, p.product_price,
                           "--", int(p.order_product_qty), total]
                matrix.append(col)

            order_instance.total_vat = total_vat
            order_instance.save()

            # send email to user
            sub_total = order_instance.order_total_price - order_instance.total_vat - delivery_charge
            invoice.discount_amount = float(round(total_price_without_offer - sub_total))
            invoice.save()

            content = {'user_name': billing_person_name,
                       'order_number': order_instance.order_number,
                       'shipping_address': address,
                       'mobile_no': order_instance.contact_number,
                       'order_date': order_instance.created_on.date(),
                       'delivery_date_time': str(order_instance.delivery_date_time.date()) + " ( " + str(slot) + " )",
                       'sub_total': sub_total,
                       'vat': total_vat,
                       'delivery_charge': delivery_charge,
                       'total': order_instance.order_total_price,
                       'order_details': matrix,
                       'saved_amount': float(round(invoice.discount_amount)),
                       'colspan_value': "4" if is_offer else "3"
                       }

            subject = 'Your shodai order (#' + str(order_instance.order_number) + ') summary'
            from_email, to = 'noreply@shod.ai', request.user.email
            html_customer = get_template('email.html')
            html_content = html_customer.render(content)
            msg = EmailMultiAlternatives(subject, "shodai", from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            """
            To send notification to admin
            """
            if invoice.payment_method == "CASH_ON_DELIVERY":
                payment_method = "Cash on Delivery"
            else:
                payment_method = "Online Payment"
            content = {'user_name': billing_person_name,
                       'user_mobile': invoice.billing_person_mobile_number,
                       'order_number': order_instance.order_number,
                       'platform': "App",
                       'shipping_address': address,
                       'mobile_no': order_instance.contact_number,
                       'order_date': order_instance.created_on.date(),
                       'delivery_date_time': str(order_instance.delivery_date_time.date()) + " ( " + str(slot) + " )",
                       'invoice_number': invoice.invoice_number,
                       'payment_method': payment_method,
                       'sub_total': sub_total,
                       'vat': total_vat,
                       'delivery_charge': delivery_charge,
                       'total': order_instance.order_total_price,
                       'order_details': matrix,
                       'saved_amount': float(round(total_price_without_offer - sub_total)),
                       'colspan_value': "4" if is_offer else "3"
                       }
            admin_subject = 'Order (#' + str(order_instance.order_number) + ') has been placed'
            admin_email = config("TARGET_EMAIL_USER").replace(" ", "").split(',')
            html_admin = get_template('admin_email.html')
            html_content = html_admin.render(content)
            msg_to_admin = EmailMultiAlternatives(admin_subject, "shodai", from_email, admin_email)
            msg_to_admin.attach_alternative(html_content, "text/html")
            msg_to_admin.send()
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
    # this view returns all the products in a order. this has been commented out as it has marged with "Orderdetail" view in get function.

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
                    product['order_product_price_with_vat'] = orderProduct['order_product_price_with_vat']
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
                        data = {
                            'status': "success",
                            # 'payment_id': payment['payment_id'],
                            # 'bill_id': payment['bill_id'],
                            'total_amount': payment['order_total_price'],
                            "currency": "BDT",
                            'created_on': payment['created_on'].strftime("%Y-%m-%d %H:%M:%S"),
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


class CheckPaidStatus(APIView):

    def get(self, request):
        completed_orders = Order.objects.filter(order_status='COM')
        queryset = []
        for o in completed_orders:
            invoice = InvoiceInfo.objects.filter(invoice_number=o.invoice_number)
            if not invoice[0].paid_status:
                queryset.append(invoice)
        print(queryset)
        field_names = ['id', 'invoice_number', 'order_number', 'payment_method']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=payment_check_report.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for i in range(len(queryset)):
            for obj in queryset[i]:
                writer.writerow([getattr(obj, field) for field in field_names])

        return response
