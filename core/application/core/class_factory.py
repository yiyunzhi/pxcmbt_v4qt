# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_factory.py
# ------------------------------------------------------------------------------
#
# File          : class_factory.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .exceptions import ClassRegisterError


class _ClassFactoryItem:
    def __init__(self, cls: type, alias=None, ns=None, ns_key='__namespace__'):
        self.name = cls.__name__
        self.alias = alias if alias is not None else self.name
        assert hasattr(cls, ns_key), ClassRegisterError('attribute {} is required'.format(ns_key))
        self.ns = getattr(cls,ns_key) or ns
        self.klass = cls

    @property
    def display_name(self):
        return '{}.{}'.format(self.ns, self.alias)

    @property
    def class_type(self):
        return '{}.{}'.format(self.ns, self.name)


class ClassFactory:
    """
    Node factory that stores all the node types.
    """

    def __init__(self, ns_key='__namespace__'):
        self.__klass = {}
        self._nsKey = ns_key

    @property
    def aliases(self):
        """
        Return aliases assigned to the node types.

        Returns:
            dict: key=alias, value=node type
        """
        return [v.alias for k, v in self.__klass.items()]

    @property
    def names(self):
        return [v.name for k, v in self.__klass.items()]

    @property
    def klass(self):
        """
        Return all registered nodes.

        Returns:
            dict: key=node identifier, value=node class
        """
        return self.__klass

    @property
    def grouped(self):
        _res = dict()
        for k, v in self.__klass.items():
            if v.ns not in _res:
                _res[v.ns] = []
            _res[v.ns].append(v)
        return _res

    def create_class_instance(self, cls_type=None, *args, **kwargs):
        """
        create node object by the node type identifier or alias.

        Args:
            cls_type (str): node type or optional alias name.

        Returns:
            NodeGraphQt.NodeObject: new node object.
        """
        if cls_type is None or cls_type not in self.__klass:
            return
        _fi = self.__klass[cls_type]

        _class = _fi.klass
        if _class:
            return _class(*args, **kwargs)

    def register(self, cls, alias=None, namespace=None, ns_override=False):
        """
        register the node.

        Args:
            cls (type): node object.
            alias (str): custom alias for the node identifier (optional).
            namespace (str): custom namespace for the class.
            ns_override (bool): if override the attribute __namespace__
        """
        if cls is None:
            return
        if getattr(cls, self._nsKey) is None and namespace is None:
            raise ClassRegisterError(
                'for node type "{}" {} attribute is required! '
                'Please specify a {}.'
                .format(cls, self._nsKey, self._nsKey))
        _ns = getattr(cls, self._nsKey) or namespace
        if ns_override and namespace:
            setattr(cls, self._nsKey, namespace)
        _cls_item = _ClassFactoryItem(cls, alias, _ns, self._nsKey)

        if self.__klass.get(_cls_item.class_type):
            raise ClassRegisterError(
                'node type "{}" already registered to "{}"! '
                'Please specify a new plugin class name or __identifier__.'
                .format(_cls_item.class_type, self.__klass[_cls_item.class_type]))
        self.__klass[_cls_item.class_type] = _cls_item

    def clear_registered(self):
        """
        clear out registered nodes, to prevent conflicts on reset.
        """
        self.__klass.clear()
