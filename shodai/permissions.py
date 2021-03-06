from decouple import config
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission, SAFE_METHODS
from user.models import BlackListedToken, UserProfile


class GenericAuth(IsAuthenticated):
    def has_permission(self, request, view):
        try:
            token = request.headers['Authorization'].split(' ')[1]
        except KeyError:
            return False

        try:
            is_blacklisted = BlackListedToken.objects.get(
                user=request.user, token=token)

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
        is_read_only = request.user.groups.filter(name='read_only').exists()
        try:
            token = request.headers['Authorization'].split(' ')[1]
        except KeyError:
            return False

        try:
            is_blacklisted = BlackListedToken.objects.get(
                user=request.user, token=token)

            if is_blacklisted:
                return False

        except BlackListedToken.DoesNotExist:
            pass
        if is_read_only:
            return bool(
                request.method in SAFE_METHODS
            )
        return super().has_permission(request, view)


class IsAdminUserQP(TokenAuthentication):
    def has_permission(self, request, view):
        token = request.query_params.get('token')
        if token:
            user, _ = self.authenticate_credentials(token)
            return user.is_staff
        return False


class ServiceAPIAuth(BasePermission):

    def has_permission(self, request, view):
        api_key = 'API-Key ' + config("API_KEY")
        api_key_info = request.headers.get('Authorization')

        if api_key_info and api_key_info == api_key:
            return True
        return False
