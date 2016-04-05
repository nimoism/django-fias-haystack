"""Haystack support for django-fias"""

VERSION = (0, 1, 'a', 0)

__version__ = '.'.join(map(str, VERSION))
__author__ = 'Dmitry Puhov'
__contact__ = 'dmitry.puhov@gmail.com'


default_app_config = 'fias_haystack.apps.FiasHaystackConfig'
