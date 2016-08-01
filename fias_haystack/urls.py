from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from fias_haystack.views import HaystackResponseView


urlpatterns = [
    url(r'^suggest\.json$', HaystackResponseView.as_view(), name='suggest'),
    # url(r'^suggest-area.json$', HaystackGetAreasView.as_view(), name='suggest-area'),
]
