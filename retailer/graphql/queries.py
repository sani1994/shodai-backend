import graphene
from graphene_django.types import DjangoObjectType
from ..models import Shop, ShopProduct


class ShopType(DjangoObjectType):
    class Meta:
        model = Shop


class ShopProductType(DjangoObjectType):
    class Meta:
        model = ShopProduct


class Query(graphene.ObjectType):
    shop_list = graphene.List(ShopType)
    shop_product_list = graphene.List(ShopProductType)

    def resolve_shop_list(self, info):
        return Shop.objects.all()

    def resolve_shop_product_list(self, info):
        user = info.context.user
        if user.useruser_type == 'RT':
            if not user.is_authenticated:
                raise Exception('Must Log in to see Shop product details')
            else:
                return ShopProduct.objects.filter(user=user)
        else:
            raise Exception('Unauthorized request')
