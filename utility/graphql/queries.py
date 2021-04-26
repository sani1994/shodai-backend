import graphene
from django.utils import timezone
from graphene_django.types import DjangoObjectType
from utility.models import Message, Banner


class MessageType(DjangoObjectType):
    class Meta:
        model = Message


class BannerType(DjangoObjectType):
    class Meta:
        model = Banner
        fields = ['id', 'banner_img', 'banner_url', 'offer']


class Query(graphene.ObjectType):
    message_list = graphene.List(MessageType, screen_name=graphene.String())
    banner_list = graphene.List(BannerType)

    def resolve_message_list(self, info, **kwargs):
        screen_name = kwargs.get('screen_name')
        return Message.objects.filter(screen_name=screen_name).order_by('-created_on')[:1]

    def resolve_banner_list(self, info):
        today = timezone.now()
        all_banners = Banner.objects.filter(is_approved=True,
                                            banner_show_starts_in__lte=today,
                                            banner_show_ends_in__gte=today)
        return all_banners
