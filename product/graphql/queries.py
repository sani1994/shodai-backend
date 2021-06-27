import graphene
from django.utils import timezone
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from base.views import keyword_based_search
from offer.models import OfferProduct
from order.models import PreOrderSetting
from product.models import Product, ProductCategory, ShopCategory, ProductMeta
from utility.models import ProductUnit
from graphene import relay


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        exclude_fields = ['orderproduct_set', 'created_on', 'created_by', 'modified_on', 'modified_by']
        filter_fields = {"product_name": ["icontains"]}
        interfaces = (relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(is_approved=True)

    offer_price = graphene.Float()
    pre_order_slug = graphene.String()
    pre_order_price = graphene.Float()
    breadcrumb = graphene.String()

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

    def resolve_pre_order_slug(self, info):
        time_now = timezone.now()
        pre_order_setting = PreOrderSetting.objects.filter(product=self,
                                                           is_approved=True,
                                                           is_processed=False,
                                                           start_date__lte=time_now,
                                                           end_date__gte=time_now).first()
        if pre_order_setting:
            return pre_order_setting.slug
        else:
            return None

    def resolve_pre_order_price(self, info):
        time_now = timezone.now()
        pre_order_setting = PreOrderSetting.objects.filter(product=self,
                                                           is_approved=True,
                                                           is_processed=False,
                                                           start_date__lte=time_now,
                                                           end_date__gte=time_now).first()
        if pre_order_setting:
            return pre_order_setting.discounted_price
        else:
            return None

    def resolve_breadcrumb(self, info):
        category = ProductCategory.objects.get(id=self.product_category.id)
        breadcrumb = category.type_of_product
        while category.parent:
            category = ProductCategory.objects.get(id=category.parent.id)
            breadcrumb = f"{category.type_of_product} > {breadcrumb}"
        return breadcrumb


class ProductConnection(relay.Connection):
    class Meta:
        node = ProductNode


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        exclude_fields = ['orderproduct_set', 'created_on', 'created_by', 'modified_on', 'modified_by']

    offer_price = graphene.Float()
    breadcrumb = graphene.String()

    def resolve_offer_price(self, info):
        today = timezone.now()
        offer_product = OfferProduct.objects.filter(is_approved=True, offer__offer_starts_in__lte=today,
                                                    offer__offer_ends_in__gte=today, product=self)
        if offer_product:
            return offer_product[0].offer_price
        else:
            return None

    def resolve_breadcrumb(self, info):
        category = ProductCategory.objects.get(id=self.product_category.id)
        breadcrumb = category.type_of_product
        while category.parent:
            category = ProductCategory.objects.get(id=category.parent.id)
            breadcrumb = f"{category.type_of_product} > {breadcrumb}"
        return breadcrumb


class ProductCategoryType(DjangoObjectType):
    class Meta:
        model = ProductCategory
        exclude_fields = ['product_set', 'created_on', 'created_by', 'modified_on', 'modified_by']


class ProductUnitType(DjangoObjectType):
    class Meta:
        model = ProductUnit
        exclude_fields = ['product_set', 'created_on', 'created_by', 'modified_on', 'modified_by']


# class ProductMetaType(DjangoObjectType):
#     class Meta:
#         model = ProductMeta
#
#
# class ShopCategoryType(DjangoObjectType):
#     class Meta:
#         model = ShopCategory


class Query(graphene.ObjectType):
    products_by_category = relay.ConnectionField(ProductConnection, category_id=graphene.Int())
    product_by_slug = graphene.Field(ProductNode, slug=graphene.String())
    search_product = DjangoFilterConnectionField(ProductNode)

    # product_categories = graphene.List(ProductCategoryType)
    # product_by_id = relay.Node.Field(ProductNode)
    # search_product = relay.ConnectionField(ProductConnection, search=graphene.String())
    # products_by_meta = relay.ConnectionField(ProductConnection, meta_id=graphene.Int())
    # all_products_pagination = relay.ConnectionField(ProductConnection)
    # all_products = graphene.List(ProductType)
    # shop_categories = graphene.List(ShopCategoryType)
    # product_meta_list = graphene.List(ProductMetaType)
    # product_meta_by_category = graphene.List(ProductMetaType, cat_ID=graphene.Int())

    def resolve_products_by_category(root, info, **kwargs):
        category_id = kwargs.get('category_id')
        return Product.objects.filter(product_category__id=category_id,
                                      product_category__is_approved=True,
                                      is_approved=True).order_by('-created_on')

    def resolve_product_by_slug(self, info, **kwargs):
        slug = kwargs.get('slug')
        return Product.objects.filter(slug=slug, is_approved=True).first()

    # def resolve_product_categories(self, info):
    #     return ProductCategory.objects.filter(is_approved=True)
    #
    # def resolve_search_product(self, info, **kwargs):
    #     query = kwargs.get('search')
    #     return keyword_based_search(Product, query, ['product_name'], {'is_approved': True})
    #
    # def resolve_products_by_meta(root, info, **kwargs):
    #     meta_id = kwargs.get('meta_id')
    #     return Product.objects.filter(product_meta__pk=meta_id,
    #                                   product_meta__is_approved=True,
    #                                   product_meta__product_category__is_approved=True,
    #                                   is_approved=True).order_by('-created_on')
    #
    # def resolve_all_products_pagination(root, info, **kwargs):
    #     return Product.objects.filter(product_category__is_approved=True,
    #                                   is_approved=True).order_by('-created_on')
    #
    # def resolve_all_products(self, info, **kwargs):
    #     return Product.objects.filter(is_approved=True)
    #
    # def resolve_shop_categories(self, info):
    #     return ShopCategory.objects.filter(is_approved=True)
    #
    # def resolve_product_meta_list(self, info):
    #     return ProductMeta.objects.filter(is_approved=True)
    #
    # def resolve_product_meta_by_category(root, info, **kwargs):
    #     cat_id = kwargs.get('cat_ID')
    #     return ProductMeta.objects.filter(product_category__pk=cat_id, is_approved=True)
