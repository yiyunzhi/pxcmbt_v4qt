# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_welcome_mc.py
# ------------------------------------------------------------------------------
#
# File          : pane_welcome_mc.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.core.class_base import ZViewManager, ZViewContentContainer


class WelcomeContentContainer(ZViewContentContainer):
    def __init__(self, **kwargs):
        ZViewContentContainer.__init__(self, **kwargs)

    def transform_data(self):
        return self._content


class WelcomeViewManager(ZViewManager):
    def __init__(self, **kwargs):
        ZViewManager.__init__(self, **kwargs)
