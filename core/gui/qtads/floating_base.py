# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : floating_base.py
# ------------------------------------------------------------------------------
#
# File          : floating_base.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtCore, QtWidgets
from .define import EnumDragState


class IFloatingWidget:
    def startFloating(self, drag_start_mouse_pos: QtCore.QPoint,
                      size: QtCore.QSize,
                      drag_state: EnumDragState, widget: QtWidgets.QWidget):
        raise NotImplementedError

    def moveFloating(self):
        raise NotImplementedError

    def finishDragging(self):
        raise NotImplementedError
