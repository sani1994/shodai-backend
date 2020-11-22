from django.utils import timezone

import graphene
from graphene_django.types import DjangoObjectType

from bases.views import checkAuthentication
from product.graphql.queries import ProductConnection
from product.models import Product
from ..models import Offer, OfferProduct
from graphene import relay


class OfferType(DjangoObjectType):
    class Meta:
        model = Offer


class OfferProductType(DjangoObjectType):
    class Meta:
        model = OfferProduct


class Query(graphene.ObjectType):
    offer_list = graphene.List(OfferType)
    all_offer_products = relay.ConnectionField(ProductConnection)

    def resolve_offer_list(self, info):
        today = timezone.now()
        all_offers = Offer.objects.filter(is_approved=True, offer_starts_in__lte=today, offer_ends_in__gte=today)
        return all_offers

    def resolve_all_offer_products(root, info, **kwargs):
        today = timezone.now()
        all_offer_products = Product.objects.filter(products__in=OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                                                                             offer__offer_ends_in__gte=today).order_by('-created_on'))
        return all_offer_products
