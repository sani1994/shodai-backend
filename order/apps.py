from django.apps import AppConfig


class OrderConfig(AppConfig):
    name = 'order'

    def ready(self):
        from order import signals
