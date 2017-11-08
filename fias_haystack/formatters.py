# coding=utf-8
from __future__ import absolute_import, unicode_literals

import functools
import re

from django.conf import settings
from django.utils.module_loading import import_string
from fias.models.addrobj import AddrObj
from fias.models.socrbase import SocrBase


class BaseAddressFormatter(object):
    address_delimiter = ', '

    def _get_obj_path(self, addr_obj):
        path = []
        model = addr_obj._meta.model
        while addr_obj:
            path.append(self._get_obj_path_part(addr_obj))
            try:
                addr_obj = model.objects.get(aoguid=addr_obj.parentguid)
            except model.DoesNotExist:
                addr_obj = None
        path = reversed(path)
        return path

    def _get_obj_path_part(self, addr_obj):
        raise NotImplementedError()

    def format_verbose(self, obj):
        if isinstance(obj, AddrObj):
            return self.format_obj_verbose(obj)
        elif isinstance(obj, dict):
            return self.format_path_verbose(obj)
        else:
            raise AttributeError("Parameter 'obj' must be AddrObj or dict instance")

    def format_obj_verbose(self, addr_obj):
        address_path = self._get_obj_path(addr_obj)
        return self.format_path_verbose(address_path)

    def format_path_index(self, address_path):
        return self.__format_path(self._format_index_address_part, address_path)

    def format_path_verbose(self, address_path):
        return self.__format_path(self._format_verbose_address_part, address_path)

    def __format_path(self, format_address_part_func, address_path):
        formatted_address_path = [format_address_part_func(address_part) for address_part in address_path]
        return self.address_delimiter.join(formatted_address_path)

    def _format_index_address_part(self, addr_obj_info):
        raise NotImplementedError()

    def _format_verbose_address_part(self, addr_obj_info):
        raise NotImplementedError()


class AddressFormatter(BaseAddressFormatter):

    def is_reversed_type(self, addr_obj_info):
        reversed_types = (
            'автономный округ',
            'автономная область',
            'край',
            'область',
            'станица',
        )
        if self._get_type_name(addr_obj_info) in reversed_types:
            return True

    def is_reversed_type_republic(self, addr_obj_info):
        if self._get_type_name(addr_obj_info) not in ('республика', ):
            return None
        official_name = addr_obj_info['official_name']
        return official_name[-2:] == 'ая'

    def is_reversed_type_area(self, addr_obj_info):
        if self._get_type_name(addr_obj_info) not in ('район', ):
            return None
        official_name = addr_obj_info['official_name']
        return official_name[-2:] in ('ий', 'ый')

    def is_reversed_type_highway(self, addr_obj_info):
        if self._get_type_name(addr_obj_info) not in ('шоссе', ):
            return None
        official_name = addr_obj_info['official_name']
        return official_name[-2:] in ('ое', )

    reversed_funcs = (
        is_reversed_type,
        is_reversed_type_area,
        is_reversed_type_republic,
        is_reversed_type_highway,
    )

    def is_full_name_reversed(self, addr_obj_info):
        for reversed_func in self.reversed_funcs:
            if hasattr(reversed_func, 'im_self') or hasattr(reversed_func, '__class__'):
                reversed_func = functools.partial(reversed_func, *[self])
            is_reversed = reversed_func(addr_obj_info)
            if is_reversed is not None:
                return is_reversed
        return False

    not_dottable_symbols = ['.', '-']
    re_not_dottable_symbols = re.compile(r'[{symbols}]'.format(symbols=''.join([re.escape(s) for s in not_dottable_symbols])))

    def is_dottable_short_type(self, short_type):
        if not short_type:
            return False
        return self.re_not_dottable_symbols.search(short_type) is None

    def _get_address_part_format(self, addr_obj_info, dotted_type=False):
        short_type = self._get_type_short_name(addr_obj_info)
        if dotted_type and self.is_dottable_short_type(short_type):
            dot = '.'
        else:
            dot = ''
        if self.is_full_name_reversed(addr_obj_info):
            address_format = '{{name}} {{type}}{dot}'.format(dot=dot)
        else:
            address_format = '{{type}}{dot} {{name}}'.format(dot=dot)
        return address_format

    def _format_full_address_part(self, addr_obj_info):
        type_ = addr_obj_info['full_type']
        name = addr_obj_info['official_name']
        address_format = self._get_address_part_format(addr_obj_info, dotted_type=False)
        formatted = address_format.format(type=type_, name=name)
        return formatted

    def _format_short_address_part(self, addr_obj_info):
        type_ = self._get_type_short_name(addr_obj_info)
        name = addr_obj_info.get('official_name')
        address_format = self._get_address_part_format(addr_obj_info, dotted_type=True)
        formatted = address_format.format(type=type_, name=name)
        return formatted

    def _format_index_address_part(self, addr_obj_info):
        return self._format_full_address_part(addr_obj_info)

    def _format_verbose_address_part(self, addr_obj_info):
        return self._format_short_address_part(addr_obj_info)

    def _get_obj_path_part(self, addr_obj):
        type_ = SocrBase.objects.get(scname=addr_obj.shortname, level=addr_obj.aolevel)
        return {
            'aoguid': addr_obj.aoguid,
            'short_type': addr_obj.shortname.lower(),
            'full_type': type_.socrname.lower(),
            'formal_name': addr_obj.formalname,
            'official_name': addr_obj.offname,
            'item_weight': type_.item_weight,
        }

    def _get_type_name(self, addr_obj_info):
        type_name = addr_obj_info.get('type_name', addr_obj_info.get('full_type'))
        if type_name:
            type_name = type_name.lower()
        return type_name

    def _get_type_short_name(self, addr_obj_info):
        return addr_obj_info.get('type_short_name', addr_obj_info.get('short_type'))


def get_address_formatter(*args, **kwargs) -> BaseAddressFormatter:
    return import_string(settings.FIAS_HAYSTACK_ADDRESS_FORMATTER)(*args, **kwargs)
