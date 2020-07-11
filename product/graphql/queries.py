import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from ..models import Product, ProductCategory, ShopCategory, ProductMeta
from utility.models import ProductUnit
from graphene import relay


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = {"product_name": ["icontains"]}
        interfaces = (relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


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
    product_categories = graphene.List(ProductCategoryType)
    shop_categories = graphene.List(ShopCategoryType)
    product_meta_list = graphene.List(ProductMetaType)
    recently_added_product_list = graphene.List(ProductNode)

    def resolve_products_by_category(root, info, **kwargs):
        category = kwargs.get('category')
        return Product.objects.filter(product_meta__product_category__pk=category)

    def resolve_products_by_meta(root, info, **kwargs):
        meta_id = kwargs.get('meta_id')
        return Product.objects.filter(product_meta__pk=meta_id)

    def resolve_all_products_pagination(root, info, **kwargs):
        return Product.objects.all()

    def resolve_all_products(self, info, **kwargs):
        return Product.objects.all()

    def resolve_product_categories(self, info):
        return ProductCategory.objects.all()

    def resolve_product_meta_list(self, info):
        return ProductMeta.objects.all()

    def resolve_shop_categories(self, info):
        return ShopCategory.objects.all()

    def resolve_recently_added_product_list(self, info):
        return Product.objects.all().order_by('-created_on')[:20]
