from __future__ import absolute_import, unicode_literals

from fias.widgets import AddressSelect2 as BaseAddressSelect2


class AddressSelect2(BaseAddressSelect2):

    options = {}

    def init_options(self):
        super(AddressSelect2, self).init_options()
        self.options.update({
            'autocomplete': 'off',
            'minimumInputLength': 1,
        })
