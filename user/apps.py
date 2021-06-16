from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'
    icon_name = 'face'

    def ready(self):
        from user import signals  # noqa
