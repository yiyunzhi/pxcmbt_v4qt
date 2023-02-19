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
from core.gui.qtimp import QtCore, QtGui


class EditorBase(QtCore.QObject):
    def __init__(self, parent=None, undo_stack=None, editor_flag=0):
        super().__init__(parent)
        self.editorFlag = editor_flag
        self._content = None
        self._view = None
        self._undoStack = undo_stack
        self._contentUndoStack = QtGui.QUndoStack(self)

    def set_editor_flag(self, flag, on=True):
        if on:
            self.editorFlag |= flag
        else:
            self.editorFlag &= ~flag
        self.on_editor_flag_changed()

    def has_editor_flag(self, flag):
        return (self.editorFlag & flag) != 0

    def reset_editor_flag(self):
        self.editorFlag = 0
        self.on_editor_flag_changed()

    def on_editor_flag_changed(self):
        raise NotImplementedError

    def set_content(self, *args, **kwargs):
        raise NotImplementedError

    def restore_content(self, *args, **kwargs):
        raise NotImplementedError

    def ensure_view(self, *args, **kwargs):
        raise NotImplementedError
