from django.utils import timezone

import graphene
from graphene_django.types import DjangoObjectType

from bases.views import checkAuthentication
from product.graphql.queries import ProductConnection
from ..models import Offer, OfferProduct
from graphene import relay


class OfferType(DjangoObjectType):
    class Meta:
        model = Offer


class OfferProductType(DjangoObjectType):
    class Meta:
        model = OfferProduct


class OfferProductNode(DjangoObjectType):
    class Meta:
        model = OfferProduct
        interfaces = (relay.Node,)

    # @classmethod
    # def get_queryset(cls, queryset, info):
    #     return queryset.filter(is_approved=True)


class OfferProductConnection(relay.Connection):
    class Meta:
        node = OfferProductNode


class Query(graphene.ObjectType):
    offer_list = graphene.List(OfferType)
    all_offer_products = relay.ConnectionField(ProductConnection)
    offer_product_pagination = relay.ConnectionField(OfferProductConnection)

    def resolve_offer_list(self, info):
        today = timezone.now()
        all_offers = Offer.objects.filter(is_approved=True, offer_starts_in__lte=today, offer_ends_in__gte=today)
        return all_offers

    def resolve_all_offer_products(root, info):
        today = timezone.now()
        all_offer_products = OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                                         offer__offer_ends_in__gte=today)
        products = [op.product for op in all_offer_products]
        return products

    def resolve_offer_product_pagination(root, info, **kwargs):
        today = timezone.now()
        return OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                           offer__offer_ends_in__gte=today).order_by('-created_on')
