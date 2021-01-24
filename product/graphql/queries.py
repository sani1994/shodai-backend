import graphene
from django.utils import timezone
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from offer.models import OfferProduct
from ..models import Product, ProductCategory, ShopCategory, ProductMeta
from utility.models import ProductUnit
from graphene import relay


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = {"product_name": ["icontains"]}
        interfaces = (relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(is_approved=True)

    offer_price = graphene.Float()

    def resolve_offer_price(self, info):
        today = timezone.now()
        offer_product = OfferProduct.objects.filter(product=self,
                                                    is_approved=True,
                                                    offer__is_approved=True,
                                                    offer__offer_starts_in__lte=today,
                                                    offer__offer_ends_in__gte=today)
        if offer_product:
            return offer_product[0].offer_price
        else:
            return None


class ProductType(DjangoObjectType):
    class Meta:
        model = Product

    offer_price = graphene.Float()

    def resolve_offer_price(self, info):
        today = timezone.now()
        offer_product = OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                                    offer__offer_ends_in__gte=today, product=self)
        if offer_product:
            return offer_product[0].offer_price
        else:
            return None


class ProductMetaType(DjangoObjectType):
    class Meta:
        model = ProductMeta


class ProductCategoryType(DjangoObjectType):
    class Meta:
        model = ProductCategory


class ShopCategoryType(DjangoObjectType):
    class Meta:
        model = ShopCategory


class ProductUnitType(DjangoObjectType):
    class Meta:
        model = ProductUnit


class ProductConnection(relay.Connection):
    class Meta:
        node = ProductNode


class Query(graphene.ObjectType):
    products_by_category = relay.ConnectionField(ProductConnection, category=graphene.Int())
    products_by_meta = relay.ConnectionField(ProductConnection, meta_id=graphene.Int())
    search_product = DjangoFilterConnectionField(ProductNode)
    all_products_pagination = relay.ConnectionField(ProductConnection)
    all_products = graphene.List(ProductType)
    product_by_id = relay.Node.Field(ProductNode)
    product_by_slug = graphene.Field(ProductNode, slug=graphene.String())
    product_categories = graphene.List(ProductCategoryType)
    shop_categories = graphene.List(ShopCategoryType)
    product_meta_list = graphene.List(ProductMetaType)
    product_meta_by_category = graphene.List(ProductMetaType, cat_ID=graphene.Int())
    recently_added_product_list = graphene.List(ProductNode)

    def resolve_products_by_category(root, info, **kwargs):
        category = kwargs.get('category')
        return Product.objects.filter(product_meta__product_category__pk=category,
                                      product_meta__product_category__is_approved=True,
                                      product_meta__is_approved=True,
                                      is_approved=True).order_by('-created_on')

    def resolve_products_by_meta(root, info, **kwargs):
        meta_id = kwargs.get('meta_id')
        return Product.objects.filter(product_meta__pk=meta_id,
                                      product_meta__is_approved=True,
                                      product_meta__product_category__is_approved=True,
                                      is_approved=True).order_by('-created_on')

    def resolve_all_products_pagination(root, info, **kwargs):
        return Product.objects.filter(product_meta__product_category__is_approved=True,
                                      product_meta__is_approved=True,
                                      is_approved=True).order_by('-created_on')

    def resolve_all_products(self, info, **kwargs):
        return Product.objects.filter(is_approved=True)

    def resolve_product_by_slug(self, info, **kwargs):
        slug = kwargs.get('slug')
        product = Product.objects.filter(slug=slug, is_approved=True)
        if product:
            return product[0]
        else:
            return None

    def resolve_product_categories(self, info):
        return ProductCategory.objects.filter(is_approved=True)

    def resolve_product_meta_list(self, info):
        return ProductMeta.objects.filter(is_approved=True)

    def resolve_product_meta_by_category(root, info, **kwargs):
        cat_id = kwargs.get('cat_ID')
        return ProductMeta.objects.filter(product_category__pk=cat_id, is_approved=True)

    def resolve_shop_categories(self, info):
        return ShopCategory.objects.filter(is_approved=True)

    def resolve_recently_added_product_list(self, info):
        return Product.objects.filter(is_approved=True).order_by('-created_on')[:20]
