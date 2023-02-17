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
from gui import QtGui
import gui.qtawesome as qta


class IconUsageRegistryItem:
    def __init__(self, icon_ns, icon_name):
        self.iconNs = icon_ns
        self.iconName = icon_name
        self._cache = None

    def get_cache(self):
        return self._cache

    def set_cache(self, cache):
        self._cache = cache

    def clear_cache(self):
        self._cache = None


class IconUsageRegistry:
    def __init__(self):
        self._map = weakref.WeakKeyDictionary()

    def keyrefs(self):
        return self._map.keyrefs()

    @staticmethod
    def build_icon(item: IconUsageRegistryItem, *args, **kwargs):
        _cached = item.get_cache()
        _force = kwargs.get('force', False)
        if _force:
            item.clear_cache()
        if _cached is None:
            if item.iconNs == 'fa':
                _icon = qta.icon(item.iconName, **kwargs)
            else:
                _icon = QtGui.QIcon(item.iconName)
            item.set_cache(_icon)
        else:
            _icon = _cached
        return _icon

    def register(self, target_obj, icon_ns, icon_name):
        self._map[target_obj] = IconUsageRegistryItem(icon_ns, icon_name)

    def unregister(self, target_obj):
        if target_obj in self._map:
            self._map.pop(target_obj)

    def get_icon(self, target_obj, *args, **kwargs):
        _key = target_obj
        _item = self._map.get(_key)
        if _item is None:
            return None
        else:
            return self.build_icon(_item, *args, **kwargs)
