from django.apps import AppConfig
from django.core.signals import request_started


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from config.utils.utils import log_request

        request_started.connect(log_request)
