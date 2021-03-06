import graphene

from .mutation import Mutation
from .queries import Query

schema = graphene.Schema(query=Query, mutation=Mutation)
