# -*- coding: utf-8 -*-
import re

from bson import ObjectId
from eve.io.mongo import Validator as Base
from eve.utils import config, str_type
from flask import current_app as app


class Validator(Base):
    def _validate_mapping(self, mapping, field, value):
        pass

    def _validate_type_objectid(self, field, value):
        """ Enables validation for `objectid` schema attribute.

        :param unique: Boolean, whether the field value should be
                       unique or not.
        :param field: field name.
        :param value: field value.
        """
        if not (re.match('[A-Fa-f0-9]{24}', value) or isinstance(value, ObjectId)):
            self._error(field, "value '%s' cannot be converted to a ObjectId"
                        % value)

    def _is_value_unique(self, unique, field, value, query):
        if unique:
            query = { 'must':{'match':{}}}
            query['must']['match'][field] = value
            resource_config = config.DOMAIN[self.resource]
            if resource_config['soft_delete']:
                if 'should' not in query:
                    query['should'] = []
                subquery = {'bool': {'must_not': {'match': {}}}}
                subquery['bool']['must_not']['match'][config.DELETED] = True
                query['should'].append(subquery)
            if self._id:
                if 'should' not in query:
                    query['should'] = []
                id_field = resource_config['id_field']
                subquery = {'bool': {'must_not': {'match': {}}}}
                subquery['bool']['must_not']['match'][id_field] = self._id
                query['should'].append(subquery)
            query = {'query':{'bool':query}, 'size':0 }
            datasource, _, _, _ = app.data.datasource(self.resource)
            hits = app.data.es.search(body=query)
            print hits
            if hits['hits']['total'] > 0:
                self._error(field, "value '%s' is not unique" % value)

