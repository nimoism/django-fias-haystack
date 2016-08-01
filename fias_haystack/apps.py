from __future__ import absolute_import, unicode_literals

from django.apps.config import AppConfig


class FiasHaystackConfig(AppConfig):
    name = 'fias_haystack'

    def ready(self):
        import fias_haystack.conf
