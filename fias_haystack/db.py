from __future__ import absolute_import, unicode_literals

import string

from django import db
from django.conf import settings
from fias.models.socrbase import SocrBase


def get_index_db_loader():
    return settings.FIAS_HAYSTACK_INDEX_DB_LOADER


class IndexDbLoader(object):

    def __init__(self, index):
        self.index = index

    def pre_index(self):
        raise NotImplementedError()

    def prepare_queryset(self, queryset, temp_aoguid_field='aoguid'):
        raise NotImplementedError()

    def get_address_path(self, addr_obj):
        raise NotImplementedError()


class IndexSimpleLoader(IndexDbLoader):
    def pre_index(self):
        pass

    def prepare_queryset(self, queryset, temp_aoguid_field='aoguid'):
        return queryset

    def get_address_path(self, addr_obj):
        model = self.index.get_model()
        path = []
        while addr_obj:
            path.append({
                'aolevel': addr_obj.aolevel,
                'short_type': addr_obj.shortname,
                'full_type': SocrBase.objects.get(scname=addr_obj.shortname).socrname,
                'formal_name': addr_obj.formalname,
                'official_name': addr_obj.official_name,
            })
            try:
                addr_obj = model.objects.get(aoguid=addr_obj.parentguid)
            except model.DoesNotExist:
                addr_obj = None
        path = reversed(path)
        return path


class IndexPostgresqlLoader(IndexDbLoader):
    part_delimiter = '#'

    def _create_temp_addrobj_index_table(self):
        sql = """
            DROP SEQUENCE IF EXISTS fias_addrobj_docid_seq;
            DROP TABLE IF EXISTS temp_fias_addrobj_index;

            CREATE TEMPORARY SEQUENCE fias_addrobj_docid_seq;
            CREATE TEMP TABLE temp_fias_addrobj_index (
                aoguid uuid PRIMARY KEY,
                aolevel integer,
                aolevels varchar(255),
                short_types varchar(255),
                full_types varchar(255),
                formal_names varchar(255),
                official_names varchar(255),
                item_weight integer
            );

            WITH RECURSIVE fias_addrobj_index (
                    docid, aoguid, aolevel, aolevels, short_types, full_types, formal_names, official_names, item_weight
            )
            AS (
                SELECT DISTINCT ON (ao.aoguid)
                    NEXTVAL('fias_addrobj_docid_seq') AS docid,
                    ao.aoguid,
                    ao.aolevel,
                    ao.aolevel::TEXT AS aolevels,
                    sn.scname::TEXT AS short_types,
                    sn.socrname::TEXT AS full_types,
                    ao.formalname::TEXT AS formal_names,
                    ao.offname::TEXT AS official_names,
                    sn.item_weight
                FROM fias_addrobj AS ao
                INNER JOIN fias_socrbase AS sn ON (sn.scname = ao.shortname AND sn.level = ao.aolevel)
                WHERE aolevel = 1 AND livestatus = TRUE
            UNION
                SELECT DISTINCT ON (child.aoguid)
                    NEXTVAL('fias_addrobj_docid_seq') AS docid,
                    child.aoguid,
                    child.aolevel,
                    fias_addrobj_index.aolevels::TEXT || '{delimiter}' || child.aolevel::TEXT AS aolevels,
                    fias_addrobj_index.short_types::TEXT || '{delimiter}' || sn.scname::TEXT AS short_types,
                    fias_addrobj_index.full_types::TEXT || '{delimiter}' || sn.socrname::TEXT AS full_types,
                    fias_addrobj_index.formal_names::TEXT || '{delimiter}' || child.formalname AS formal_names,
                    fias_addrobj_index.official_names::TEXT || '{delimiter}' || child.offname AS official_names,
                    sn.item_weight
                FROM fias_addrobj AS child
                INNER JOIN
                    fias_socrbase AS sn ON (sn.scname = child.shortname AND sn.level = child.aolevel),
                    fias_addrobj_index
                WHERE child.parentguid = fias_addrobj_index.aoguid AND livestatus = TRUE
            )
            INSERT INTO temp_fias_addrobj_index
                SELECT
                    aoguid,
                    aolevel,
                    aolevels,
                    short_types,
                    full_types,
                    formal_names,
                    official_names,
                    item_weight
                FROM
                    fias_addrobj_index;
        """.format(delimiter=self.part_delimiter)
        connection = db.connections[settings.FIAS_DATABASE_ALIAS]
        cursor = connection.cursor()
        cursor.execute(sql)

    def pre_index(self):
        self._create_temp_addrobj_index_table()

    def prepare_queryset(self, queryset, temp_aoguid_field='aoguid'):
        model = self.index.get_model()
        db_table = model._meta.db_table
        # check for SQL-injection
        for name in [db_table, temp_aoguid_field]:
            if {';', ' '} & set(name):
                raise RuntimeError('Wrong name: {}'.format(name))

        connection = db.connections[settings.FIAS_DATABASE_ALIAS]

        queryset = queryset.extra(
            select={
                'aolevels': 'temp_fias_addrobj_index.aolevels',
                'short_types': 'temp_fias_addrobj_index.short_types',
                'full_types': 'temp_fias_addrobj_index.full_types',
                'formal_names': 'temp_fias_addrobj_index.formal_names',
                'official_names': 'temp_fias_addrobj_index.official_names',
                'item_weight': 'temp_fias_addrobj_index.item_weight',
            },
            tables=['temp_fias_addrobj_index'],
            where=['temp_fias_addrobj_index.aoguid = %s.%s' %
                   (connection.ops.quote_name(db_table), connection.ops.quote_name(temp_aoguid_field))]
        )
        return queryset

    def get_address_path(self, addr_obj):
        aolevels_parts = map(int, addr_obj.aolevels.split(self.part_delimiter))
        short_types_parts = map(lambda x: x.strip().lower(), addr_obj.short_types.split(self.part_delimiter))
        full_types_parts = map(lambda x: x.strip().lower(), addr_obj.full_types.split(self.part_delimiter))
        formal_names_parts = map(string.strip, addr_obj.formal_names.split(self.part_delimiter))
        if addr_obj.official_names:
            official_names_parts = map(string.strip, addr_obj.official_names.split(self.part_delimiter))
        else:
            official_names_parts = list(formal_names_parts)
        path_parts = [aolevels_parts, short_types_parts, full_types_parts, formal_names_parts, official_names_parts]
        parts_lengths = [len(p) for p in path_parts]
        if min(parts_lengths) != max(parts_lengths):
            raise RuntimeError("Address object parts has different lengths")
        path_list = zip(*path_parts)
        path_part_keys = ['aolevel', 'short_type', 'full_type', 'formal_name', 'official_name']
        path_dict_list = [dict(zip(path_part_keys, path_part)) for path_part in path_list]
        return path_dict_list
