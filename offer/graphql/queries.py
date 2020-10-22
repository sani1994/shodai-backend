from django.utils import timezone

import graphene
from graphene_django.types import DjangoObjectType

from bases.views import checkAuthentication
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
        today = timezone.now()
        all_offers = Offer.objects.filter(is_approved=True, offer_starts_in__lte=today, offer_ends_in__gte=today)
        return all_offers

    def resolve_offer_product_list(self, info):
        today = timezone.now()
        all_offer_products = OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                                         offer__offer_ends_in__gte=today)
        return all_offer_products
