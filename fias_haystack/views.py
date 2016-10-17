# coding=utf-8

from __future__ import absolute_import, unicode_literals

import operator
from string import strip

import six
from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.http.response import JsonResponse
from django.views.generic.list import BaseListView
from fias.models.addrobj import AddrObj
from haystack.backends import SQ
from haystack.query import SearchQuerySet


class HaystackResponseView(BaseListView):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        if len(term) > 0:
            sqs = SearchQuerySet().using(settings.FIAS_HAYSTACK_CONNECTION_ALIAS).models(AddrObj)
            aolevels = request.GET.get('aolevels', '')
            aolevels = map(int, filter(lambda s: s not in EMPTY_VALUES, map(strip, aolevels.split(','))))
            if aolevels:
                sqs = sqs.filter(aolevel__in=aolevels)
            socrs = request.GET.get('socrs', '')
            socrs = map(strip, socrs.split(','))
            if socrs:
                sqs = sqs.filter(shortname__in=socrs)
            cleaned_words = [sqs.query.clean(word.strip()) for word in term.split(' ')]
            query_bits = [SQ(text_auto=word) for word in cleaned_words if word]
            if query_bits:
                sqs = sqs.filter(six.moves.reduce(operator.__or__, query_bits))
            items = sqs
            items = items[:50]
        else:
            items = []
        return JsonResponse({
            'results': [
                {'id': l.aoguid, 'text': l.full_name, 'level': l.aolevel} for l in items
            ],
            'more': False
        })
