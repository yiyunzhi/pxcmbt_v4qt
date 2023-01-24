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
from gui import QtGui


class I18nTextUsageRegistryItem:
    def __init__(self, i18n_ns, i18n_key):
        self.i18nNs = i18n_ns
        self.i18nKey = i18n_key


class I18nTextUsageRegistry:
    def __init__(self):
        self._map = weakref.WeakKeyDictionary()

    def keyrefs(self):
        return self._map.keyrefs()

    @staticmethod
    def build_i18n_text(item: I18nTextUsageRegistryItem, *args, **kwargs):
        return i18n.t('%s.%s' % (item.i18nNs, item.i18nKey))

    def register(self, target_obj, i18n_ns, i18n_key):
        self._map[target_obj] = I18nTextUsageRegistryItem(i18n_ns, i18n_key)

    def unregister(self, target_obj):
        if target_obj in self._map:
            self._map.pop(target_obj)

    def get_i18n_text(self, target_obj, *args, **kwargs):
        _key = target_obj
        _item = self._map.get(_key)
        if _item is None:
            if hasattr(target_obj, 'text'):
                return target_obj.text()
            return None
        else:
            return self.build_i18n_text(_item, *args, **kwargs)
