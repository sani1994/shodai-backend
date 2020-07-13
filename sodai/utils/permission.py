from django.contrib.auth.models import Permission
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from sodai.utils.helper import get_user_object
from userProfile.models import BlackListedToken, UserProfile


# from userProfile.views import GET


class GenericAuth(IsAuthenticated):
    def has_permission(self, request, view):
        username = request.user
        try:
            token = request.headers['Authorization'].split(' ')[1]
        except KeyError:
            return False

        try:
            is_blacklisted = BlackListedToken.objects.get(
                user=get_user_object(username=username), token=token)

            if is_blacklisted:
                return False

        except BlackListedToken.DoesNotExist:
            pass
        return super().has_permission(request, view)


class AdminAuth(IsAdminUser):
    def has_permission(self, request, view):
        username = request.user.username
        try:
            token = request.headers['Authorization'].split(' ')[1]
        except KeyError:
            return False

        try:
            is_blacklisted = BlackListedToken.objects.get(
                user=get_user_object(username=username), token=token)

            if is_blacklisted:
                return False

        except BlackListedToken.DoesNotExist:
            pass
        return super().has_permission(request, view)
