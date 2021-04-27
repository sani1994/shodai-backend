import graphene
from django.utils import timezone
from offer.models import OfferProduct, Offer
from product.models import Product


class OfferProductCount(graphene.Mutation):
    status = graphene.Boolean()
    count = graphene.Int()

    @staticmethod
    def mutate(root, info, input=None):
        today = timezone.now()
        all_offers = Offer.objects.filter(is_approved=True,
                                          offer_starts_in__lte=today,
                                          offer_ends_in__gte=today,
                                          offer_types='SP')
        count = 0
        for offer in all_offers:
            product_count = Product.objects.filter(is_approved=True,
                                                   products__in=OfferProduct.objects.filter(offer=offer,
                                                                                            is_approved=True)).distinct().count()
            count += product_count

        return OfferProductCount(status=True, count=count)


class Mutation(graphene.ObjectType):
    offer_product_count = OfferProductCount.Field()
