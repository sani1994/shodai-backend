import graphene
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from random import randint

from django.utils.crypto import get_random_string

from utility.messaging import otp_text, send_sms_otp
from utility.notification import send_sms, email_notification
from .queries import UserType, AddressType
from ..models import UserProfile, Address
from graphql_jwt.shortcuts import get_token, create_refresh_token


class UserEnum(graphene.Enum):
    CUSTOMER = "CM"
    RETAILER = "RT"
    PRODUCER = "PD"
    STAFF = "SF"


class UserInfoInput(graphene.InputObjectType):
    user_type = graphene.NonNull(UserEnum)
    user_image = graphene.String()
    mobile_number = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)


class UpdateUserInfoInput(graphene.InputObjectType):
    user_image = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()


class RetailerInfoInput(graphene.InputObjectType):
    user_type = graphene.NonNull(UserEnum)
    user_image = graphene.String()
    mobile_number = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    user_NID = graphene.String(required=True)
    password = graphene.String(required=True)


class AddressInput(graphene.InputObjectType):
    road = graphene.String(required=True)
    city = graphene.String(required=True)
    district = graphene.String(required=True)
    country = graphene.String(required=True)
    zip_code = graphene.String(required=True)


class AddressUpdateInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    road = graphene.String(required=True)
    city = graphene.String(required=True)
    district = graphene.String(required=True)
    country = graphene.String(required=True)
    zip_code = graphene.String(required=True)


class UserCreateMutation(graphene.Mutation):
    user = graphene.Field(UserType)
    otp_status = graphene.String()
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        input = UserInfoInput(required=True)

    @staticmethod
    def mutate(root, info, input=None):
        try:
            user = UserProfile.objects.get(username=input.mobile_number)
        except UserProfile.DoesNotExist as e:
            user = None

        if user:
            raise Exception('User Already Exists!')
        else:
            user_instance = UserProfile(username=input.mobile_number,
                                        user_type=input.user_type,
                                        email=input.email,
                                        mobile_number=input.mobile_number,
                                        first_name=input.first_name,
                                        last_name=input.last_name,
                                        created_on=timezone.now(),
                                        modified_on=timezone.now(),
                                        code_valid_till=timezone.now() + timedelta(minutes=5),
                                        verification_code=randint(100000, 999999)
                                        )
            user_instance.set_password(input.password)
            user_instance.is_approved = True
            user_instance.save()
            token = get_token(user_instance)
            refresh_token = create_refresh_token(user_instance)
            otp_code = user_instance.verification_code
            otp_flag = send_sms_otp(user_instance.mobile_number, otp_text.format(
                otp_code))
            otp_status = "OTP send successfully" if otp_flag else "OTP failed"
            return UserCreateMutation(user=user_instance,
                                      token=token,
                                      refresh_token=refresh_token,
                                      otp_status=otp_status)


class UserUpdateMutation(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        input = UpdateUserInfoInput(required=True)

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Must Log in to update information')
        else:
            user_instance = UserProfile.objects.get(username=user.mobile_number)
            user_instance.email = input.email if input.email else user.email
            user_instance.first_name = input.first_name if input.first_name else user.first_name
            user_instance.last_name = input.last_name if input.last_name else user.last_name
            user_instance.modified_on = timezone.now()
            user_instance.save()
            return UserUpdateMutation(user=user_instance)


class RetailerProducerCreateMutation(graphene.Mutation):
    user = graphene.Field(UserType)
    otp_status = graphene.String()
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        input = RetailerInfoInput(required=True)

    @staticmethod
    def mutate(root, info, input=None):
        try:
            user = UserProfile.objects.get(username=input.mobile_number)
        except UserProfile.DoesNotExist as e:
            user = None

        if user:
            raise Exception('User Already Exists!')
        else:
            user_instance = UserProfile(username=input.mobile_number,
                                        user_type=input.user_type,
                                        email=input.email,
                                        user_NID=input.user_NID,
                                        mobile_number=input.mobile_number,
                                        first_name=input.first_name,
                                        last_name=input.last_name,
                                        created_on=timezone.now(),
                                        modified_on=timezone.now(),
                                        code_valid_till=timezone.now() + timedelta(minutes=5),
                                        verification_code=randint(100000, 999999)
                                        )
            user_instance.set_password(input.password)
            user_instance.save()

            """
            To send notification to admin 
            """
            sub = "Approval Request For Retailer Account"
            body = f"Dear Concern,\r\n User phone number :{user_instance.mobile_number} " \
                   f"\r\nUser type: {user_instance.user_type} \r\nis requesting your approval.\r\n \r\nThanks and " \
                   f"Regards\r\nShodai "
            email_notification(sub, body)

            '''
            To send sms to retailer.
            '''
            sms_body = f"Dear sir,\r\nYour account is waiting for shodai admin approval.Please keep " \
                       f"patients.\r\n\r\nShodai Team "
            send_sms(user_instance.mobile_number, sms_body)

            token = get_token(user_instance)
            refresh_token = create_refresh_token(user_instance)
            otp_code = user_instance.verification_code
            otp_flag = send_sms_otp(user_instance.mobile_number, otp_text.format(
                otp_code))
            otp_status = "OTP send successfully" if otp_flag else "OTP failed"
            return UserCreateMutation(user=user_instance,
                                      token=token,
                                      refresh_token=refresh_token,
                                      otp_status=otp_status)


class AddressCreateMutation(graphene.Mutation):
    class Arguments:
        input = AddressInput(required=True)

    address = graphene.Field(AddressType)

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Must Log In!')
        else:
            if user.user_type == 'CM':
                address_instance = Address(road=input.road,
                                           city=input.city,
                                           district=input.district,
                                           country=input.country,
                                           zip_code=input.zip_code,
                                           user=user,
                                           )
                address_instance.save()
                return AddressCreateMutation(address=address_instance)
            else:
                raise Exception('Unauthorized request!')


class AddressUpdateMutation(graphene.Mutation):
    class Arguments:
        input = AddressUpdateInput(required=True)

    address = graphene.Field(AddressType)
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Must Log In!')
        else:
            if user.user_type == 'CM':
                address = Address.objects.get(id=input.id, user=user)
                address.road = input.road if input.road else address.road
                address.city = input.city if input.city else address.city
                address.district = input.district if input.district else address.district
                address.country = input.country if input.country else address.country
                address.zip_code = input.zip_code if input.zip_code else address.zip_code
                address.user = user
                address.save()
                return AddressUpdateMutation(address=address, ok=True)
            else:
                raise Exception('Unauthorized request!')


class AddressDeleteMutation(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Must Log In!')
        else:
            if user.user_type == 'CM':
                obj = Address.objects.get(pk=kwargs["id"], user=user)
                obj.delete()
                return cls(ok=True)
            else:
                raise Exception('Unauthorized request!')


class ForgotPasswordMutation(graphene.Mutation):
    msg = graphene.String()

    class Arguments:
        mobile_number = graphene.String()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        mobile_number = kwargs.get('mobile_number')
        user_instance = get_object_or_404(UserProfile, mobile_number=mobile_number)
        if user_instance:
            temp_password = get_random_string(length=6)
            sms_body = f"Dear Mr/Mrs,\r\nYour one time password is " + temp_password + ".\r\n[N.B:Please change the " \
                                                                                       "password after " \
                                                                                       f"login] "
            send_sms(mobile_number=user_instance.mobile_number, sms_content=sms_body)
            user_instance.set_password(temp_password)
            user_instance.save()
            return cls(msg="Message Sent Successfully")
        else:
            return cls(msg="User not available")


class ChangePasswordMutation(graphene.Mutation):
    msg = graphene.String()

    class Arguments:
        old_password = graphene.String()
        new_password = graphene.String()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user_instance = info.context.user
        if user_instance.is_authenticated:
            old_password = kwargs.get('old_password')
            new_password = kwargs.get('new_password')
            valid = user_instance.check_password(old_password)
            if not valid:
                return cls(msg="Invalid Password")
            user_instance.set_password(new_password)
            user_instance.save()
            return cls(msg="Password Changed Successfully")
        else:
            raise Exception('Authentication credentials were not provided')


class Mutation(graphene.ObjectType):
    create_user = UserCreateMutation.Field()
    update_user = UserUpdateMutation.Field()
    create_retailer = RetailerProducerCreateMutation.Field()
    create_address = AddressCreateMutation.Field()
    update_address = AddressUpdateMutation.Field()
    delete_address = AddressDeleteMutation.Field()
    change_password = ChangePasswordMutation.Field()
    forgot_password = ForgotPasswordMutation.Field()
