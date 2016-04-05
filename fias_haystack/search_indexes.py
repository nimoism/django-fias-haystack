from haystack.backends.elasticsearch_backend import ElasticsearchSearchEngine
from haystack.constants import Indexable
from haystack.indexes import SearchIndex

from fias_haystack.db import IndexPostgresqlLoader
from fias_haystack.formatters import get_address_formatter
from fias_haystack.utils import get_haystack_engine


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


haystack_engine = get_haystack_engine()
if issubclass(haystack_engine, ElasticsearchSearchEngine):
    from fias_haystack.elasticsearch.search_indexes import *
else:
    raise NotImplemented('Backend indexes is not implemented')
