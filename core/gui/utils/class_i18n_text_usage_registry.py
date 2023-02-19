# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_icon_usage_regestry.py
# ------------------------------------------------------------------------------
#
# File          : class_icon_usage_regestry.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import weakref
import i18n
from core.gui.qtimp import QtGui


class I18nTextUsageRegistryItem:
    def __init__(self, i18n_ns, i18n_key, func_to_set=None):
        self.i18nNs = i18n_ns
        self.i18nKey = i18n_key
        self.funcToSet = func_to_set


class I18nTextUsageRegistry:
    def __init__(self):
        self._map = weakref.WeakKeyDictionary()

    def keyrefs(self):
        return self._map.keyrefs()

    @staticmethod
    def build_i18n_text(wr_obj, item: I18nTextUsageRegistryItem, *args, **kwargs):
        _i18n_text = I18nTextUsageRegistry.get_i18n(item.i18nNs, item.i18nKey)
        if item.funcToSet is None:
            return _i18n_text
        else:
            if hasattr(wr_obj, item.funcToSet):
                getattr(wr_obj, item.funcToSet)(_i18n_text)

    def update_i18n_text(self, obj):
        _key = obj
        _item = self._map.get(_key)
        if _item is not None:
            if _item.funcToSet is not None and hasattr(_key, _item.funcToSet):
                _i18n_text = I18nTextUsageRegistry.get_i18n(_item.i18nNs, _item.i18nKey)
                getattr(_key, _item.funcToSet)(_i18n_text)

    @staticmethod
    def get_i18n(ns, key):
        return i18n.t('%s.%s' % (ns, key))

    def register(self, target_obj, i18n_ns, i18n_key, func_to_set=None, do_update=False):
        self._map[target_obj] = I18nTextUsageRegistryItem(i18n_ns, i18n_key, func_to_set)
        if do_update:
            self.update_i18n_text(target_obj)

    def unregister(self, target_obj):
        if target_obj in self._map:
            self._map.pop(target_obj)

    def get_i18n_text(self, target_obj, *args, **kwargs):
        _key = target_obj
        _item = self._map.get(_key)
        if _item is None:
            if hasattr(target_obj, 'text'):
                return target_obj.text()
            return '-'
        else:
            return I18nTextUsageRegistry.get_i18n(_item.i18nNs, _item.i18nKey)
