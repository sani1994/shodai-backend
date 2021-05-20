from django.utils import timezone

import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType

from product.graphql.queries import ProductConnection
from product.models import Product
from offer.models import Offer, OfferProduct


class OfferType(DjangoObjectType):
    class Meta:
        model = Offer
        fields = ['id', 'offer_name', 'offer_types']

    total_offer_product = graphene.Int()

    def resolve_total_offer_product(self, info):
        today = timezone.now()
        product_count = Product.objects.filter(is_approved=True,
                                               products__in=OfferProduct.objects.filter(offer=self,
                                                                                        is_approved=True,
                                                                                        offer__is_approved=True,
                                                                                        offer__offer_starts_in__lte=today,
                                                                                        offer__offer_ends_in__gte=today)).distinct().count()
        return product_count


class Query(graphene.ObjectType):
    offer_list = graphene.List(OfferType)
    all_offer_products = relay.ConnectionField(ProductConnection)
    all_products_by_offer = relay.ConnectionField(ProductConnection, offer_id=graphene.Int())

    def resolve_offer_list(self, info):
        today = timezone.now()
        all_offers = Offer.objects.filter(is_approved=True,
                                          offer_starts_in__lte=today,
                                          offer_ends_in__gte=today,
                                          offer_types='SP')
        return all_offers

    def resolve_all_offer_products(root, info, **kwargs):
        today = timezone.now()
        all_offer_products = Product.objects.filter(is_approved=True,
                                                    products__in=OfferProduct.objects.filter(is_approved=True,
                                                                                             offer__is_approved=True,
                                                                                             offer__offer_starts_in__lte=today,
                                                                                             offer__offer_ends_in__gte=today,
                                                                                             offer__offer_types='SP').order_by('-created_on'))
        return all_offer_products

    def resolve_all_products_by_offer(root, info, **kwargs):
        offer_id = kwargs.get('offer_id')
        today = timezone.now()
        all_offer_products = Product.objects.filter(is_approved=True,
                                                    products__in=OfferProduct.objects.filter(is_approved=True,
                                                                                             offer__id=offer_id,
                                                                                             offer__is_approved=True,
                                                                                             offer__offer_starts_in__lte=today,
                                                                                             offer__offer_ends_in__gte=today).order_by('-created_on')).distinct()
        return all_offer_products
