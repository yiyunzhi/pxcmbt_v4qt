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
from pubsub import pub
from gui.utils.class_icon_usage_registry import IconUsageRegistry
from gui.utils.class_i18n_text_usage_registry import I18nTextUsageRegistry


class ThemeStyledUiObject:
    def __init__(self):
        self.iconUsageRegistry = IconUsageRegistry()
        pub.subscribe(self.on_theme_changed, 'theme')

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        raise NotImplementedError


class I18nUiObject:
    def __init__(self):
        self.i18nUsageRegistry = I18nTextUsageRegistry()
        pub.subscribe(self.on_locale_changed, 'locale')

    def on_locale_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        raise NotImplementedError
