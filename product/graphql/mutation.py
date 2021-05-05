import graphene
from django.utils.text import slugify
from .queries import ProductNode
from ..models import Product, ProductMeta
from utility.models import ProductUnit


class ProductInput(graphene.InputObjectType):
    product_name = graphene.String(required=True)
    product_name_bn = graphene.String()
    product_image = graphene.String(required=True)
    product_description = graphene.String(required=True)
    product_description_bn = graphene.String()
    product_unit = graphene.String(required=True)
    product_price = graphene.Float(required=True)
    product_price_bn = graphene.Float()
    product_meta = graphene.String(required=True)
    product_last_price = graphene.Float()
    is_approved = graphene.Boolean()


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductNode)

    @staticmethod
    def mutate(root, info, input=None):
        user = info.context.user
        print(user)
        product_unit = ProductUnit.objects.get(product_unit=input.product_unit)
        product_meta = ProductMeta.objects.get(name=input.product_meta)
        if user.is_anonymous:
            raise Exception('Must Log In!')
        else:
            if user.user_type == 'SF':
                product_instance = Product(product_name=input.product_name,
                                           product_image=input.product_image,
                                           product_description=input.product_description,
                                           product_unit=product_unit,
                                           product_price=input.product_price,
                                           product_meta=product_meta,
                                           is_approved=True, )
                product_instance.save()
                return CreateProduct(product=product_instance)
            else:
                raise Exception('Unauthorized request!')


class ProductCategories(graphene.Mutation):
    category_list = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input=None):
        all_product_categories = [
          {
            "id": 1,
            "name": "Baby",
            "childs": [
              {
                "id": 23,
                "name": "Baby Food",
                "childs": [
                  {
                    "id": 24,
                    "name": "Imported"
                  }
                ]
              },
              {
                "id": 29,
                "name": "Diapers"
              }
            ]
          },
          {
            "id": 2,
            "name": "Stationary",
            "childs": [
              {
                "id": 39,
                "name": "Office Stationaries"
              }
            ]
          }
        ]
        return ProductCategories(category_list=all_product_categories)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    product_categories = ProductCategories.Field()
