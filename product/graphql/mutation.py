import graphene
from product.graphql.queries import ProductNode
from product.models import Product, ProductCategory, ProductMeta
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
    category_list = graphene.types.generic.GenericScalar()

    @staticmethod
    def mutate(root, info, input=None):
        category_list = []
        primary_categories = ProductCategory.objects.filter(parent=None, is_approved=True)
        for category in primary_categories:
            primary_category = {'id': category.id,
                                'name': category.type_of_product,
                                'image': category.img.url if category.img else None,
                                'subcategories': []}
            temporary_category = primary_category
            previous_categories = [primary_category]
            all_children_found = False
            while not all_children_found:
                child_categories = ProductCategory.objects.filter(parent=temporary_category['id'], is_approved=True)
                if child_categories:
                    for child in child_categories:
                        child_category = {'id': child.id,
                                          'name': child.type_of_product,
                                          'image': child.img.url if child.img else None,
                                          'subcategories': []}
                        temporary_category['subcategories'].append(child_category)
                        previous_categories.append(child_category)
                    temporary_category = previous_categories[-1]
                    del previous_categories[-1]
                else:
                    if primary_category['id'] == previous_categories[-1]['id']:
                        all_children_found = True
                    temporary_category = previous_categories[-1]
                    del previous_categories[-1]
            category_list.append(primary_category)
        return ProductCategories(category_list=category_list)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    product_categories = ProductCategories.Field()
