from __future__ import absolute_import, unicode_literals

from fias_haystack.db import IndexPostgresqlLoader
from fias_haystack.formatters import get_address_formatter
from haystack.constants import Indexable
from haystack.indexes import SearchIndex


class BaseFiasHaystackSearchIndex(SearchIndex, Indexable):
    class Meta:
        abstract = True

    @property
    def db_helper(self):
        if not hasattr(self, '_db_helper'):
            setattr(self, '_db_helper', IndexPostgresqlLoader(self))
        return getattr(self, '_db_helper')

    @property
    def formatter(self):
        if not hasattr(self, '_formatter'):
            setattr(self, '_formatter', get_address_formatter())
        return getattr(self, '_formatter')
