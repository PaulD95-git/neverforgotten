from django.apps import AppConfig
from importlib import import_module


class MemorialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'memorial'

    def ready(self):
        _ = import_module('memorial.signals')

