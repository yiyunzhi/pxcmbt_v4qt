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


class IconUsageRegistry:
    def __init__(self):
        self._map = weakref.WeakKeyDictionary()

    def keyrefs(self):
        return self._map.keyrefs()

    @staticmethod
    def build_icon(item: IconUsageRegistryItem, *args, **kwargs):
        if item.iconNs == 'fa':
            return qta.icon(item.iconName, **kwargs)
        else:
            return QtGui.QIcon(item.iconName)

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
