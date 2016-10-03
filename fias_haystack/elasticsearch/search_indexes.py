# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.core.validators import EMPTY_VALUES
from elasticstack.fields import CharField
from fias.models.addrobj import AddrObj
from fias.models.house import House
from haystack.indexes import CharField as BaseCharField, IntegerField as BaseIntegerField

from fias_haystack.search_indexes_base import BaseFiasHaystackSearchIndex


class ElasticsearchSearchIndex(BaseFiasHaystackSearchIndex):
    class Meta:
        abstract = True


class AddressIndex(ElasticsearchSearchIndex):
    text = CharField(document=True, analyzer='snowball')
    text_auto = CharField(analyzer='edgengram_analyzer')
    full_name = CharField(analyzer='snowball')
    formalname = CharField(model_attr='formalname', analyzer='snowball')
    offname = CharField(model_attr='offname', null=True, analyzer='snowball')
    shortname = BaseCharField(model_attr='shortname')
    aoguid = BaseCharField(model_attr='aoguid')
    parentguid = BaseCharField(model_attr='parentguid', null=True)
    aolevel = BaseIntegerField(model_attr='aolevel')
    item_weight = BaseIntegerField(model_attr='item_weight')

    def get_model(self):
        return AddrObj

    def index_queryset(self, using=None):
        self.db_helper.pre_index()
        addr_objs = super(AddressIndex, self).index_queryset(using)
        addr_objs = self.db_helper.prepare_queryset(queryset=addr_objs)
        return addr_objs

    def prepare(self, obj):
        cleaned_data = super(AddressIndex, self).prepare(obj)
        address_path = self.db_helper.get_address_path(obj)
        text = self.formatter.format_path_index(address_path)
        cleaned_data['text'] = text
        cleaned_data['text_auto'] = text
        cleaned_data['full_name'] = self.formatter.format_path_verbose(address_path)
        return cleaned_data


class HouseAddressIndex(ElasticsearchSearchIndex):
    text = BaseCharField(document=True)
    name = BaseCharField(stored=False)
    aoguid = BaseCharField(model_attr='aoguid')
    houseguid = BaseCharField(model_attr='houseguid')
    houseid = BaseCharField(model_attr='houseid')
    housenum = BaseCharField(model_attr='housenum', null=True)
    buildnum = BaseCharField(model_attr='buildnum', null=True)
    strucnum = BaseCharField(model_attr='strucnum', null=True)

    def get_model(self):
        return House

    def index_queryset(self, using=None):
        self.db_helper.create_temp_addrobj_index_table()
        houses = super(HouseAddressIndex, self).index_queryset(using)
        houses = self.db_helper.prepare_queryset(houses, 'aoguid_id')
        return houses

    def get_name(self, obj):
        addr_obj_full_name = self.get_addr_obj_full_name(obj)
        name = addr_obj_full_name + ', ' + self.get_house_full_number(obj)
        return name

    def prepare_text(self, obj):
        return self.get_name(obj) + '; ' + obj.scname

    def get_house_full_number(self, obj):
        return '/'.join(filter(lambda x: x not in EMPTY_VALUES, [obj.housenum, obj.buildnum, obj.strucnum]))

    def prepare_name(self, obj):
        return self.get_name(obj)
