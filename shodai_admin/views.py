from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView

# Create your views here.
from rest_framework_simplejwt.tokens import RefreshToken

from sodai.utils.helper import get_user_object
from sodai.utils.permission import AdminAuth
from userProfile.models import UserProfile, BlackListedToken


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
            except UserProfile.DoesNotExist as e:
                user = None

        if user is None:
            return JsonResponse({
                "message": "User does not exist!",
                "status": False,
                "status_code": status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            }, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            if user.check_password(request.data['password']):
                if user.user_type == 'SF':
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