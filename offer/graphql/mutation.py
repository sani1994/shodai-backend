import graphene
from django.utils import timezone

from bases.views import checkAuthentication
from offer.models import OfferProduct
from product.models import Product


class OfferProductCount(graphene.Mutation):
    status = graphene.Boolean()
    count = graphene.Int()

    @staticmethod
    def mutate(root, info, input=None):
        today = timezone.now()
        count = Product.objects.filter(is_approved=True,
                                       products__in=OfferProduct.objects.filter(is_approved=True,
                                                                                offer__is_approved=True,
                                                                                offer__offer_starts_in__lte=today,
                                                                                offer__offer_ends_in__gte=today,
                                                                                offer__offer_types='SP')).distinct().count()

        return OfferProductCount(status=True, count=count)


class Mutation(graphene.ObjectType):
    offer_product_count = OfferProductCount.Field()
