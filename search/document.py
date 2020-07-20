from django_elasticsearch_dsl import Index, fields
from django_elasticsearch_dsl.documents import Document
from django_elasticsearch_dsl.registries import registry

from product.models import Product, ProductMeta


@registry.register_document
class ProductDocument(Document):
    product_meta = fields.NestedField(properties={
        'name': fields.TextField(),
        'pk': fields.IntegerField(),
    }, include_in_root=True)

    class Index:
        name = 'products'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Product
        fields = [
            'product_name',
        ]
        related_models = [ProductMeta]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Product instance(s) from the related model."""
        if isinstance(related_instance, ProductMeta):
            return related_instance.product_set.all()

# @registry.register_document
# class ProductMetaDocument(Document):
#     class Index:
#         name = 'productmeta'
#         settings = {'number_of_shards': 1,
#                     'number_of_replicas': 0}
#
#     class Django:
#         model = ProductMeta
#         fields = [
#             'name',
#         ]
