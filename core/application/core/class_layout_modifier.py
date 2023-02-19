# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_layout_modifier.py
# ------------------------------------------------------------------------------
#
# File          : class_layout_modifier.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import importlib


class LayoutModifier:
    def __init__(self, **kwargs):
        self.uid = kwargs.get('uid', None)
        self.module = kwargs.get('module', None)
        self.class_ = kwargs.get('class', None)
        self.target = kwargs.get('target', None)
        self.policy = kwargs.get('policy', None)

    def import_module(self):
        _module = importlib.import_module(self.module)
        return getattr(_module, self.class_)
