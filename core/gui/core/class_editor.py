# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_editor.py
# ------------------------------------------------------------------------------
#
# File          : class_editor.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtCore


class EditorBase(QtCore.QObject):
    def __init__(self, parent=None, undo_stack=None):
        super().__init__(parent)
        self.content = None
        self.view = None

    def set_content(self):
        pass
