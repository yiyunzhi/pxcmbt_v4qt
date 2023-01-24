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
from gui.utils.class_icon_usage_registry import IconUsageRegistry
from gui.utils.class_i18n_text_usage_registry import I18nTextUsageRegistry


class ThemeStyledUiObject:
    def __init__(self):
        self.iconUsageRegistry = IconUsageRegistry()

    def restyle(self, *args, **kwargs):
        raise NotImplementedError


class I18nUiObject:
    def __init__(self):
        self.i18nUsageRegistry = I18nTextUsageRegistry()

    def translate(self, *args, **kwargs):
        raise NotImplementedError
