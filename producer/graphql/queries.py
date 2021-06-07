import graphene
from graphene_django.types import DjangoObjectType
from graphene_gis.converter import gis_converter  # noqa

from base.views import checkAuthentication
from ..models import ProducerProductRequest


class ProducerProductType(DjangoObjectType):
    class Meta:
        model = ProducerProductRequest
        fields = ['id', 'product_name', 'product_image', 'product_description']
