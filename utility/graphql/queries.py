import graphene
from graphene_django.types import DjangoObjectType
from ..models import Message


class MessageType(DjangoObjectType):
    class Meta:
        model = Message


class Query(graphene.ObjectType):
    message_list = graphene.List(MessageType, screen_name=graphene.String())

    def resolve_message_list(self, info, **kwargs):
        screen_name = kwargs.get('screen_name')
        return Message.objects.filter(screen_name=screen_name).order_by('-created_on')[:1]
