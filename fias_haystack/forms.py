from __future__ import absolute_import, unicode_literals

from django.forms.fields import ChoiceField
from fias.config import SUGGEST_VIEW
from fias_haystack import widgets
from fias_haystack.formatters import get_address_formatter


class AddressSelect2Field(ChoiceField):
    widget = widgets.AddressSelect2Widget(data_view=SUGGEST_VIEW)

    def __init__(self, *args, **kwargs):
        self.address_formatter = kwargs.pop('address_formatter', None)
        if not self.address_formatter:
            self.address_formatter = get_address_formatter()
        super(AddressSelect2Field, self).__init__(*args, **kwargs)
