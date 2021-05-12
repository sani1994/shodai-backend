import graphene
from django.utils.text import slugify
from graphene.types import generic

from .queries import ProductNode
from ..models import Product, ProductMeta, ProductCategory
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
    category_list = generic.GenericScalar()

    @staticmethod
    def mutate(root, info, input=None):
        categories = list(ProductCategory.objects.filter(is_approved=True).values('id',
                                                                                  'type_of_product',
                                                                                  'parent'))
        category_tree = []
        temporary_categories = categories.copy()
        for category in temporary_categories:
            if categories:
                if not category['parent']:
                    primary_category = {'id': category['id'],
                                        'name': category['type_of_product'],
                                        'subcategories': []}
                    categories.remove(category)
                    temporary_category = primary_category
                    previous_categories = [primary_category]
                    all_children_found = False
                    while not all_children_found:
                        for child in temporary_categories:
                            if child['parent'] and child['parent'] == temporary_category['id']:
                                child_category = {'id': child['id'],
                                                  'name': child['type_of_product'],
                                                  'subcategories': []}
                                temporary_category['subcategories'].append(child_category)
                                categories.remove(child)
                                previous_categories.append(temporary_category)
                                temporary_category = child_category
                                break
                        else:
                            if temporary_category['id'] == previous_categories[-1]['id']:
                                all_children_found = True
                            temporary_category = previous_categories[-1]
                            del previous_categories[-1]
                            temporary_categories = categories.copy()

                    category_tree.append(primary_category)
            else:
                break

        return ProductCategories(category_list=category_tree)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    product_categories = ProductCategories.Field()
