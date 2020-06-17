import graphene
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from graphene_django.types import DjangoObjectType

from utility.messaging import send_sms_otp, otp_text
from ..models import UserProfile, Address, BlackListedToken
from datetime import timedelta
from django.utils import timezone
from random import randint


class UserType(DjangoObjectType):
    class Meta:
        model = UserProfile


class AddressType(DjangoObjectType):
    class Meta:
        model = Address


class Query(graphene.ObjectType):
    all_user = graphene.List(UserType)
    user_info = graphene.Field(UserType)
    user_login = graphene.Field(UserType)
    user_logout = graphene.Field(UserType)
    otp_verification = graphene.Field(UserType, otp=graphene.Int())
    otp_resend = graphene.Field(UserType)
    address_list_by_user = graphene.List(AddressType)
    address_by_id = graphene.List(AddressType, id=graphene.Int())

    def resolve_all_user(self, info):
        return UserProfile.objects.all()

    def resolve_user_info(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Authentication credentials were not provided')
        else:
            token = info.context.headers['Authorization'].split(' ')[1]
            print(token)
            try:
                token = BlackListedToken.objects.get(token=token)
            except BlackListedToken.DoesNotExist as e:
                token = None
            if token:
                raise Exception('Invalid or expired token!')
            else:
                return user

    def resolve_user_login(self, info):
        user = info.context.user
        if user.user_type == "CM":
            # CUSTOMER LOGIN
            if not user.is_authenticated:
                raise Exception('Authentication credentials were not provided')
            else:
                token = info.context.headers['Authorization'].split(' ')[1]
                print(token)
                try:
                    token = BlackListedToken.objects.get(token=token)
                except BlackListedToken.DoesNotExist as e:
                    token = None
                if token:
                    raise Exception('Invalid or expired token!')
                else:
                    return user
        elif user.user_type == "RT" or user.user_type == "PD":
            # RETAILER OR PRODUCER LOGIN
            if not user.is_approved:
                raise Exception('Profile request is waiting for approval')
            else:
                if not user.is_authenticated:
                    raise Exception('Authentication credentials were not provided')
                else:
                    token = info.context.headers['Authorization'].split(' ')[1]
                    print(token)
                    try:
                        token = BlackListedToken.objects.get(token=token)
                    except BlackListedToken.DoesNotExist as e:
                        token = None
                    if token:
                        raise Exception('Invalid or expired token!')
                    else:
                        return user
        elif user.user_type == "SF":
            # STAFF LOGIN
            # PORE KORBO
            return user
        else:
            raise Exception('Invalid Information')

    def resolve_user_logout(self, info):
        user = info.context.user
        try:
            BlackListedToken.objects.create(
                token=info.context.headers['Authorization'].split(' ')[1],
                user=user)
        except IntegrityError:
            raise Exception("Invalid or expired token!")
        finally:
            return None

    def resolve_otp_verification(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in to send otp')
        else:
            token = info.context.headers['Authorization'].split(' ')[1]
            print(token)
            try:
                token = BlackListedToken.objects.get(token=token)
            except BlackListedToken.DoesNotExist as e:
                token = None
            if token:
                raise Exception('Invalid or expired token!')
            else:
                if user.code_valid_till < timezone.now():
                    raise Exception('OTP Expired Try New OTP')
                otp = kwargs.get('otp')
                if otp is not None:
                    if str(otp) == user.verification_code:
                        user = UserProfile.objects.get(pk=user.pk)
                        user.pin_verified = True
                        user.save()
                        return user
                    raise Exception('Your OTP Does Not Match!')
                return None

    def resolve_otp_resend(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in to send otp')
        else:
            token = info.context.headers['Authorization'].split(' ')[1]
            print(token)
            try:
                token = BlackListedToken.objects.get(token=token)
            except BlackListedToken.DoesNotExist as e:
                token = None
            if token:
                raise Exception('Invalid or expired token!')
            else:
                if user.code_valid_till > timezone.now():
                    otp_code = user.verification_code
                else:
                    user = UserProfile.objects.get(pk=user.pk)
                    otp_code = randint(100000, 999999)
                    user.verification_code = otp_code
                    user.code_valid_till = timezone.now() + timedelta(minutes=5)
                    user.save()

                # send sms from here.
                flag = send_sms_otp(user.mobile_number, otp_text.format(
                    otp_code))  # Send OTP message from here
                if flag:
                    return None
                else:
                    token = info.context.headers['Authorization'].split(' ')[1]
                    print(token)
                    try:
                        token = BlackListedToken.objects.get(token=token)
                    except BlackListedToken.DoesNotExist as e:
                        token = None
                    if token:
                        raise Exception('Invalid or expired token!')
                    else:
                        raise Exception('An error occurred while sending the sms!')

    def resolve_address_list_by_user(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in to see address')
        else:
            token = info.context.headers['Authorization'].split(' ')[1]
            print(token)
            try:
                token = BlackListedToken.objects.get(token=token)
            except BlackListedToken.DoesNotExist as e:
                token = None
            if token:
                raise Exception('Invalid or expired token!')
            else:
                return Address.objects.filter(user=user)

    def resolve_address_by_id(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in to see address')
        else:
            token = info.context.headers['Authorization'].split(' ')[1]
            print(token)
            try:
                token = BlackListedToken.objects.get(token=token)
            except BlackListedToken.DoesNotExist as e:
                token = None
            if token:
                raise Exception('Invalid or expired token!')
            else:
                id = kwargs.get('id')
                return Address.objects.filter(user=user, id=id)
