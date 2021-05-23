import graphene
from django.utils import timezone
from offer.models import OfferProduct, Offer
from order.models import PreOrderSetting
from product.models import Product


class Count(graphene.Mutation):
    status = graphene.Boolean()
    offer_product_count = graphene.Int()
    pre_order_settings_count = graphene.Int()

    @staticmethod
    def mutate(root, info, input=None):
        today = timezone.now()
        all_offers = Offer.objects.filter(is_approved=True,
                                          offer_starts_in__lte=today,
                                          offer_ends_in__gte=today,
                                          offer_types='SP')
        offer_product_count = 0
        for offer in all_offers:
            product_count = Product.objects.filter(is_approved=True,
                                                   products__in=OfferProduct.objects.filter(offer=offer,
                                                                                            is_approved=True)).distinct().count()
            offer_product_count += product_count
        pre_order_count = PreOrderSetting.objects.filter(is_approved=True,
                                                         start_date__lte=today,
                                                         end_date__gte=today).count()

        return Count(status=True,
                     offer_product_count=offer_product_count,
                     pre_order_settings_count=pre_order_count)


class Mutation(graphene.ObjectType):
    all_count = Count.Field()
