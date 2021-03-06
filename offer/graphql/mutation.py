import graphene
from decouple import config
from django.utils import timezone
from offer.models import OfferProduct, Offer
from order.models import PreOrderSetting
from product.models import Product
from utility.models import QurbaniProductCriteria


class Count(graphene.Mutation):
    offer_product_count = graphene.Int()
    pre_order_product_count = graphene.Int()
    pre_order_qurbani_product_count = graphene.Int()

    @staticmethod
    def mutate(root, info, input=None):
        time_now = timezone.now()
        all_offers = Offer.objects.filter(is_approved=True,
                                          offer_starts_in__lte=time_now,
                                          offer_ends_in__gte=time_now,
                                          offer_types='SP')
        offer_product_count = 0
        for offer in all_offers:
            product_count = Product.objects.filter(is_approved=True,
                                                   products__in=OfferProduct.objects.filter(offer=offer,
                                                                                            is_approved=True)).distinct().count()
            offer_product_count += product_count
        pre_order_product_count = PreOrderSetting.objects.filter(is_approved=True,
                                                                 is_processed=False,
                                                                 start_date__lte=time_now,
                                                                 end_date__gte=time_now).count()
        pre_order_qurbani_product_count = PreOrderSetting.objects.filter(is_approved=True,
                                                                         is_processed=False,
                                                                         start_date__lte=time_now,
                                                                         end_date__gte=time_now,
                                                                         producer_product__producer__mobile_number=config("QURBANI_PRODUCT_PRODUCER"),
                                                                         qurbani_products__in=QurbaniProductCriteria.objects.all()).count()

        return Count(offer_product_count=offer_product_count,
                     pre_order_product_count=pre_order_product_count,
                     pre_order_qurbani_product_count=pre_order_qurbani_product_count)


class Mutation(graphene.ObjectType):
    all_count = Count.Field()
