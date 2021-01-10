import uuid
from datetime import datetime
from random import randint

from django.db import IntegrityError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from bases.views import CustomPageNumberPagination, field_validation, type_validation
from order.models import Order, InvoiceInfo, OrderProduct, DeliveryCharge, TimeSlot
from product.models import Product
from shodai_admin.serializers import AdminProfileSerializer, OrderListSerializer, OrderDetailSerializer, \
    ProductSearchSerializer, TimeSlotSerializer, CustomerSerializer
from sodai.utils.helper import get_user_object
from sodai.utils.permission import AdminAuth
from userProfile.models import UserProfile, BlackListedToken, Address

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from utility.notification import send_sms


class AdminLogin(APIView):

    def post(self, request):
        data = request.data
        if 'mobile_number' not in data:
            return JsonResponse({
                "message": "Mobile Number is required!",
                "status": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
            }, status=status.HTTP_400_BAD_REQUEST)
        if 'password' not in data:
            return JsonResponse({
                "message": "Password is required!",
                "status": False,
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
                if not user.is_staff:
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


class Logout(APIView):  # logout
    permission_classes = [AdminAuth]

    def post(self, request):
        user = get_user_object(username=request.user.username)
        try:
            BlackListedToken.objects.create(
                token=request.headers['Authorization'].split(' ')[1],
                user=user)
        except IntegrityError:
            return JsonResponse({
                "message": "Invalid or expired token!",
                "status": False,
                "status_code": status.HTTP_401_UNAUTHORIZED
            })
        finally:
            return JsonResponse({
                "message": "successfully logged out!",
                "status": True,
                "status_code": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)


class AdminProfileDetail(APIView):
    permission_classes = [AdminAuth]

    def get(self, request, id):
        user_profile = get_object_or_404(UserProfile, id=id)
        if request.user == user_profile:
            serializer = AdminProfileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Un-authorized request'}, status=status.HTTP_401_UNAUTHORIZED)


# Testing REST_FRAMEWORK Token Authentication
class LoginTest(APIView):

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


class LogoutTest(APIView):
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
                queryset = Order.objects.filter(id__icontains=search).order_by(sort_by)
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

        # *** validation started ***
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
        if not is_valid or not order or not data['delivery_address']:
            return Response({
                "status": "failed",
                "message": "Invalid request!"
            }, status=status.HTTP_400_BAD_REQUEST)
        # --- validation ended ---
        else:
            order = order[0]
            products = data['products']
            op = OrderProduct.objects.filter(order=order)
            order_products = []
            for o in op:
                c = {'product_id': o.product.id, 'product_quantity': o.order_product_qty}
                order_products.append(c)

            invoice = InvoiceInfo.objects.filter(order_number=order).order_by('-created_on')[0]
            billing_person_name = order.user.first_name + " " + order.user.last_name

            if data["delivery_address"] != invoice.delivery_address:
                delivery_address = Address.objects.create(road=data["delivery_address"],
                                                          city="Dhaka",
                                                          district="Dhaka",
                                                          country="Bangladesh",
                                                          user=order.user)
            else:
                delivery_address = order.address

            product_changed = False
            if len(order_products) != len(products):
                product_changed = True
            if not product_changed:
                for i in products:
                    if i not in order_products:
                        product_changed = True
            if not product_changed:
                # Create new Invoice update Order
                invoice = InvoiceInfo.objects.create(invoice_number="SHD" + str(uuid.uuid4())[:8].upper(),
                                                     billing_person_name=billing_person_name,
                                                     billing_person_email=order.user.email,
                                                     billing_person_mobile_number=order.user.mobile_number,
                                                     delivery_contact_number=data['contact_number'],
                                                     delivery_address=delivery_address.road,
                                                     delivery_date_time=delivery_date_time,
                                                     delivery_charge=invoice.delivery_charge,
                                                     discount_amount=invoice.discount_amount,
                                                     net_payable_amount=order.order_total_price,
                                                     payment_method=invoice.payment_method,
                                                     order_number=order,
                                                     user=order.user,
                                                     # created_by=request.user
                                                     )

                # order.modified_by = request.user
                order.invoice_number = invoice.invoice_number
                order.delivery_date_time = delivery_date_time
                order.contact_number = data['contact_number']
                order.order_status = all_order_status[data['order_status']]
                order.address = delivery_address
                order.save()
            if product_changed:
                # Create new Order and Invoice
                order.order_status = 'CN'
                order.save()
                order = Order.objects.create(user=order.user,
                                             # created_by=request.user,
                                             delivery_date_time=delivery_date_time,
                                             delivery_place=order.delivery_place,
                                             lat=order.lat,
                                             long=order.long,
                                             order_status="OD",
                                             order_type=order.order_type,
                                             address=delivery_address,
                                             contact_number=data['contact_number']
                                             )

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
                order.save()

                # Create new InvoiceInfo Instance
                InvoiceInfo.objects.create(invoice_number=order.invoice_number,
                                           billing_person_name=billing_person_name,
                                           billing_person_email=order.user.email,
                                           billing_person_mobile_number=order.user.mobile_number,
                                           delivery_contact_number=order.contact_number,
                                           delivery_address=delivery_address.road,
                                           delivery_date_time=order.delivery_date_time,
                                           delivery_charge=invoice.delivery_charge,
                                           discount_amount=total_price - total_op_price,
                                           net_payable_amount=order.order_total_price,
                                           payment_method=invoice.payment_method,
                                           order_number=order,
                                           user=order.user,
                                           # created_by=request.user
                                           )
            return Response({
                "status": "success",
                "message": "Order updated successfully."
            }, status=status.HTTP_200_OK)


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
                    if not product_exist:
                        is_valid = False
                if not is_valid or not item['product_quantity']:
                    is_valid = False
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

        delivery_address = Address.objects.create(road=data["delivery_address"],
                                                  city="Dhaka",
                                                  district="Dhaka",
                                                  country="Bangladesh",
                                                  user=user_instance)

        order_instance = Order.objects.create(user=user_instance,
                                              delivery_date_time=delivery_date_time,
                                              delivery_place="Dhaka",
                                              lat=23.7733,
                                              long=90.3548,
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
                         'message': 'Order placed.'}, status=status.HTTP_200_OK)


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
