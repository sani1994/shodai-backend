import graphene
import graphql_jwt
from product.graphql.schema import Query as product_query
from product.graphql.schema import Mutation as product_mutation
from userProfile.graphql.schema import Query as user_query
from userProfile.graphql.schema import Mutation as user_mutation
from order.graphql.schema import Query as order_query
from order.graphql.schema import Mutation as order_mutation
from utility.graphql.schema import Query as utility_query
from customer_service.graphql.schema import Mutation as customer_service_mutation
from customer_service.graphql.schema import Query as customer_service_query
from offer.graphql.schema import Query as offer_query
from coupon.graphql.schema import Mutation as coupon_mutation


class Query(product_query, user_query, order_query, utility_query, customer_service_query, offer_query):
    # This class will inherit from multiple Queries
    pass


class Mutation(product_mutation, user_mutation, order_mutation, customer_service_mutation, coupon_mutation):
    login_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
