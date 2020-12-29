import uuid

from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from bases.views import CustomPageNumberPagination
from order.models import Order, InvoiceInfo, OrderProduct
from product.models import Product
from shodai_admin.serializers import AdminProfileSerializer, OrderListSerializer, OrderDetailSerializer
from sodai.utils.helper import get_user_object
from sodai.utils.permission import AdminAuth
from userProfile.models import UserProfile, BlackListedToken

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response


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
    Get, update and create order
    """

    def get(self, request, id):
        order = get_object_or_404(Order, id=id)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        order = get_object_or_404(Order, id=id)
        delivery_date_time = request.data.get('delivery_date_time', None)
        contact_number = request.data.get('contact_number', None)
        order_status = request.data.get('order_status', None)
        delivery_charge = request.data.get('delivery_charge', None)
        products = request.data.get('products', None)
        invoice = InvoiceInfo.objects.filter(order_number=order).order_by('-created_on')[0]
        billing_person_name = order.user.first_name + " " + order.user.last_name
        if delivery_charge:
            invoice = InvoiceInfo.objects.create(invoice_number="SHD" + str(uuid.uuid4())[:8].upper(),
                                                 billing_person_name=billing_person_name,
                                                 billing_person_email=order.user.email,
                                                 billing_person_mobile_number=order.user.mobile_number,
                                                 delivery_contact_number=order.contact_number,
                                                 delivery_address=order.address.road,
                                                 delivery_date_time=order.delivery_date_time,
                                                 delivery_charge=delivery_charge,
                                                 net_payable_amount=order.order_total_price - invoice.delivery_charge + delivery_charge,
                                                 payment_method=invoice.payment_method,
                                                 order_number=order,
                                                 user=order.user)
        if delivery_date_time or contact_number or order_status:
            serializer = OrderDetailSerializer(order, data=request.data)
            if serializer.is_valid():
                serializer.save()
        if products:
            # Create new Order
            order = Order.objects.create(user=order.user,
                                         # created_by=request.user,
                                         delivery_date_time=order.delivery_date_time,
                                         delivery_place=order.delivery_place,
                                         lat=order.lat,
                                         long=order.long,
                                         order_status="OD",
                                         order_type=order.order_type,
                                         address=order.address,
                                         contact_number=order.contact_number if order.contact_number else order.user.mobile_number
                                         )

            total_vat, total = 0, 0
            for p in products:
                product = Product.objects.get(id=p["product_id"])
                op = OrderProduct.objects.create(product=product,
                                                 order=order,
                                                 order_product_price=product.product_price,
                                                 order_product_qty=p["order_product_qty"])
                total = float(op.order_product_price_with_vat) * op.order_product_qty
                total += total
                vat = float(op.order_product_price_with_vat - op.order_product_price) * op.order_product_qty
                total_vat += vat

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
                                       delivery_address=order.address.road,
                                       delivery_date_time=order.delivery_date_time,
                                       delivery_charge=invoice.delivery_charge,
                                       net_payable_amount=order.order_total_price,
                                       payment_method=invoice.payment_method,
                                       order_number=order,
                                       user=order.user, )
            # created_by=request.user)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
