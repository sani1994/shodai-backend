import random

from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny

from sodai.utils.helper import get_user_object
from sodai.utils.permission import GenericAuth
from userProfile.serializers import UserProfileSerializer, AddressSerializer,UserRegistrationSerializer,RetailerRegistrationSreializer

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


class UserProfileList(APIView):             # this view returns list of user and create user
    # permission_classes = (IsAuthenticated,)
    permission_classes = [GenericAuth]

    ## list of UserProfile list

    def get(self, request, format=None):
        # is_staff = request.user.is_staff
        user_profile = UserProfile.objects.all()
        # if is_staff:
        #     # user = UserProfile.objects.all()
        #     return Response(user_profile)
        # else:
        user_type = request.user.user_type
        if user_type=='CM' or user_type == 'RT' or user_type=='PD':                 # Customer = CM Retailer = RT
            user_obj = UserProfile.objects.filter(id=request.user.id, is_approved=True).get() # takes only requestd users object
            serializer = UserProfileSerializer(user_obj)
            return Response(serializer.data,status=status.HTTP_200_OK)
        # elif user_type=='RT': # Retailer = RT
        #     product = UserProfile.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        else:
            if user_type == 'SF':                   # takes all users object
                serializer = UserProfileSerializer(user_profile, many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
        return Response ({"status": "Invalid request"},status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetail(APIView):

    def get(self, request, id):
        user_profile = get_object_or_404(UserProfile,id = id)
        if request.user == user_profile:
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Un-authorized request'},status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, id ):
        user_profile = get_object_or_404(UserProfile, id=id)
        if request.user==user_profile or request.user.is_staff:
            serializer = UserProfileSerializer(user_profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'Un-authorized request'},status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, id):
        user_profile = get_object_or_404(UserProfile, id = id)
        if request.user==user_profile or request.user.is_staff:
            user_profile.delete()
        return Response({'User Deleted'},status=status.HTTP_204_NO_CONTENT)


class AddressList(APIView):         # get address list and create new address
    permission_classes = [GenericAuth]

    def get(self,request):
        address = Address.objects.all()
        user_type = request.user.user_type
        if address:
            serializer = AddressSerializer(address,many=True)
            if user_type == 'SF':
                return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({"Status": "No data to show"},status=status.HTTP_204_NO_CONTENT)

    def post(self, request, format=None):
        serializer = AddressSerializer(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


class AddressDetail(APIView):           #get address with address id, update and delete
    """
    Retrieve, update and delete Orders
    """
    def get(self, request, id, format=None):
        address = get_object_or_404(Address,id = id)
        serializer = AddressSerializer(address)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        address = get_object_or_404(Address,id = id)
        serializer = AddressSerializer(address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self, request, id, format=None):
        address = get_object_or_404(Address, id=id)
        address.delete()
        return Response({'Delete Successful..!!'},status=status.HTTP_200_OK)


class Login(APIView):           #login with mobile number and passwrd

    def post(self,request):
        if not request.data:
            return Response({'Error': "Please provide mobile no/password"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserProfile.objects.get( mobile_number = request.data['mobile_number'])
        except UserProfile.DoesNotExist:
            return Response({'Error': "Invalid email/password"}, status=status.HTTP_400_BAD_REQUEST)

        if user.user_type == 'CM':  # if user type is customer no need to approve from admin panel. it will be automatically approve here.
            if not user.is_approved:
                user.is_approved = True
                user.save()

        if user.is_approved:            #check weather user is approved or not.
            if user:
                if user.check_password(request.data['password']):
                    refresh = RefreshToken.for_user(user)
                    return JsonResponse({
                        "message": "success",
                        "status": True,
                        "user_type":user.user_type,
                        "user_id": user.id,
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
        return Response({'status: Profile request is waiting for approval'},status=status.HTTP_406_NOT_ACCEPTABLE)


class Logout(APIView):          #logout
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


class UserRegistration(CreateAPIView):              #user registration class
    permission_classes = (AllowAny,)
    models = UserProfile
    serializer_class = UserRegistrationSerializer


def otp_key(number):            #generate OTP code
    if number:
        key = random.randint(999,9999)
        return key
    else:
        return False


class OtpCode(APIView):             #OTP code class to generate OTP code

    def post(self,request):
        mobile_number = request.data['mobile_number']
        if mobile_number:
            mobile_number = str(mobile_number)
            obj = Otp.objects.get(mobile_number=mobile_number)
            if obj:
                # obj.counter = 0
                # obj.save()
                if obj.count >5 :     # if otp is sent more then 5 times it will block the user
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


class OtpVerify(APIView):               # to varify otp code against a number

    def post(self,request):
        mobile_number = request.data['mobile_number']
        code = request.data['otp_code']
        obj = Otp.objects.get(mobile_number=mobile_number)
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


class RetailerRegistration(APIView):                #Retailer regerstration class

    def post(self,request):
        if request.data:
            serializer = RetailerRegistrationSreializer(data=request.data,context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return  Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "No content"}, status=status.HTTP_204_NO_CONTENT)
