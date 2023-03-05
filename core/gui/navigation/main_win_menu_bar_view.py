# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : mb_app.py
# ------------------------------------------------------------------------------
#
# File          : mb_app.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtWidgets
from core.gui.core.class_base import ZView


class AppMenubar(QtWidgets.QMenuBar, ZView):
    def __init__(self, parent=None):
        QtWidgets.QMenuBar.__init__(self, parent)
        self.zViewTitle = 'AppMainMenubar'
