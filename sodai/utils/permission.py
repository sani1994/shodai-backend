from django.contrib.auth.models import Permission
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission, SAFE_METHODS

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
        is_access_denied = request.user.groups.filter(name='access_denied').exists()
        try:
            token = request.headers['Authorization'].split(' ')[1]

        except KeyError:
            return False

        try:
            is_blacklisted = BlackListedToken.objects.get(
                user=UserProfile.objects.filter(username=username)[0], token=token)

            if is_blacklisted:
                return False

        except BlackListedToken.DoesNotExist:
            pass
        if is_access_denied:
            return False
        return super().has_permission(request, view)


class ReadOnly(BasePermission):
    """
    The request is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user
        )


class ReadOnlyAuth(IsAuthenticated):
    def has_permission(self, request, view):
        username = request.user
        is_read_only = request.user.groups.filter(name='read_only').exists()
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
        if is_read_only:
            return bool(
                request.method in SAFE_METHODS
            )
        return super().has_permission(request, view)
