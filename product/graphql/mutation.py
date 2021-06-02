import graphene
from product.models import ProductCategory


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
    product_categories = ProductCategories.Field()
