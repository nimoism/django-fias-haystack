from __future__ import absolute_import, unicode_literals

from django_select2.forms import HeavySelect2Widget
from fias.config import SUGGEST_VIEW


class AddressSelect2Widget(HeavySelect2Widget):
    options = {}
    data_view = SUGGEST_VIEW

    def init_options(self):
        super(AddressSelect2Widget, self).init_options()
        self.options.update({
            'autocomplete': 'off',
            'minimumInputLength': 1,
        })
