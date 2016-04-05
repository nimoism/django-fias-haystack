from __future__ import absolute_import, unicode_literals

from fias.forms import AddressSelect2Field as BaseAddressSelect2Field
from fias_haystack import widgets
from fias_haystack.formatters import get_address_formatter


class AddressSelect2Field(BaseAddressSelect2Field):
    widget = widgets.AddressSelect2

    def __init__(self, *args, **kwargs):
        self.address_formatter = kwargs.pop('address_formatter', get_address_formatter())
        super(AddressSelect2Field, self).__init__(*args, **kwargs)

    def _txt_for_val(self, value):
        if not value:
            return
        obj = self.queryset.get(pk=value)
        text = self.address_formatter.format_verbose(obj)
        return text
