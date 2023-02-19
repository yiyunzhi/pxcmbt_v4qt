# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : editor_stc.py
# ------------------------------------------------------------------------------
#
# File          : editor_stc.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.core.class_editor import EditorBase


class STCEditor(EditorBase):
    def __init__(self, parent=None, undo_stack=None, editor_flag=None):
        EditorBase.__init__(self, parent, undo_stack, editor_flag)

    def on_editor_flag_changed(self):
        pass

    def set_content(self):
        pass

    def restore_content(self):
        pass

    def ensure_view(self):
        pass
