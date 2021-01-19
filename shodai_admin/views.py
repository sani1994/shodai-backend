import uuid
from datetime import datetime
from random import randint

from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.core.validators import validate_email
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.utils.crypto import get_random_string
from num2words import num2words
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from bases.views import CustomPageNumberPagination, field_validation, type_validation
from offer.models import OfferProduct
from order.models import Order, InvoiceInfo, OrderProduct, DeliveryCharge, TimeSlot
from product.models import Product
from shodai_admin.serializers import AdminUserProfileSerializer, OrderListSerializer, OrderDetailSerializer, \
    ProductSearchSerializer, TimeSlotSerializer, CustomerSerializer
from sodai.utils.helper import get_user_object
from sodai.utils.permission import AdminAuth
from userProfile.models import UserProfile, BlackListedToken, Address

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from utility.notification import send_sms
from utility.pdf import render_to_pdf


class AdminLogin(APIView):

    def post(self, request):
        data = request.data
        if 'mobile_number' or 'password' not in data:
            return JsonResponse({
                "status": "failed",
                "message": "Invalid request!",
                "status_code": status.HTTP_400_BAD_REQUEST,
            }, status=status.HTTP_400_BAD_REQUEST)

        if 'mobile_number' in data:
            try:
                user = UserProfile.objects.get(mobile_number=request.data['mobile_number'])
            except UserProfile.DoesNotExist:
                user = None

        if user is None:
            return JsonResponse({
                "message": "User does not exist!",
                "status": False,
                "status_code": status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            }, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            if user.check_password(request.data['password']):
                if user.is_staff:
                    refresh = RefreshToken.for_user(user)
                    return JsonResponse({
                        "message": "success",
                        "status": True,
                        "user_type": user.user_type,
                        "user_id": user.id,
                        "username": user.username,
                        'refresh_token': str(refresh),
                        'access_token': str(refresh.access_token),
                        "status_code": status.HTTP_202_ACCEPTED,
                    }, status=status.HTTP_202_ACCEPTED)
                else:
                    return JsonResponse({
                        "message": "Unauthorized access!",
                        "status": False,
                        "status_code": status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
                    }, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                return JsonResponse({
                    "message": "Password did not match!",
                    "status": False,
                    "status_code": status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
                }, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)


class AdminLogout(APIView):  # logout
    permission_classes = [AdminAuth]

    def post(self, request):
        user = get_user_object(username=request.user.username)
        try:
            BlackListedToken.objects.create(
                token=request.headers['Authorization'].split(' ')[1],
                user=user)
        except IntegrityError:
            return JsonResponse({
                "status": "failed",
                "message": "Invalid or expired token!",
                "status_code": status.HTTP_401_UNAUTHORIZED
            })
        finally:
            return JsonResponse({
                "status": "success",
                "message": "successfully logged out!",
                "status_code": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)


class AdminUserProfile(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        serializer = AdminUserProfileSerializer(request.user)
        if serializer:
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserRegistration(APIView):

    def post(self, request):
        data = request.data
        required_fields = ['name',
                           'mobile_number',
                           'email',
                           'password']
        is_valid = field_validation(required_fields, data)

        if is_valid:
            string_fields = [data['name'],
                             data['mobile_number'],
                             data['email'],
                             data['password']]
            is_valid = type_validation(string_fields, str)
        if is_valid and len(data["mobile_number"]) == 14 and \
                data["mobile_number"].startswith('+8801') and data["mobile_number"][1:].isdigit():
            pass
        else:
            is_valid = False
        if is_valid and data["email"]:
            try:
                validate_email(data["email"])
            except Exception:
                is_valid = False
        if not is_valid or not data['name'] or not data['password']:
            return Response({
                "status": "failed",
                "message": "Invalid request!"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                mobile_user_instance = UserProfile.objects.get(mobile_number=data["mobile_number"])
            except UserProfile.DoesNotExist:
                mobile_user_instance = None

            try:
                email_user_instance = UserProfile.objects.get(email=data["email"])
            except UserProfile.DoesNotExist:
                email_user_instance = None

            if not mobile_user_instance and not email_user_instance:
                user_instance = UserProfile.objects.create(username=data["mobile_number"],
                                                           first_name=data["name"],
                                                           last_name="",
                                                           email=data["email"],
                                                           mobile_number=data["mobile_number"],
                                                           user_type="CM",
                                                           created_on=timezone.now(),
                                                           verification_code=randint(100000, 999999),
                                                           is_approved=True)
                user_instance.set_password(data['password'])
                user_instance.save()
                return Response({
                    "status": "success",
                    "message": "User Created."}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "failed",
                    "message": "Mobile or Email Already Exists!"
                }, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):

    def post(self, request):
        data = request.data
        if 'username' not in data or 'password' not in data:
            return Response({
                "status": "failed",
                "message": "Invalid request!"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=data['username'], password=data['password'])

        if not user or not user.is_staff:
            return Response({
                "status": "failed",
                "message": "Invalid username or password!"
            }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful.",
                "status": "success",
                "username": user.username,
                'access_token': token.key,
            }, status=status.HTTP_200_OK)


class Logout(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        Token.objects.get(key=request.auth).delete()
        return Response({
            "status": "success",
            "message": "Logout successful."
        }, status=status.HTTP_200_OK)


class TokenViewAPITest(APIView):  # Sample API test with Authentication
    permission_classes = [IsAdminUser]

    def get(self, request):
        if not request.user.has_perms(['authtoken.view_token']):
            return Response({
                "status": "failed",
                "message": "You are not authorized to do this action!"
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = Token.objects.get(user=request.user)
        data = {'token': token.key}
        return Response(data, status=status.HTTP_200_OK)


class OrderList(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.query_params.get('search', None)
        sort_by = request.query_params.get('sort_by', '')
        sort_type = request.query_params.get('sort_type', 'dsc')
        if not getattr(Order, sort_by, False):
            sort_by = 'created_on'
        if sort_type != 'asc':
            sort_by = '-' + sort_by
        if search:
            if search.startswith("01") and len(search) == 11:
                queryset = Order.objects.filter(user__mobile_number='+88' + search).order_by(sort_by)
            else:
                queryset = Order.objects.filter(order_number__icontains=search).order_by(sort_by)
        else:
            queryset = Order.objects.all().order_by(sort_by)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OrderListSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class OrderDetail(APIView):
    # permission_classes = [IsAdminUser]
    """
    Get, update order
    """

    def get(self, request, id):
        order = get_object_or_404(Order, id=id)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        data = request.data
        all_order_status = {
            'Ordered': 'OD',
            'Order Accepted': 'OA',
            'Order Ready': 'RE',
            'Order At Delivery': 'OAD',
            'Order Completed': 'COM',
            'Order Cancelled': 'CN',
        }

        required_fields = ['delivery_date',
                           'delivery_time_slot_id',
                           'delivery_address',
                           'contact_number',
                           'order_status',
                           'products',
                           'note']
        is_valid = field_validation(required_fields, data)

        if is_valid:
            string_fields = [data['delivery_date'],
                             data['delivery_address'],
                             data['contact_number'],
                             data['order_status'],
                             data['note']]
            is_valid = type_validation(string_fields, str)

        if is_valid and isinstance(data['products'], list) and data['products']:
            required_fields = ['product_id', 'product_quantity']
            for item in data['products']:
                is_valid = field_validation(required_fields, item)
                if is_valid:
                    integer_fields = [item['product_id'],
                                      item['product_quantity']]
                    is_valid = type_validation(integer_fields, int)
                if is_valid:
                    product_exist = Product.objects.filter(id=item['product_id'], is_approved=True)
                    if not product_exist or not item['product_quantity']:
                        is_valid = False
                if not is_valid:
                    break
        else:
            is_valid = False

        if is_valid and isinstance(data['delivery_time_slot_id'], int):
            time = TimeSlot.objects.filter(id=data['delivery_time_slot_id'])
            if time:
                delivery_date_time = data['delivery_date'] + str(time[0].time)
                try:
                    delivery_date_time = timezone.make_aware(datetime.strptime(delivery_date_time, "%Y-%m-%d%H:%M:%S"))
                except Exception:
                    is_valid = False
            else:
                is_valid = False
        else:
            is_valid = False

        if is_valid and len(data["contact_number"]) == 14 and \
                data["contact_number"].startswith('+8801') and data["contact_number"][1:].isdigit():
            pass
        else:
            is_valid = False

        order = Order.objects.filter(id=id)
        if not is_valid or not order or not data['delivery_address'] or data['order_status'] not in all_order_status:
            return Response({
                "status": "failed",
                "message": "Invalid request!"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            order = order[0]
            products = data['products']
            products_updated = True

            if order.order_status == 'COM' or order.order_status == 'CN' or \
                    data['order_status'] == 'Order Completed' or data['order_status'] == 'Order Cancelled':
                products_updated = False

            if products_updated:
                all_order_products = OrderProduct.objects.filter(order=order)
                order_products = []
                for item in all_order_products:
                    product_data = {'product_id': item.product.id,
                                    'product_quantity': item.order_product_qty}
                    order_products.append(product_data)
                if len(order_products) == len(products):
                    for i in products:
                        if i not in order_products:
                            break
                    else:
                        products_updated = False

            if not order.address or data["delivery_address"] != order.address.road:
                address = Address.objects.filter(road=data["delivery_address"])
                if not address:
                    delivery_address = Address.objects.create(road=data["delivery_address"],
                                                              city="Dhaka",
                                                              district="Dhaka",
                                                              country="Bangladesh",
                                                              zip_code="",
                                                              user=order.user)
                else:
                    delivery_address = address[0]
            else:
                delivery_address = order.address

            invoice = InvoiceInfo.objects.filter(order_number=order).order_by('-created_on')[0]
            billing_person_name = order.user.first_name + " " + order.user.last_name
            if products_updated:
                if "-" in order.order_number:
                    x = order.order_number.split("-")
                    x[1] = int(x[1]) + 1
                    order_number = x[0] + "-" + str(x[1])
                else:
                    order_number = order.order_number + "-1"

                try:
                    new_order = Order.objects.create(user=order.user,
                                                     order_number=order_number,
                                                     delivery_date_time=delivery_date_time,
                                                     delivery_place=order.delivery_place,
                                                     lat=order.lat,
                                                     long=order.long,
                                                     order_status="OA",
                                                     address=delivery_address,
                                                     contact_number=data['contact_number'],
                                                     # created_by=request.user,
                                                     )
                    order.order_status = 'CN'
                    order.save()
                    order = new_order
                except Exception:
                    return Response({
                        "status": "failed",
                        "message": "Invalid request!"
                    }, status=status.HTTP_400_BAD_REQUEST)

                total_vat = total = total_price = total_op_price = 0
                for p in products:
                    product = Product.objects.get(id=p["product_id"])
                    op = OrderProduct.objects.create(product=product,
                                                     order=order,
                                                     order_product_qty=p["product_quantity"])
                    total_price += float(product.product_price) * op.order_product_qty
                    total_op_price += op.order_product_price * op.order_product_qty
                    total += float(op.order_product_price_with_vat) * op.order_product_qty
                    total_vat += float(op.order_product_price_with_vat - op.order_product_price) * op.order_product_qty

                order.order_total_price = total + invoice.delivery_charge
                order.total_vat = total_vat
                order.payment_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
                order.bill_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order.note = data['note']
            else:
                order.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
                order.delivery_date_time = delivery_date_time
                order.contact_number = data['contact_number']
                order.order_status = all_order_status[data['order_status']]
                order.address = delivery_address
                order.note = data['note']
                # order.modified_by = request.user

            discount_amount = total_price - total_op_price if products_updated else invoice.discount_amount
            payment_method = 'CASH_ON_DELIVERY' if products_updated else invoice.payment_method
            InvoiceInfo.objects.create(invoice_number=order.invoice_number,
                                       billing_person_name=billing_person_name,
                                       billing_person_email=order.user.email,
                                       billing_person_mobile_number=order.user.mobile_number,
                                       delivery_contact_number=order.contact_number,
                                       delivery_address=delivery_address.road,
                                       delivery_date_time=order.delivery_date_time,
                                       delivery_charge=invoice.delivery_charge,
                                       discount_amount=discount_amount,
                                       net_payable_amount=order.order_total_price,
                                       payment_method=payment_method,
                                       order_number=order,
                                       user=order.user,
                                       # created_by=request.user
                                       )
            order.save()
            return Response({
                "status": "success",
                "message": "Order updated.",
                "order_id": order.id}, status=status.HTTP_200_OK)


class CreateOrder(APIView):
    # permission_classes = [IsAdminUser]
    """
    Create order
    """

    def post(self, request):
        data = request.data
        required_fields = ['delivery_date',
                           'delivery_time_slot_id',
                           'delivery_address',
                           'contact_number',
                           'customer',
                           'products',
                           'note']
        is_valid = field_validation(required_fields, data)

        if is_valid:
            customer = data['customer']
            products = data['products']

            string_fields = [data['delivery_date'],
                             data['delivery_address'],
                             data['contact_number'],
                             data['note']]
            is_valid = type_validation(string_fields, str)

        if is_valid:
            required_fields = ['name', 'mobile_number', 'email']
            is_valid = field_validation(required_fields, customer)
            if is_valid:
                string_fields = [customer["name"],
                                 customer["mobile_number"],
                                 customer["email"]]
                is_valid = type_validation(string_fields, str)
            if is_valid and len(customer["mobile_number"]) == 14 and \
                    customer["mobile_number"].startswith('+8801') and customer["mobile_number"][1:].isdigit():
                pass
            else:
                is_valid = False
            if is_valid and customer["email"]:
                try:
                    validate_email(customer["email"])
                except Exception:
                    is_valid = False

        if is_valid and isinstance(products, list) and products:
            required_fields = ['product_id', 'product_quantity']
            for item in products:
                is_valid = field_validation(required_fields, item)
                if is_valid:
                    integer_fields = [item['product_id'],
                                      item['product_quantity']]
                    is_valid = type_validation(integer_fields, int)
                if is_valid:
                    product_exist = Product.objects.filter(id=item['product_id'], is_approved=True)
                    if not product_exist or not item['product_quantity']:
                        is_valid = False
                if not is_valid:
                    break
        else:
            is_valid = False

        if is_valid and isinstance(data['delivery_time_slot_id'], int):
            time = TimeSlot.objects.filter(id=data['delivery_time_slot_id'])
            if time:
                delivery_date_time = data['delivery_date'] + str(time[0].time)
                try:
                    delivery_date_time = timezone.make_aware(datetime.strptime(delivery_date_time, "%Y-%m-%d%H:%M:%S"))
                except Exception:
                    is_valid = False
            else:
                is_valid = False
        else:
            is_valid = False

        if is_valid and len(data["contact_number"]) == 14 and \
                data["contact_number"].startswith('+8801') and data["contact_number"][1:].isdigit():
            pass
        else:
            is_valid = False

        if not is_valid or not data['delivery_address']:
            return Response({
                "status": "failed",
                "message": "Invalid request!"}, status=status.HTTP_400_BAD_REQUEST)

        delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
        try:
            user_instance = UserProfile.objects.get(mobile_number=customer["mobile_number"])
        except UserProfile.DoesNotExist:
            user_instance = None

        if not user_instance:
            user_instance = UserProfile.objects.create(username=customer["mobile_number"],
                                                       first_name=customer["name"],
                                                       last_name="",
                                                       email=customer["email"],
                                                       mobile_number=customer["mobile_number"],
                                                       user_type="CM",
                                                       created_on=timezone.now(),
                                                       verification_code=randint(100000, 999999),
                                                       is_approved=True)
            temp_password = get_random_string(length=6)
            user_instance.set_password(temp_password)
            user_instance.save()

            # sms_body = f"Dear " + customer["name"] + \
            #            ",\r\nWe have created a account with temporary password [" + temp_password + \
            #            "] based on your order request." \
            #            "\r\n[N.B:Please change your password after login]"
            # send_sms(mobile_number=customer["mobile_number"], sms_content=sms_body)

        address = Address.objects.filter(road=data["delivery_address"])
        if not address:
            delivery_address = Address.objects.create(road=data["delivery_address"],
                                                      city="Dhaka",
                                                      district="Dhaka",
                                                      country="Bangladesh",
                                                      zip_code="",
                                                      user=user_instance)
        else:
            delivery_address = address[0]

        order_instance = Order.objects.create(user=user_instance,
                                              delivery_date_time=delivery_date_time,
                                              delivery_place="Dhaka",
                                              lat=23.7733,
                                              long=90.3548,
                                              order_status="OA",
                                              contact_number=data["contact_number"],
                                              address=delivery_address,
                                              # created_by=request.user,
                                              )

        total_vat = total = total_price = total_op_price = 0
        for p in products:
            product = Product.objects.get(id=p["product_id"])
            op = OrderProduct.objects.create(product=product,
                                             order=order_instance,
                                             order_product_qty=p["product_quantity"])
            total_price += float(product.product_price) * op.order_product_qty
            total_op_price += op.order_product_price * op.order_product_qty
            total += float(op.order_product_price_with_vat) * op.order_product_qty
            total_vat += float(op.order_product_price_with_vat - op.order_product_price) * op.order_product_qty

        order_instance.order_total_price = total + delivery_charge
        order_instance.total_vat = total_vat
        order_instance.payment_id = "SHD" + str(uuid.uuid4())[:8].upper()
        order_instance.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
        order_instance.bill_id = "SHD" + str(uuid.uuid4())[:8].upper()
        order_instance.note = data['note']
        order_instance.save()

        billing_person_name = user_instance.first_name + " " + user_instance.last_name
        InvoiceInfo.objects.create(invoice_number=order_instance.invoice_number,
                                   billing_person_name=billing_person_name,
                                   billing_person_email=user_instance.email,
                                   billing_person_mobile_number=user_instance.mobile_number,
                                   delivery_contact_number=order_instance.contact_number,
                                   delivery_address=delivery_address.road,
                                   delivery_date_time=order_instance.delivery_date_time,
                                   delivery_charge=delivery_charge,
                                   discount_amount=total_price - total_op_price,
                                   net_payable_amount=order_instance.order_total_price,
                                   payment_method="CASH_ON_DELIVERY",
                                   order_number=order_instance,
                                   user=user_instance,
                                   # created_by=request.user,
                                   )

        return Response({'status': 'success',
                         'message': 'Order placed.',
                         "order_id": order_instance.id}, status=status.HTTP_200_OK)


class ProductSearch(APIView):
    # permission_classes = [IsAdminUser]
    """
    Get Product by name
    """

    def get(self, request):
        query = request.query_params.get('query', '')
        product = Product.objects.filter(product_name__icontains=query, is_approved=True)[:10]
        serializer = ProductSearchSerializer(product, many=True)
        if serializer:
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeSlotList(APIView):
    # permission_classes = [IsAdminUser]
    """
    Get List of Timeslots
    """

    def get(self, request):
        queryset = TimeSlot.objects.filter(allow=True)
        serializer = TimeSlotSerializer(queryset, many=True)
        if serializer:
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderStatusList(APIView):
    # permission_classes = [IsAdminUser]
    """
    Get All Order Status
    """

    def get(self, request):
        all_order_status = [
            'Ordered',
            'Order Accepted',
            'Order Ready',
            'Order At Delivery',
            'Order Completed',
            'Order Cancelled',
        ]
        return Response({'status': 'success', 'data': all_order_status}, status=status.HTTP_200_OK)


class CustomerSearch(APIView):
    # permission_classes = [IsAdminUser]
    """
    Get List of Customers by mobile number
    """

    def get(self, request):
        query = request.query_params.get('query', '')
        queryset = UserProfile.objects.filter(mobile_number__icontains=query,
                                              user_type="CM")
        serializer = CustomerSerializer(queryset, many=True)
        if serializer:
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceDownloadPDF(APIView):
    # permission_classes = [IsAdminUser]
    """
    Get PDF of Invoice by order ID
    """

    def get(self, request, id):
        order = get_object_or_404(Order, id=id)
        if order:
            product_list = OrderProduct.objects.filter(order=order)
            matrix = []
            for p in product_list:
                today = timezone.now()
                offer_product = OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                                            offer__offer_ends_in__gte=today, product=p.product)

                if offer_product.exists():
                    total = float(offer_product[0].offer_price) * p.order_product_qty
                    col = [p.product.product_name, p.product.product_unit.product_unit, p.order_product_qty,
                           p.product.product_price, offer_product[0].offer_price, total]
                    matrix.append(col)
                else:
                    total = float(p.product.product_price) * p.order_product_qty
                    col = [p.product.product_name, p.product.product_unit.product_unit, p.order_product_qty,
                           p.product.product_price, "--", total]
                    matrix.append(col)
            invoice = InvoiceInfo.objects.filter(invoice_number=order.invoice_number)
            paid_status = invoice[0].paid_status

            if invoice[0].payment_method == "CASH_ON_DELIVERY":
                payment_method = "Cash on Delivery"
            else:
                payment_method = "Online Payment"
            data = {
                'customer_name': order.user.first_name + " " + order.user.last_name,
                'address': order.address,
                'user_email': order.user.email,
                'user_mobile': order.user.mobile_number,
                'order_number': order.order_number,
                'invoice_number': order.invoice_number,
                'created_on': order.created_on,
                'delivery_date': order.delivery_date_time.date(),
                'delivery_time': order.delivery_date_time.time(),
                'order_details': matrix,
                'delivery': invoice[0].delivery_charge,
                'vat': order.total_vat,
                'total': order.order_total_price,
                'in_words': num2words(order.order_total_price),
                'payment_method': payment_method if paid_status else 'Cash on Delivery',
                'paid_status': paid_status,
                'downloaded_on': datetime.now().replace(microsecond=0)
            }
            pdf = render_to_pdf('pdf/invoice.html', data)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "invoice_of_order_%s.pdf" % order.order_number
                content = "inline; filename=%s" % filename
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename=%s" % filename
                response['Content-Disposition'] = content
                return response
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class OrderNotification(APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        if data.get('order_id') and isinstance(data['order_id'], int):
            order_instance = get_object_or_404(Order, id=data['order_id'])
            invoice = InvoiceInfo.objects.filter(invoice_number=order_instance.invoice_number).order_by('-created_on')[0]
            product_list = OrderProduct.objects.filter(order__pk=data['order_id'])
            matrix = []
            total_price_without_offer = 0
            is_offer = False
            for p in product_list:
                total = float(p.product.product_price) * p.order_product_qty
                total_price_without_offer += total
                if p.order_product_price != p.product.product_price:
                    is_offer = True
                    total_by_offer = float(p.order_product_price) * p.order_product_qty
                    col = [p.product.product_name, p.product.product_unit, p.product.product_price,
                           p.order_product_price, int(p.order_product_qty), total_by_offer]
                else:
                    col = [p.product.product_name, p.product.product_unit, p.product.product_price,
                           "--", int(p.order_product_qty), total]
                matrix.append(col)

            time = TimeSlot.objects.get(time=timezone.localtime(order_instance.delivery_date_time).time())
            if time:
                time_slot = time
            else:
                time_slot = TimeSlot.objects.get(id=1)
            delivery_charge = invoice.delivery_charge
            sub_total = order_instance.order_total_price - order_instance.total_vat - delivery_charge
            client_name = order_instance.user.first_name + " " + order_instance.user.last_name

            """
            To send notification to customer
            """

            content = {'user_name': client_name,
                       'order_number': order_instance.order_number,
                       'shipping_address': order_instance.address.road + " " + order_instance.address.city,
                       'mobile_no': order_instance.contact_number,
                       'order_date': order_instance.created_on.date(),
                       'delivery_date_time': str(
                            order_instance.delivery_date_time.date()) + " ( " + time_slot.slot + " )",
                       'sub_total': sub_total,
                       'vat': order_instance.total_vat,
                       'delivery_charge': delivery_charge,
                       'total': order_instance.order_total_price,
                       'order_details': matrix,
                       'is_offer': is_offer,
                       'saved_amount': float(round(total_price_without_offer - sub_total)),
                       'colspan_value': "4" if is_offer else "3"}

            subject = 'Your shodai order (#' + str(order_instance.order_number) + ') summary'
            from_email, to = 'noreply@shod.ai', order_instance.user.email
            html_customer = get_template('email.html')
            html_content = html_customer.render(content)
            msg = EmailMultiAlternatives(subject, 'shodai', from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            """
            To send notification to admin
            """

            if invoice.payment_method == "CASH_ON_DELIVERY":
                payment_method = "Cash on Delivery"
            else:
                payment_method = "Online Payment"
            content = {'user_name': client_name,
                       'user_mobile': order_instance.user.mobile_number,
                       'order_number': order_instance.order_number,
                       'platform': "Website",
                       'shipping_address': order_instance.address.road + " " + order_instance.address.city,
                       'mobile_no': order_instance.contact_number,
                       'order_date': order_instance.created_on.date(),
                       'delivery_date_time': str(
                           order_instance.delivery_date_time.date()) + " ( " + time_slot.slot + " )",
                       'invoice_number': invoice.invoice_number,
                       'payment_method': payment_method,
                       'sub_total': sub_total,
                       'vat': order_instance.total_vat,
                       'delivery_charge': delivery_charge,
                       'total': order_instance.order_total_price,
                       'order_details': matrix,
                       'is_offer': is_offer,
                       'saved_amount': float(round(total_price_without_offer - sub_total)),
                       'colspan_value': "4" if is_offer else "3"
                       }

            admin_subject = 'Order (#' + str(order_instance.order_number) + ') Has Been Placed'
            admin_email = config("TARGET_EMAIL_USER").replace(" ", "").split(',')
            html_admin = get_template('admin_email.html')
            html_content = html_admin.render(content)
            msg_to_admin = EmailMultiAlternatives(admin_subject, 'shodai', from_email, admin_email)
            msg_to_admin.attach_alternative(html_content, "text/html")
            msg_to_admin.send()
            return Response({
                "status": "success",
                "message": "email sent successfully."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failed",
                "message": "Invalid request!"
            }, status=status.HTTP_400_BAD_REQUEST)
