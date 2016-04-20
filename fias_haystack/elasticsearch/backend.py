from __future__ import absolute_import, unicode_literals

import haystack
from django.conf import settings
from elasticsearch.exceptions import NotFoundError
from elasticstack.backends import ConfigurableElasticBackend, ConfigurableElasticSearchEngine
from fias.models.addrobj import AddrObj
from haystack.utils import get_model_ct


class FiasHaystackElasticsearchSearchBackend(ConfigurableElasticBackend):
    def setup(self):
        """
        Same as parent method except removed `_boost` parameter in mapping for ES 2 support
        """
        try:
            self.existing_mapping = self.conn.indices.get_mapping(index=self.index_name)
        except NotFoundError:
            pass
        except Exception:
            if not self.silently_fail:
                raise

        unified_index = haystack.connections[self.connection_alias].get_unified_index()
        self.content_field_name, field_mapping = self.build_schema(unified_index.all_searchfields())
        current_mapping = {
            'modelresult': {
                'properties': field_mapping,
            }
        }

        if current_mapping != self.existing_mapping:
            try:
                # Make sure the index is there first.
                self.conn.indices.create(index=self.index_name, body=self.DEFAULT_SETTINGS, ignore=400)
                self.conn.indices.put_mapping(index=self.index_name, doc_type='modelresult', body=current_mapping)
                self.existing_mapping = current_mapping
            except Exception:
                if not self.silently_fail:
                    raise

        self.setup_complete = True

    def build_search_kwargs(self, *args, **kwargs):
        kwargs = super(FiasHaystackElasticsearchSearchBackend, self).build_search_kwargs(*args, **kwargs)

        query = kwargs.get('query', {}).get('filtered').get('query')
        query_string = query.get('query_string', {})
        query_string.update({
            'default_operator': 'OR',
            'auto_generate_phrase_queries': False,
            'analyze_wildcard': False,
        })

        score_script = settings.FIAS_HAYSTACK_ELASTICSEARCH_SCORE_SCRIPT
        if score_script:
            models = kwargs.get('query', {}).get('filtered', {}).get('filter', {}).get('terms', {}).get('django_ct')
            if models and len(models) == 1 and get_model_ct(AddrObj) in models:
                kwargs['query'] = {
                    'function_score': {
                        'query': kwargs.pop('query'),
                        'boost_mode': 'replace',
                        'script_score': {
                            'script': {
                                'lang': 'expression',
                                'inline': score_script,
                            }
                        }
                    }
                }
        return kwargs


class FiasHaystackElasticsearchSearchEngine(ConfigurableElasticSearchEngine):
    backend = FiasHaystackElasticsearchSearchBackend
