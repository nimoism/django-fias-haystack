from __future__ import unicode_literals

import inspect
import types

import six
from django.conf import settings
import importlib
from django.utils.module_loading import module_has_submodule


def get_haystack_engine():
    connection_alias = settings.FIAS_HAYSTACK_CONNECTION_ALIAS
    connection_config = settings.HAYSTACK_CONNECTIONS.get(connection_alias)
    engine_name = connection_config['ENGINE']
    engine_module_name, engine_class_name = engine_name.rsplit('.', 1)
    engine_module = importlib.import_module(engine_module_name)
    engine_class = getattr(engine_module, engine_class_name)
    return engine_class


class ExcludedIndexes(object):

    def __init__(self, included_indexes=None):
        if included_indexes is None:
            included_indexes = []
        self.included_indexes = []
        for included_index in included_indexes:
            if not isinstance(included_index, types.UnicodeType):
                included_index = six.u(included_index)
            self.included_indexes.append(included_index)
        self._excluded = None
        super(ExcludedIndexes, self).__init__()

    def _get_excluded(self):
        if self._excluded is None:
            all_indexes = self._collect_indexes()
            excluded_indexes = list(set(all_indexes) - set(self.included_indexes))
            self._excluded = excluded_indexes
        return self._excluded

    def __iter__(self):
        return self._get_excluded()

    def __contains__(self, item):
        return item in self._get_excluded()

    def _collect_indexes(self):
        """
        Partial duplicates UnifiedIndex.collect_indexes()
        """
        from haystack.utils.app_loading import haystack_get_app_modules
        all_indexes = []
        for app_mod in haystack_get_app_modules():
            try:
                search_index_module = importlib.import_module("%s.search_indexes" % app_mod.__name__)
            except ImportError:
                if module_has_submodule(app_mod, 'search_indexes'):
                    raise
                continue

            for item_name, item in inspect.getmembers(search_index_module, inspect.isclass):
                if getattr(item, 'haystack_use_for_indexing', False) and getattr(item, 'get_model', None):
                    # We've got an index. Check if we should be ignoring it.
                    class_path = "%s.search_indexes.%s" % (app_mod.__name__, item_name)
                    all_indexes.append(class_path)
        return all_indexes
