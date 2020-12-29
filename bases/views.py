from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from userProfile.models import BlackListedToken


def checkAuthentication(user, info):
    if user.is_anonymous:
        raise Exception('Must Log In!')
    else:
        token = info.context.headers['Authorization'].split(' ')[1]
        try:
            token = BlackListedToken.objects.get(token=token)
        except BlackListedToken.DoesNotExist:
            token = None
        if token:
            raise Exception('Invalid or expired token!')
        else:
            # checks if user mobile number verified (has frontend dependency)
            # if not user.pin_verified:
            #     raise Exception('mobile number not verified')
            return True


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({'page': self.page.number,
                         'page_size': self.page.paginator.per_page,
                         'count': self.page.paginator.count,
                         'results': data})
