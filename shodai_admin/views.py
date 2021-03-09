import math
import uuid
from datetime import datetime, timedelta
from random import randint

from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.conf import settings
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
from coupon.models import CouponCode
from offer.models import Offer, CartOffer
from order.models import Order, InvoiceInfo, OrderProduct, DeliveryCharge, TimeSlot, DiscountInfo
from product.models import Product
from shodai_admin.serializers import AdminUserProfileSerializer, OrderListSerializer, OrderDetailSerializer, \
    ProductSearchSerializer, TimeSlotSerializer, CustomerSerializer, DeliveryChargeOfferSerializer
from shodai.utils.helper import get_user_object
from shodai.utils.permission import AdminAuth, IsAdminUserQP
from userProfile.models import UserProfile, BlackListedToken, Address

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from utility.notification import send_sms
from utility.pdf import render_to_pdf

all_order_status = {
    'Ordered': 'OD',
    'Order Accepted': 'OA',
    'Order Ready': 'RE',
    'Order At Delivery': 'OAD',
    'Order Completed': 'COM',
    'Order Cancelled': 'CN'
}


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


class AdminLogout(APIView):
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
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.query_params.get('search')
        sort_by = request.query_params.get('sort_by', '')
        sort_type = request.query_params.get('sort_type', 'dsc')
        date_from = request.query_params.get('date_from', Order.objects.first().created_on)
        date_to = request.query_params.get('date_to', timezone.now())
        order_status = all_order_status.get(request.query_params.get('order_status'))
        if not getattr(Order, sort_by, False):
            sort_by = 'created_on'
        if sort_type != 'asc':
            sort_by = '-' + sort_by
        if isinstance(date_from, str):
            try:
                date_from = timezone.make_aware(datetime.strptime(date_from, "%Y-%m-%d"))
            except Exception:
                date_from = Order.objects.first().created_on
        if isinstance(date_to, str):
            try:
                date_to = timezone.make_aware(datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1))
            except Exception:
                date_to = timezone.now()
        if search and order_status:
            if search.startswith("01") and len(search) == 11:
                queryset = Order.objects.filter(order_status=order_status,
                                                user__mobile_number='+88' + search,
                                                created_on__gte=date_from,
                                                created_on__lt=date_to).order_by(sort_by)
            else:
                queryset = Order.objects.filter(order_status=order_status,
                                                order_number__icontains=search,
                                                created_on__gte=date_from,
                                                created_on__lt=date_to).order_by(sort_by)

        elif search and not order_status:
            if search.startswith("01") and len(search) == 11:
                queryset = Order.objects.filter(user__mobile_number='+88' + search,
                                                created_on__gte=date_from,
                                                created_on__lt=date_to).order_by(sort_by)
            else:
                queryset = Order.objects.filter(order_number__icontains=search,
                                                created_on__gte=date_from,
                                                created_on__lt=date_to).order_by(sort_by)

        elif not search and order_status:
            queryset = Order.objects.filter(order_status=order_status,
                                            created_on__gte=date_from,
                                            created_on__lt=date_to).order_by(sort_by)
        else:
            queryset = Order.objects.filter(created_on__gte=date_from,
                                            created_on__lt=date_to).order_by(sort_by)
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OrderListSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class OrderDetail(APIView):
    permission_classes = [IsAdminUser]
    """
    Get, update order
    """

    def get(self, request, id):
        order = get_object_or_404(Order, id=id)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        data = request.data
        offer_id = data.get('offer_id')
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
            product_list = []
            for item in data['products']:
                is_valid = field_validation(required_fields, item)
                if is_valid and isinstance(item['product_id'], int):
                    if item['product_id'] not in product_list:
                        product_list.append(item['product_id'])
                        product_exist = Product.objects.filter(id=item['product_id'], is_approved=True)
                        if not product_exist or not item['product_quantity']:
                            is_valid = False
                        if is_valid:
                            decimal_allowed = product_exist[0].decimal_allowed
                            if not decimal_allowed and not isinstance(item['product_quantity'], int):
                                is_valid = False
                            elif decimal_allowed and not isinstance(item['product_quantity'], (float, int)):
                                is_valid = False
                        if is_valid and decimal_allowed:
                            item['product_quantity'] = math.floor(item['product_quantity'] * 10 ** 3) / 10 ** 3
                    else:
                        is_valid = False
                else:
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
            delivery_charge = invoice.delivery_charge

            is_delivery_discount = DiscountInfo.objects.filter(discount_type='DC', invoice=invoice)
            delivery_charge_discount = is_delivery_discount[0].discount_amount if is_delivery_discount else 0
            if offer_id and isinstance(offer_id, int):
                today = timezone.now()
                offer = Offer.objects.filter(id=offer_id, offer_types="DD", is_approved=True,
                                             offer_starts_in__lte=today, offer_ends_in__gte=today)
                if offer:
                    cart_offer = CartOffer.objects.get(offer=offer[0])
                    if cart_offer:
                        delivery_charge_without_offer = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
                        delivery_charge = cart_offer.updated_delivery_charge
                        delivery_charge_discount = delivery_charge_without_offer - delivery_charge

            is_coupon_discount = DiscountInfo.objects.filter(discount_type='CP', invoice=invoice)
            coupon_discount = is_coupon_discount[0].discount_amount if is_coupon_discount else 0

            if products_updated:
                if "-" in order.order_number:
                    x = order.order_number.split("-")
                    x[1] = int(x[1]) + 1
                    order_number = x[0] + "-" + str(x[1])
                else:
                    order_number = order.order_number + "-1"

                is_used = Order.objects.filter(order_number=order_number).count()
                if is_used:
                    return Response({
                        "status": "failed",
                        "message": "Invalid request!"
                    }, status=status.HTTP_400_BAD_REQUEST)

                order.order_status = 'CN'
                order.save()

                order = Order.objects.create(user=order.user,
                                             order_number=order_number,
                                             delivery_date_time=delivery_date_time,
                                             delivery_place=order.delivery_place,
                                             lat=order.lat,
                                             long=order.long,
                                             order_status="OA",
                                             address=delivery_address,
                                             contact_number=data['contact_number'],
                                             created_by=request.user)

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

                if coupon_discount:
                    coupon_code = is_coupon_discount[0].coupon
                    if coupon_code.discount_type == 'DP':
                        coupon_discount = round(total * (coupon_code.discount_percent / 100))
                        if coupon_discount > coupon_code.discount_amount_limit:
                            coupon_discount = coupon_code.discount_amount_limit
                    elif coupon_code.discount_type == 'DA':
                        coupon_discount = coupon_code.discount_amount

                order.order_total_price = round(total) + delivery_charge - coupon_discount
                order.total_vat = total_vat
                order.payment_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
                order.bill_id = "SHD" + str(uuid.uuid4())[:8].upper()
                order.note = data['note'][:500]
            else:
                order.order_total_price = order.order_total_price - invoice.delivery_charge + delivery_charge
                order.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
                order.delivery_date_time = delivery_date_time
                order.contact_number = data['contact_number']
                order.order_status = all_order_status[data['order_status']]
                order.address = delivery_address
                order.note = data['note'][:500]
                order.modified_by = request.user

            if products_updated:
                product_discount = total_price - total_op_price
            else:
                is_product_discount = DiscountInfo.objects.filter(discount_type='PD', invoice=invoice)
                product_discount = is_product_discount[0].discount_amount if is_product_discount else 0

            discount_amount = delivery_charge_discount + coupon_discount + product_discount

            if order.user.first_name and order.user.last_name:
                billing_person_name = order.user.first_name + " " + order.user.last_name
            elif order.user.first_name:
                billing_person_name = order.user.first_name
            else:
                billing_person_name = ""
            payment_method = 'CASH_ON_DELIVERY' if products_updated else invoice.payment_method
            new_invoice = InvoiceInfo.objects.create(invoice_number=order.invoice_number,
                                                     billing_person_name=billing_person_name,
                                                     billing_person_email=order.user.email,
                                                     billing_person_mobile_number=order.user.mobile_number,
                                                     delivery_contact_number=order.contact_number,
                                                     delivery_address=delivery_address.road,
                                                     delivery_date_time=order.delivery_date_time,
                                                     delivery_charge=delivery_charge,
                                                     discount_amount=discount_amount,
                                                     net_payable_amount=order.order_total_price,
                                                     payment_method=payment_method,
                                                     order_number=order,
                                                     user=order.user,
                                                     created_by=request.user)
            order.save()

            if coupon_discount:
                DiscountInfo.objects.create(discount_amount=coupon_discount,
                                            discount_type='CP',
                                            discount_description=is_coupon_discount[0].discount_description,
                                            coupon=is_coupon_discount[0].coupon,
                                            invoice=new_invoice)

            if product_discount:
                DiscountInfo.objects.create(discount_amount=product_discount,
                                            discount_type='PD',
                                            discount_description='Product Offer Discount',
                                            invoice=new_invoice)

            if delivery_charge_discount:
                DiscountInfo.objects.create(discount_amount=delivery_charge_discount,
                                            discount_type='DC',
                                            discount_description='Offer ID: {}'.format(offer_id)
                                            if offer_id else is_delivery_discount[0].discount_description,
                                            offer=offer[0] if offer_id else is_delivery_discount[0].offer,
                                            invoice=new_invoice)
            return Response({
                "status": "success",
                "message": "Order updated.",
                "order_id": order.id}, status=status.HTTP_200_OK)


class CreateOrder(APIView):
    permission_classes = [IsAdminUser]
    """
    Create order
    """

    def post(self, request):
        data = request.data
        offer_id = data.get('offer_id', None)
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
            product_list = []
            for item in products:
                is_valid = field_validation(required_fields, item)
                if is_valid and isinstance(item['product_id'], int):
                    if item['product_id'] not in product_list:
                        product_list.append(item['product_id'])
                        product_exist = Product.objects.filter(id=item['product_id'], is_approved=True)
                        if not product_exist or not item['product_quantity']:
                            is_valid = False
                        if is_valid:
                            decimal_allowed = product_exist[0].decimal_allowed
                            if not decimal_allowed and not isinstance(item['product_quantity'], int):
                                is_valid = False
                            elif decimal_allowed and not isinstance(item['product_quantity'], (float, int)):
                                is_valid = False
                        if is_valid and decimal_allowed:
                            item['product_quantity'] = math.floor(item['product_quantity'] * 10 ** 3) / 10 ** 3
                    else:
                        is_valid = False
                else:
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
        delivery_charge_discount = 0
        if offer_id and isinstance(offer_id, int):
            today = timezone.now()
            offer = Offer.objects.filter(id=offer_id, offer_types="DD", is_approved=True,
                                         offer_starts_in__lte=today, offer_ends_in__gte=today)
            if offer:
                cart_offer = CartOffer.objects.get(offer=offer[0])
                if cart_offer:
                    delivery_charge_discount = delivery_charge - cart_offer.updated_delivery_charge
                    delivery_charge = cart_offer.updated_delivery_charge

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

            coupon = CouponCode.objects.create(coupon_code=str(uuid.uuid4())[:6].upper(),
                                               name="Referral Code",
                                               discount_percent=5,
                                               max_usage_count=3,
                                               minimum_purchase_limit=0,
                                               discount_amount_limit=200,
                                               expiry_date=timezone.now() + timedelta(days=90),
                                               discount_type='DP',
                                               coupon_code_type='RC',
                                               created_by=user_instance,
                                               created_on=timezone.now())

            if not settings.DEBUG:
                sms_body = "Dear Customer,\n" + \
                           "We have created an account with temporary password " + \
                           "[{}] based on your order request. ".format(temp_password) + \
                           "Please change your password after login.\n\n" + \
                           "www.shod.ai"
                send_sms(mobile_number=customer["mobile_number"], sms_content=sms_body)
                coupon_sms_body = "Dear Customer,\n" + \
                                  "Congratulations for your Shodai account!\n" + \
                                  "Share this code [{}] with your friends and ".format(coupon.coupon_code) + \
                                  "family to avail them 5% discount on their next purchase and " + \
                                  "receive exciting discount after each successful referral.\n\n" + \
                                  "www.shod.ai"
                send_sms(mobile_number=user_instance.mobile_number, sms_content=coupon_sms_body)

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
                                              created_by=request.user)

        total_vat = total = total_price = total_op_price = 0
        for p in products:
            product = Product.objects.get(id=p["product_id"])
            op = OrderProduct.objects.create(product=product,
                                             order=order_instance,
                                             order_product_qty=p["product_quantity"])
            total_price += float(op.product_price) * op.order_product_qty
            total_op_price += op.order_product_price * op.order_product_qty
            total += float(op.order_product_price_with_vat) * op.order_product_qty
            total_vat += float(op.order_product_price_with_vat - op.order_product_price) * op.order_product_qty

        order_instance.order_total_price = round(total) + delivery_charge
        order_instance.total_vat = total_vat
        order_instance.payment_id = "SHD" + str(uuid.uuid4())[:8].upper()
        order_instance.invoice_number = "SHD" + str(uuid.uuid4())[:8].upper()
        order_instance.bill_id = "SHD" + str(uuid.uuid4())[:8].upper()
        order_instance.note = data['note'][:500]
        order_instance.save()

        billing_person_name = user_instance.first_name + " " + user_instance.last_name
        invoice = InvoiceInfo.objects.create(invoice_number=order_instance.invoice_number,
                                             billing_person_name=billing_person_name,
                                             billing_person_email=user_instance.email,
                                             billing_person_mobile_number=user_instance.mobile_number,
                                             delivery_contact_number=order_instance.contact_number,
                                             delivery_address=delivery_address.road,
                                             delivery_date_time=order_instance.delivery_date_time,
                                             delivery_charge=delivery_charge,
                                             discount_amount=total_price - total_op_price + delivery_charge_discount,
                                             net_payable_amount=order_instance.order_total_price,
                                             payment_method="CASH_ON_DELIVERY",
                                             order_number=order_instance,
                                             user=user_instance,
                                             created_by=request.user)
        if total_price != total_op_price:
            DiscountInfo.objects.create(discount_amount=total_price - total_op_price,
                                        discount_type='PD',
                                        discount_description='Product Offer Discount',
                                        invoice=invoice)
        if delivery_charge_discount > 0:
            DiscountInfo.objects.create(discount_amount=delivery_charge_discount,
                                        discount_type='DC',
                                        discount_description='Offer ID: {}'.format(offer_id),
                                        offer=offer[0],
                                        invoice=invoice)

        return Response({'status': 'success',
                         'message': 'Order placed.',
                         "order_id": order_instance.id}, status=status.HTTP_200_OK)


class ProductSearch(APIView):
    permission_classes = [IsAdminUser]
    """
    Get Product by name
    """

    def get(self, request):
        query = request.query_params.get('query', '')
        product = Product.objects.filter(product_name__icontains=query, is_approved=True)[:20]
        serializer = ProductSearchSerializer(product, many=True)
        if serializer:
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeSlotList(APIView):
    permission_classes = [IsAdminUser]
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
    permission_classes = [IsAdminUser]
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
    permission_classes = [IsAdminUser]
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
    permission_classes = [IsAdminUserQP]
    """
    Get PDF of Invoice by order ID
    """

    def get(self, request, id):
        order = get_object_or_404(Order, id=id)
        product_list = OrderProduct.objects.filter(order=order)
        matrix = []
        is_product_offer = False
        sub_total = 0
        for p in product_list:
            if p.order_product_price != p.product_price:
                is_product_offer = True
                total_by_offer = float(p.order_product_price) * p.order_product_qty
                sub_total += total_by_offer
                col = [p.product.product_name, p.product.product_unit, p.product_price,
                       p.order_product_price, p.order_product_qty, total_by_offer]
            else:
                total = float(p.product_price) * p.order_product_qty
                sub_total += total
                col = [p.product.product_name, p.product.product_unit, p.product_price,
                       "--", p.order_product_qty, total]
            matrix.append(col)

        invoice = InvoiceInfo.objects.filter(invoice_number=order.invoice_number)
        if not invoice:
            return HttpResponse("Not found")
        invoice = invoice[0]

        customer_name = invoice.billing_person_name
        paid_status = invoice.paid_status
        is_coupon_discount = DiscountInfo.objects.filter(discount_type='CP', invoice=invoice)
        coupon_discount = is_coupon_discount[0].discount_amount if is_coupon_discount else 0

        if invoice.payment_method == "CASH_ON_DELIVERY":
            payment_method = "Cash on Delivery"
        else:
            payment_method = "Online Payment"
        data = {
            'customer_name': customer_name,
            'address': order.address,
            'user_email': order.user.email,
            'user_mobile': order.user.mobile_number,
            'order_number': order.order_number,
            'invoice_number': order.invoice_number,
            'created_on': order.created_on,
            'delivery_date': order.delivery_date_time.date(),
            'order_details': matrix,
            'delivery': invoice.delivery_charge,
            'vat': order.total_vat,
            'sub_total': sub_total,
            'total': order.order_total_price,
            'in_words': num2words(order.order_total_price),
            'payment_method': payment_method if paid_status else 'Cash on Delivery',
            'paid_status': paid_status,
            'is_offer': is_product_offer,
            'coupon_discount': coupon_discount,
            'note': order.note if order.note else None,
            'colspan_value': "4" if is_product_offer else "3",
            'downloaded_on': datetime.now().replace(microsecond=0)
        }
        pdf = render_to_pdf('pdf/invoice.html', data)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "invoice_of_order_%s.pdf" % order.order_number
        content = "inline; filename=%s" % filename
        response['Content-Disposition'] = content
        return response


class OrderNotification(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        if isinstance(data.get('order_id'), int) and data.get('notify_type') in ['placed', 'updated']:
            order_instance = get_object_or_404(Order, id=data['order_id'])
            invoices = InvoiceInfo.objects.filter(order_number=order_instance).order_by('-created_on')
            if data['notify_type'] == 'updated' and len(invoices) > 1 and \
                    invoices[0].net_payable_amount == invoices[1].net_payable_amount:
                pass
            else:
                if data['notify_type'] == 'updated':
                    customer_subject = 'Your shodai order (#' + str(order_instance.order_number) + ') has been updated'
                    admin_subject = 'Order (#' + str(order_instance.order_number) + ') has been updated'
                elif data['notify_type'] == 'placed':
                    customer_subject = 'Your shodai order (#' + str(order_instance.order_number) + ') summary'
                    admin_subject = 'Order (#' + str(order_instance.order_number) + ') has been placed'
                invoice = invoices[0]
                delivery_charge = DeliveryCharge.objects.get().delivery_charge_inside_dhaka
                delivery_charge_discount = delivery_charge - invoice.delivery_charge
                client_name = invoice.billing_person_name
                product_list = OrderProduct.objects.filter(order__pk=data['order_id'])
                matrix = []
                is_offer = False
                sub_total = 0
                for p in product_list:
                    if p.order_product_price != p.product_price:
                        is_offer = True
                        total_by_offer = float(p.order_product_price) * p.order_product_qty
                        sub_total += total_by_offer
                        col = [p.product.product_name, p.product.product_unit, p.product_price,
                               p.order_product_price, p.order_product_qty, total_by_offer]
                    else:
                        total = float(p.product_price) * p.order_product_qty
                        sub_total += total
                        col = [p.product.product_name, p.product.product_unit, p.product_price,
                               "--", p.order_product_qty, total]
                    matrix.append(col)

                time = TimeSlot.objects.get(time=timezone.localtime(order_instance.delivery_date_time).time())
                if time:
                    time_slot = time
                else:
                    time_slot = TimeSlot.objects.get(id=1)
                is_coupon_discount = DiscountInfo.objects.filter(discount_type='CP', invoice=invoice)
                coupon_discount = is_coupon_discount[0].discount_amount if is_coupon_discount else 0

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
                           'is_product_discount': is_offer,
                           'coupon_discount': coupon_discount,
                           'delivery_charge_discount': delivery_charge_discount,
                           'saved_amount': invoice.discount_amount,
                           'note': order_instance.note if order_instance.note else None,
                           'colspan_value': "4" if is_offer else "3"}

                from_email, to = 'noreply@shod.ai', order_instance.user.email
                html_customer = get_template('email.html')
                html_content = html_customer.render(content)
                msg = EmailMultiAlternatives(customer_subject, 'shodai', from_email, [to])
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
                           'platform': "Admin",
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
                           'is_product_discount': is_offer,
                           'coupon_discount': coupon_discount,
                           'delivery_charge_discount': delivery_charge_discount,
                           'saved_amount': invoice.discount_amount,
                           'note': order_instance.note if order_instance.note else None,
                           'colspan_value': "4" if is_offer else "3"
                           }

                admin_email = config("TARGET_EMAIL_USER").replace(" ", "").split(',')
                html_admin = get_template('admin_email.html')
                html_content = html_admin.render(content)
                msg_to_admin = EmailMultiAlternatives(admin_subject, 'shodai', from_email, admin_email)
                msg_to_admin.attach_alternative(html_content, "text/html")
                msg_to_admin.send()
            return Response({
                "status": "success",
                "message": "request received."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failed",
                "message": "Invalid request!"
            }, status=status.HTTP_400_BAD_REQUEST)


class DeliveryChargeOfferList(APIView):
    permission_classes = [IsAdminUser]
    """
    Get All Offers with offer_types DD
    """

    def get(self, request):
        today = timezone.now()
        offers = Offer.objects.filter(offer_types="DD", is_approved=True, offer_starts_in__lte=today,
                                      offer_ends_in__gte=today)
        serializer = DeliveryChargeOfferSerializer(offers, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
