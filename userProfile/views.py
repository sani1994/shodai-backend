import random

from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
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



class UserProfileList(APIView):
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
        if user_type=='CM' or user_type == 'RT' or user_type=='PD':  # Customer = CM Retailer RT
            user_profile = UserProfile.objects.filter(id=request.user.id, is_approved=True)
            serializer = UserProfileSerializer(user_profile, many=True)
            return Response(serializer.data)
        # elif user_type=='RT': # Retailer = RT
        #     product = UserProfile.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        else:
            if user_type == 'SF':
                serializer = UserProfileSerializer(user_profile, many=True)
                return Response(serializer.data)



            # elif user_type== 'PD': # Producer = PD
            #     product = .objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
            # elif user_type== 'SF': # Staff = SF
            #     order = Order.objects.filter(created_by=request.user)
        return Response ({"status": "Invalid request"},status=status.HTTP_400_BAD_REQUEST)
            


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
    # permission_classes = [GenericAuth]
    # """
    # Retrieve, update and delete Orders
    # """
    def get_object(self, request, id):
        # is_staff = request.user.is_staff
        # try:
        #     if is_staff:
        #         return UserProfile.objects.get(pk=pk)
        #     else:
        #         # user_type = request.user.user_type
        #         # if user_type=='CM':  # Customer = CM
        #         #     return UserProfile.objects.get(pk=pk)
        #         # elif user_type=='RT': # Retailer = RT
        #         #     return UserProfile.objects.get(pk=pk)
        #         #     # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         # elif user_type== 'PD': # Producer = PD
        #         #     return UserProfile.objects.get(pk=pk)
        #         #      # order = Order.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
        #         return UserProfile.objects.get(pk=pk)
        # except UserProfile.DoesNotExist:
        #     raise Http404

        user = UserProfile.objects.get(id=id)
        return user

    def get(self, request, id, format=None):
        user_profile = self.get_object(request, id)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def put(self, request, id, format=None):
        user_profile = self.get_object(request, id)
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            # if request.user==UserProfile.created_by or request.user.is_staff:
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        user_profile = self.get_object(request, pk)
        # if request.user==user_profile.created_by or request.user.is_staff:
        user_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddressList(APIView):
    permission_classes = [GenericAuth]
    ## list of Address

    # def get(self, request, format=None):   # previous get function
    #     is_staff = request.user.is_staff
    #     address =Address.objects.all()
    #     if is_staff:
    #         # address = Address.objects.all()
    #         serializer = AddressSerializer(data=address)
    #         return  Response(serializer.data)
    #     else:
    #         user_type = request.user.user_type
    #         if user_type=='CM':  # Customer = CM
    #             address = Address.objects.filter(user=request.user)
    #         elif user_type=='RT': # Retailer = RT
    #             address = Address.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
    #
    #
    #         elif user_type== 'PD': # Producer = PD
    #             address = Address.objects.filter(order_status='OD', delivery_date_time__gt=datetime.now())
    #         elif user_type== 'SF': # Staff = SF
    #             address = Address.objects.filter(created_by=request.user)
    #
    #         serializer = AddressSerializer(address, many=True, context={'request': request})
    #     return Response(serializer.data)

    def get(self,request):    # new written by me
        if request:
            address = Address.objects.all()
            user_type = request.user.user_type
            if address:
                serializer = AddressSerializer(address,many=True)
                if user_type == 'SF':
                    return Response(serializer.data)
                    # else:
                    #     Response({"Status": "user not allowed"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Status": "Invalide serializer"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Status": "No data to show"},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response ({"Status": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = AddressSerializer(data=request.data,context={'request': request})
        print(serializer)
        if serializer.is_valid():
            if request.user.is_staff:
            # if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            if request.user.user_type=='RT': # Retailer = RT
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
        # if serializer.is_valid():
        #     serializer.save()
        return Response({"baaal..!!"}, status=status.HTTP_400_BAD_REQUEST)






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
        # address = self.get_object(request, pk)
        address = Address.objects.all()
        address.delete()
        # if request.user==address.created_by or request.user.is_staff:
        #     address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Login(APIView):

    def post(self,request,*args,**kwargs):
        if not request.data:
            return Response({'Error': "Please provide mobile no/password"}, status="400")

        mobile_number = request.data['mobile_number']
        # email = request.data['email']
        password = request.data['password']
        try:
            user = UserProfile.objects.get( mobile_number = mobile_number)
        except UserProfile.DoesNotExist:
            return Response({'Error': "Invalid email/password"}, status="400")

        if user.user_type == 'CM':
            if not user.is_approved:
                user.is_approved = True
                user.save()

        if user.is_approved:
            if user:
                if user.check_password(password):
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
    permission_classes = (AllowAny,)
    models = UserProfile
    serializer_class = UserRegistrationSerializer


def otp_key(number):
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


class RetailerRegistration(APIView):

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
