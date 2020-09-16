from django.shortcuts import render

# Create your views here.
from userProfile.models import BlackListedToken


def checkAuthentication(user, info):
    if user.is_anonymous:
        raise Exception('Must Log In!')
    else:
        token = info.context.headers['Authorization'].split(' ')[1]
        try:
            token = BlackListedToken.objects.get(token=token)
        except BlackListedToken.DoesNotExist as e:
            token = None
        if token:
            raise Exception('Invalid or expired token!')
        else:
            # checks if user mobile number verified (has frontend dependency)
            # if not user.pin_verified:
            #     raise Exception('mobile number not verified')
            return True
