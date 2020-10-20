import graphene
from graphene_django.types import DjangoObjectType
from graphene_gis.converter import gis_converter

from bases.views import checkAuthentication
from userProfile.models import BlackListedToken
from ..models import Offer, OfferProduct


class OfferType(DjangoObjectType):
    class Meta:
        model = Offer


class OfferProductType(DjangoObjectType):
    class Meta:
        model = OfferProduct


class Query(graphene.ObjectType):
    offer_list = graphene.List(OfferType)
    offer_product_list = graphene.List(OfferProductType)

    def resolve_offer_list(self, info):
        return Offer.objects.all()

    def resolve_offer_product_list(self, info):
        return OfferProduct.objects.all()
