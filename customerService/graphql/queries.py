import graphene
from ..models import CustomerQuery
from .mutation import CustomerQueryType


class Query(graphene.ObjectType):
    query_list = graphene.List(CustomerQueryType)

    def resolve_query_list(self, info):
        return CustomerQuery.objects.all()
