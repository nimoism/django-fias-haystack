from __future__ import absolute_import, unicode_literals

import operator
import six
from django.conf import settings
from django_select2.views import Select2View, NO_ERR_RESP
from fias.models.addrobj import AddrObj
from fias.views import EMPTY_RESULT
from haystack.backends import SQ
from haystack.query import SearchQuerySet


class SuggestByHaystack(Select2View):
    def get_results(self, request, term, page, context):
        sqs = SearchQuerySet().using(settings.FIAS_HAYSTACK_CONNECTION_ALIAS).models(AddrObj)
        cleaned_words = [sqs.query.clean(word.strip()) for word in term.split(' ')]
        query_bits = [SQ(text_auto=word) for word in cleaned_words if word]
        if query_bits:
            sqs = sqs.filter(six.moves.reduce(operator.__or__, query_bits))
        items = sqs
        items = items[:50]
        if not len(items):
            return EMPTY_RESULT
        return (
            NO_ERR_RESP,
            False,
            ((l.aoguid, l.full_name, {'level': l.aolevel}) for l in items)
        )
