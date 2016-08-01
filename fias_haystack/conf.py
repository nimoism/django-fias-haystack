# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from appconf.base import AppConf


class FiasHaystackAppConf(AppConf):
    CONNECTION_ALIAS = 'fias'
    ADDRESS_FORMATTER = 'fias_haystack.formatters.AddressFormatter'
    ELASTICSEARCH_SCORE_SCRIPT = "_score * ((doc['item_weight'].value / 64 - 1) * 0.2 + 1)"

    class Meta(object):
        prefix = 'fias_haystack'
