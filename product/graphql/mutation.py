import graphene
from django.utils.text import slugify
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
    category_list = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input=None):
        category_list = []
        parent = ProductCategory.objects.filter(parent=None, is_approved=True)
        child = ProductCategory.objects.filter(parent__isnull=False, is_approved=True)
        for p in parent:
            parent_category = {'id': p.id,
                               'name': p.type_of_product,
                               'children': []}
            for c in child:
                for item in child:
                    if c.id == item.parent.id:
                        data = {'id': c.id,
                                'name': c.type_of_product,
                                'children': [{'id': item.id,
                                              'name': item.type_of_product,
                                              'children': []}]}
                        # search for the parent id in category_list and store child info
                    else:
                        data = {'id': c.id,
                                'name': c.type_of_product,
                                'children': []}
                        if parent_category['id'] == c.parent.id:
                            parent_category['children'].append(data)

            category_list.append(parent_category)
        return ProductCategories(category_list=category_list)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    product_categories = ProductCategories.Field()
