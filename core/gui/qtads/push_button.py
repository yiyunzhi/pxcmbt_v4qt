# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : push_button.py
# ------------------------------------------------------------------------------
#
# File          : push_button.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import enum
from core.gui.qtimp import QtWidgets, QtCore, QtGui


class EnumButtonOrientation(enum.IntEnum):
    Horizontal = enum.auto()
    VerticalTopToBottom = enum.auto()
    VerticalBottomToTop = enum.auto()


class CPushButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orientation = EnumButtonOrientation.Horizontal

    def sizeHint(self) -> QtCore.QSize:
        _sh = super().sizeHint()
        if self._orientation != EnumButtonOrientation.Horizontal:
            _sh.transpose()
        return _sh

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        _painter = QtWidgets.QStylePainter(self)
        _opt = QtWidgets.QStyleOptionButton()
        self.initStyleOption(_opt)
        if self._orientation == EnumButtonOrientation.VerticalTopToBottom:
            _painter.rotate(90)
            _painter.translate(0, -1 * self.width())
            _opt.rect = _opt.rect.transposed()
        elif self._orientation == EnumButtonOrientation.VerticalBottomToTop:
            _painter.rotate(-90)
            _painter.translate(-1 * self.height(), 0)
            _opt.rect = _opt.rect.transposed()
        _painter.drawControl(QtWidgets.QStyle.ControlElement.CE_PushButton, _opt)

    def buttonOrientation(self):
        return self._orientation

    def setButtonOrientation(self, orientation: EnumButtonOrientation):
        self._orientation=orientation
        self.updateGeometry()
