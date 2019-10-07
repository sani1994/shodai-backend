import random

from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from sodai.utils.helper import get_user_object
from sodai.utils.permission import GenericAuth
from userProfile.serializers import UserProfileSerializer, AddressSerializer,UserRegistrationSerializer

from userProfile.models import UserProfile, Address, BlackListedToken

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import IsAuthenticated
from userProfile.models import UserProfile,Otp
from django.db.models import Q
import jwt,json
# from django.contrib.auth import authenticate

from datetime import datetime
# Create your views here.



class UserProfileList(APIView):
    # permission_classes = (IsAuthenticated,)
    # permission_classes = [GenericAuth]

    ## list of UserProfile list

    def get(self, request, format=None):
        is_staff = request.user.is_staff
        user_profile = UserProfile.objects.all()
        # if is_staff:
        #     product = Product.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         product = Product.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         product = Product.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
            
        serializer = UserProfileSerializer(user_profile, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        # if request.user.is_staff:
        #     if serializer.is_valid():
        #         serializer.save(created_by=request.user)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # else:
        #     if request.user.user_type=='RT': # Retailer = RT
        #         if serializer.is_valid():
        #             serializer.save(created_by=request.user)
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserProfileDetail(APIView):
    """
    Retrieve, update and delete Orders
    """
    def get_object(self, request, pk):
        is_staff = request.user.is_staff
        try:
            if is_staff:
                return UserProfile.objects.get(pk=pk)
            else:
                # user_type = request.user.user_type
                # if user_type=='CM':  # Customer = CM
                #     return UserProfile.objects.get(pk=pk)
                # elif user_type=='RT': # Retailer = RT
                #     return UserProfile.objects.get(pk=pk)
                #     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                # elif user_type== 'PD': # Producer = PD
                #     return UserProfile.objects.get(pk=pk)
                #      # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
                return UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user_profile = self.get_object(request, pk)
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        user_profile = self.get_object(request, pk)
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            if request.user==UserProfile.created_by or request.user.is_staff:
                serializer.save(modified_by=request.user)
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        user_profile = self.get_object(request, pk)
        # if request.user==user_profile.created_by or request.user.is_staff:
        user_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddressList(APIView):

    ## list of Address

    def get(self, request, format=None):
        is_staff = request.user.is_staff
        address =Address.objects.all()
        # if is_staff:
        #     address = Address.objects.all()
        # else:
        #     user_type = request.user.user_type
        #     if user_type=='CM':  # Customer = CM
        #         address = Address.objects.filter(created_by=request.user)
        #     elif user_type=='RT': # Retailer = RT
        #         address = Address.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())


        #     elif user_type== 'PD': # Producer = PD
        #         address = Address.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     address = Address.objects.filter(created_by=request.user)
            
        serializer = AddressSerializer(address, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AddressSerializer(data=request.data)
        # if request.user.is_staff:
        #     if serializer.is_valid():
        #         serializer.save(created_by=request.user)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        #
        # else:
        #     if request.user.user_type=='RT': # Retailer = RT
        #         if serializer.is_valid():
        #             serializer.save(created_by=request.user)
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
        if serializer.is_valid():
            serializer.save()
 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class AddressDetail(APIView):
    """
    Retrieve, update and delete Orders
    """
    def get_object(self, request, pk):
        # is_staff = request.user.is_staff
        # try:
        #     if is_staff:
        #         return Address.objects.get(pk=pk)
        #     else:
        #         user_type = request.user.user_type
        #         if user_type=='CM':  # Customer = CM
        #             return Address.objects.get(pk=pk)
        #         elif user_type=='RT': # Retailer = RT
        #             return Address.objects.get(pk=pk)
        #             # address = Address.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         elif user_type== 'PD': # Producer = PD
        #             return Address.objects.get(pk=pk)
        #              # address = Address.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         return Address.objects.get(pk=pk)
        try:
            return Address.objects.get(pk=pk)
        except Address.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        address = self.get_object(request, pk)
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk, format=None):
        address = self.get_object(request, pk)
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            # if request.user==address.created_by or request.user.is_staff:
            #     serializer.save(modified_by=request.user)
            #     return Response(serializer.data)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        address = self.get_object(request, pk)
        if request.user==address.created_by or request.user.is_staff:
            address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class UserRegistration(APIView):
#
#     def post(self,request):
#         if not request.data:
#             return Response({'Error': "Please provide data"}, status="400")
#         serializer = UserProfileSerializer(data=request.data)
#
#         if serializer.is_valid:
#             if 'mobile_number' in serializer:
#                 # user = serializer.create['mobile_number']
#                 user_registered = serializer.create()
#
#                 if user_registered:
#                     return JsonResponse({
#                         "message": "User created successfully",
#                         # "user": user,
#                         "status": True,
#                         "status_code": status.HTTP_201_CREATED
#                     }, status=status.HTTP_201_CREATED)
#                 else:
#                     return JsonResponse({
#                         "message": "User creation failed.",
#                         "status": False,
#                         "status_code": status.HTTP_406_NOT_ACCEPTABLE,
#                     }, status=status.HTTP_406_NOT_ACCEPTABLE)




class Login(APIView):

    def post(self,request,*args,**kwargs):
        if not request.data:
            return Response({'Error': "Please provide mobile no/password"}, status="400")

        mobile_number = request.data['mobile_number']
        # email = request.data['email']
        password = request.data['password']
        try:
            user = UserProfile.objects.get( mobile_number = mobile_number)
            print(user)
        except UserProfile.DoesNotExist:
            return Response({'Error': "Invalid email/password"}, status="400")

        if user:
            print(user.password)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                # UserProfile.objects.create()
                # user.objects.create( token = refresh)

                # serializer = UserProfileSerializer(jwt_token=refresh.access_token)
                # serializer.save()
                return JsonResponse({
                    "message": "success",
                    "status": True,
                    "username": user.username,
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    "status_code": status.HTTP_202_ACCEPTED,
                }, status=status.HTTP_202_ACCEPTED)
            else:
                return JsonResponse({
                    "message": "Username, Password did not match!",
                    "status": False,
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                }, status=status.HTTP_401_UNAUTHORIZED)

class Logout(APIView):
    permission_classes = [GenericAuth]
    def post(self,request):
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


class UserRegistration(CreateAPIView):
    models = UserProfile
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


def otp_key(number):
    print("otp_key_func",number)
    if number:
        key = random.randint(999,9999)
        return key
    else:
        return False


class OtpCode(APIView):

    def post(self,request):
        mobile_number = request.data['mobile_number']
        if mobile_number:
            mobile_number = str(mobile_number)
            obj = Otp.objects.filter(mobile_number__exact=mobile_number).first()
            if obj:
                # obj.counter = 0
                # obj.save()
                if obj.count >5 :
                    return Response ({"Status": "Faild",
                                                "details": "OTP sent 5 times. please contact with support"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    key = otp_key(mobile_number)
                    obj.otp_code = key
                    obj.count=obj.count+1
                    obj.save()
                    return  Response({
                        "Status": "Success..!!",
                        "details": "Mobile number: " + str(obj.mobile_number)+ " Otp code: " + str(obj.otp_code)
                    },status=status.HTTP_200_OK)
            else:
                key = otp_key(mobile_number)
                obj = Otp.objects.create(mobile_number=mobile_number,otp_code=key,count=1)
                return Response({
                    "Status": "Success..!!",
                    "details": "Mobile number: " + str(obj.mobile_number) + " Otp code: " + str(obj.otp_code)
                },status=status.HTTP_200_OK)


class OtpVerify(APIView):

    def post(self,request):
        mobile_number = request.data['mobile_number']
        code = request.data['otp_code']
        obj = Otp.objects.filter(mobile_number__exact=mobile_number).first()
        if obj:
            if obj.otp_code == code:
                obj.otp_code = 0
                obj.count = 0
                obj.save()
                return Response({
                    "status": "Varified..!!",
                },status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "Failed..!!",
                },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status": "Invalide..!!",
            }, status=status.HTTP_204_NO_CONTENT)


