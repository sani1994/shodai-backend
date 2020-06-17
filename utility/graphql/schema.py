import graphene

from .queries import Query
# from .mutation import Mutation

schema = graphene.Schema(query=Query)