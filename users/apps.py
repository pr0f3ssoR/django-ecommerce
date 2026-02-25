from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'


    def ready(self):

        from . import signals

        from . import stripe_api
        

        return super().ready()
