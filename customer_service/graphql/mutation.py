import graphene
from graphene_django import DjangoObjectType

from ..models import CustomerQuery


class CustomerQueryType(DjangoObjectType):
    class Meta:
        model = CustomerQuery


class CustomerQueryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    contact_number = graphene.String(required=True)
    subject = graphene.String(required=True)
    message = graphene.String(required=True)


class CreateCustomerQuery(graphene.Mutation):
    class Arguments:
        input = CustomerQueryInput(required=True)

    question = graphene.Field(CustomerQueryType)

    @staticmethod
    def mutate(root, info, input=None):
        question_instance = CustomerQuery(name=input.name,
                                          email=input.email,
                                          contact_number=input.contact_number,
                                          subject=input.subject,
                                          message=input.message,
                                          )
        question_instance.save()
        return CreateCustomerQuery(question=question_instance)


class Mutation(graphene.ObjectType):
    create_customer_query = CreateCustomerQuery.Field()
