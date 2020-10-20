import graphene
import graphql_jwt
from product.graphql.schema import Query as product_query
from product.graphql.schema import Mutation as product_mutation
from userProfile.graphql.schema import Query as user_query
from userProfile.graphql.schema import Mutation as user_mutation
from order.graphql.schema import Query as order_query
from order.graphql.schema import Mutation as order_mutation
from utility.graphql.schema import Query as utility_query
from customerService.graphql.schema import Mutation as customerService_mutation
from customerService.graphql.schema import Query as customerService_query
from offer.graphql.schema import Query as offer_query


class Query(product_query, user_query, order_query, utility_query, customerService_query, offer_query):
    # This class will inherit from multiple Queries
    pass


class Mutation(product_mutation, user_mutation, order_mutation, customerService_mutation):
    login_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
