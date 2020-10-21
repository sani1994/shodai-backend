from django.utils import timezone

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
        payload = []
        all_offers = Offer.objects.filter(is_approved=True)
        today = timezone.now()
        for o in all_offers:
            if o.offer_starts_in < today < o.offer_ends_in:
                payload.append(o)
        return payload

    def resolve_offer_product_list(self, info):
        return OfferProduct.objects.all()
