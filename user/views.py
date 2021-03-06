import random

from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from shodai.permissions import GenericAuth
from user.serializers import UserProfileSerializer, AddressSerializer, UserRegistrationSerializer, \
    RetailerRegistrationSreializer
from user.models import Address, BlackListedToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from user.models import UserProfile, Otp

from utility.notification import email_notification, send_sms


class UserProfileList(APIView):  # this view returns list of user and create user
    # permission_classes = (IsAuthenticated,)
    permission_classes = [GenericAuth]

    def get(self, request, format=None):
        user_obj = UserProfile.objects.filter(id=request.user.id,
                                              is_approved=True)  # takes only requestd users object
        if user_obj:
            serializer = UserProfileSerializer(user_obj, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"User is not approved"}, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data['user_type'])
            if serializer.data['user_type'] == 'RT' or serializer.data['user_type'] == 'PD':
                sms_body = f"Dear sir,\r\nYour account is waiting for shodai admin approval.Please keep patients.\r\n\r\nShodai Team"
                u = send_sms(serializer.data['mobile_number'], sms_body)
                print(u)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetail(APIView):

    def get(self, request, id):
        user_profile = get_object_or_404(UserProfile, id=id)
        if request.user == user_profile:
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Un-authorized request'}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, id):
        user_profile = get_object_or_404(UserProfile, id=id)
        if request.user == user_profile or request.user.is_staff:
            serializer = UserProfileSerializer(user_profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Un-authorized request'}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, id):
        user_profile = get_object_or_404(UserProfile, id=id)
        if request.user == user_profile or request.user.is_staff:
            user_profile.delete()
        return Response({'User Deleted'}, status=status.HTTP_204_NO_CONTENT)


class AddressList(APIView):  # get address list and create new address
    permission_classes = [GenericAuth]

    def get(self, request):
        address = Address.objects.all()
        user_type = request.user.user_type
        if address:
            serializer = AddressSerializer(address, many=True)
            if user_type == 'SF':
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"Status": "No data to show"}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, format=None):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddressDetail(APIView):  # get address with address id, update and delete
    """
    Retrieve, update and delete Orders
    """

    def get(self, request, id, format=None):
        address = get_object_or_404(Address, id=id)
        serializer = AddressSerializer(address)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        address = get_object_or_404(Address, id=id)
        serializer = AddressSerializer(address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        address = get_object_or_404(Address, id=id)
        address.delete()
        return Response({'Delete Successful..!!'}, status=status.HTTP_200_OK)


class Login(APIView):  # login with mobile number and passwrd

    def post(self, request):
        if not request.data:
            return Response({'Error': "Please provide mobile no/password"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserProfile.objects.get(mobile_number=request.data['mobile_number'])
        except:
            return JsonResponse({"message": "User not exist"}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

        if user.user_type == 'CM':  # if user type is customer no need to approve from admin panel. it will be automatically approve here.
            if not user.is_approved:
                user.is_approved = True
                user.save()

        if user.is_approved:  # check weather user is approved or not.
            if user:
                if user.check_password(request.data['password']):
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
                    return JsonResponse({"message": "Password dosen't match"},
                                        status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        return JsonResponse({"message": "Profile request is waiting for approval"},
                            status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)


class Logout(APIView):  # logout
    permission_classes = [GenericAuth]

    def post(self, request):
        try:
            BlackListedToken.objects.create(
                token=request.headers['Authorization'].split(' ')[1],
                user=request.user)
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


class UserRegistration(CreateAPIView):  # user registration class
    permission_classes = (AllowAny,)
    models = UserProfile
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if serializer.data['user_type'] == 'RT' or serializer.data['user_type'] == 'PD':
            sms_body = f"Dear sir,\r\nYour account is waiting for shodai admin approval." \
                       f"Please keep patients.\r\n\r\nShodai Team"
            send_sms(serializer.data['mobile_number'], sms_body)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def otp_key(number):  # generate OTP code
    if number:
        key = random.randint(999, 9999)
        return key
    else:
        return False


class OtpCode(APIView):  # OTP code class to generate OTP code

    def post(self, request):
        mobile_number = request.data['mobile_number']
        if mobile_number:
            mobile_number = str(mobile_number)
            try:
                obj = Otp.objects.get(mobile_number=mobile_number)
            except Otp.DoesNotExist:
                obj = None
            if obj:
                # obj.counter = 0
                # obj.save()
                if obj.count > 5:  # if otp is sent more then 5 times it will block the user
                    return Response({"Status": "Faild",
                                     "details": "OTP sent 5 times. please contact with support"},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    key = otp_key(mobile_number)
                    obj.otp_code = key
                    obj.count = obj.count + 1
                    obj.save()
                    return Response({
                        "Status": "Success..!!",
                        "details": "Mobile number: " + str(obj.mobile_number) + " Otp code: " + str(obj.otp_code)
                    }, status=status.HTTP_200_OK)
            else:
                key = otp_key(mobile_number)
                obj = Otp.objects.create(mobile_number=mobile_number, otp_code=key, count=1)
                return Response({
                    "Status": "Success..!!",
                    "details": "Mobile number: " + str(obj.mobile_number) + " Otp code: " + str(obj.otp_code)
                }, status=status.HTTP_200_OK)


class OtpVerify(APIView):  # to varify otp code against a number

    def post(self, request):
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
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "Failed..!!",
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status": "Invalid..!!",
            }, status=status.HTTP_204_NO_CONTENT)


class RetailerRegistration(APIView):  # Retailer regerstration class

    def post(self, request):
        serializer = RetailerRegistrationSreializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            """
            To send notification to admin
            """
            sub = "Approval Request For Retailer Account"
            body = f"Dear Concern,\r\n User phone number :{serializer.data['mobile_number']} \r\nUser type: {serializer.data['user_type']} \r\nis requesting your approval.\r\n \r\nThanks and Regards\r\nShodai"
            email_notification(sub, body)
            """
            Notification code ends here
            """
            '''
            send sms to retailer.
            '''
            sms_body = f"Dear sir,\r\nYour account is waiting for shodai admin approval.Please keep patients.\r\n\r\nShodai Team"
            send_sms(serializer.data['mobile_number'], sms_body)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User Already Exist"}, status=status.HTTP_200_OK)


class ChangePassword(APIView):
    '''
    :param request: old_password,new_password
    :return: Change password if the
    '''
    permission_classes = [GenericAuth]

    def post(self, request):
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        user_instance = get_object_or_404(UserProfile, mobile_number=request.user.mobile_number)
        valid = user_instance.check_password(old_password)
        if not valid:
            return Response({"status": "Invalid Password"}, status=status.HTTP_404_NOT_FOUND)
        user_instance.set_password(new_password)
        user_instance.save()
        return Response({"status": "Password Changed Successfully"}, status=status.HTTP_200_OK)


class ForgetPassword(APIView):

    def post(self, request):
        '''
        :param request: mobile_number
        :return: text message to the given mobile number if it exist.
        '''
        mobile_number = request.POST.get("mobile_number")
        if mobile_number:
            # user_instance = get_object_or_404(UserProfile, mobile_number=mobile_number)
            user_instance = UserProfile.objects.filter(mobile_number=mobile_number)
            # if user_instance.
            if not user_instance:
                return Response({"status": "User not available"}, status=status.HTTP_200_OK)

            else:
                # print(user_instance[0].mobile_number)
                temp_password = get_random_string(length=6)
                if user_instance[0].first_name and user_instance[0].last_name:
                    client_name = user_instance[0].first_name + " " + user_instance[0].last_name
                else:
                    client_name = user_instance[0].username
                sms_body = f"Dear " + client_name + \
                           ",\r\nWe have created a new password [" + temp_password + \
                           "] based on your forget password request." \
                           "\r\n[N.B:Please change your password after login] "
                sms_flag = send_sms(mobile_number=user_instance[0].mobile_number, sms_content=sms_body)
                if sms_flag == 'success':
                    user_instance[0].set_password(temp_password)
                    user_instance[0].save()
                    return Response({"status": "Message Sent Successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "An error occurred while sending the sms"},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "User not available"}, status=status.HTTP_204_NO_CONTENT)


class ForgetPasswordVarification(APIView):

    def post(self, request):
        '''
        :param request:mobile_number, temp_password
        :return: success message or unsuccess message
        '''
        mobile_number = request.POST.get("mobile_number")
        password = request.POST.get("temp_password")
        user_instance = get_object_or_404(UserProfile, mobile_number=mobile_number)
        if user_instance:
            if user_instance.check_password(password):
                return Response({"status": "Password Changed Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Please provide the password sent by sms"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "User not available"}, status=status.HTTP_204_NO_CONTENT)
