from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from fias_haystack.views import SuggestByHaystack

urlpatterns = [
    url(r'^suggest_haystack', SuggestByHaystack.as_view(), name='suggest_by_haystack'),
]
