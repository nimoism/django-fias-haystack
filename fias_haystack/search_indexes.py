from __future__ import absolute_import, unicode_literals

from haystack.backends.elasticsearch_backend import ElasticsearchSearchEngine

from fias_haystack.utils import get_haystack_engine


haystack_engine = get_haystack_engine()
if issubclass(haystack_engine, ElasticsearchSearchEngine):
    from fias_haystack.elasticsearch.search_indexes import *  # NOQA
else:
    raise NotImplemented('Backend indexes is not implemented')
