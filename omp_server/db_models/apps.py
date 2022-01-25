from django.apps import AppConfig


class DbModelsConfig(AppConfig):
    name = 'db_models'

    def ready(self):
        # signals are imported, so that they are defined and can be used
        from db_models import receivers
