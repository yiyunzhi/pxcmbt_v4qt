# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_base.py
# ------------------------------------------------------------------------------
#
# File          : class_base.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import typing
from gui.node_graph.core.define import EnumNodePropWidgetType


class PropertyDef:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.object = kwargs.get('object')
        self.custom = kwargs.get('custom', False)
        self.value = kwargs.get('value')
        self.readonly = kwargs.get('readonly', False)
        self.valueType = kwargs.get('value_type', 'str')
        self.enumTexts = kwargs.get('enum_texts', [])
        self.valueRange = kwargs.get('value_range', [])
        self.category = kwargs.get('category', 'Properties')
        self.getter = kwargs.get('getter')
        self.multiArgs = kwargs.get('multi_args', True)
        self.undoable = kwargs.get('undoable', True)
        if self.getter is not None:
            self.get()
        self.setter = kwargs.get('setter')
        self.visible = kwargs.get('visible', True)

    def get_widget_type(self):
        pass

    def set(self):
        if self.object is None:
            raise AssertionError('object is none')
        if self.setter is None:
            return

        if isinstance(self.setter, str):
            if hasattr(self.object, self.setter):
                _attr = getattr(self.object, self.setter)
                if callable(_attr):
                    _attr(self.object, self.value)
                else:
                    setattr(self.object, self.setter, self.value)
        else:
            if callable(self.setter):
                if isinstance(self.value, (set, tuple, list)) and self.multiArgs:
                    self.setter(*self.value)
                else:
                    self.setter(self.value)

    def get(self):
        if self.object is None:
            raise AssertionError('object is none')
        if self.getter is None:
            return
        if isinstance(self.getter, str):
            if hasattr(self.object, self.getter):
                _attr = getattr(self.object, self.getter)
                if callable(_attr):
                    self.value = _attr(self.object)
                else:
                    self.value = getattr(self.object, self.getter)
        else:
            if callable(self.getter):
                self.value = self.getter()
        return self.value
