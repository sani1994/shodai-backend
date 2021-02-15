import graphene
from graphene_django import DjangoObjectType
from ..models import CouponCode


class CouponType(DjangoObjectType):
    class Meta:
        model = CouponCode
