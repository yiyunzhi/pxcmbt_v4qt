# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : helper.py
# ------------------------------------------------------------------------------
#
# File          : helper.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtGui, QtWidgets, QtCore
from core.gui.core.define import EnumRepolishChildOptions


def get_qApp() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance()


def hlp_get_harmony_color(r: int, g: int, b: int):
    _luma = ((0.299 * r) + (0.587 * g) + (0.114 * b)) / 255
    if _luma > 0.5:
        return 0, 0, 0
    else:
        return 255, 255, 255


def hlp_optimal_gui_color(color: [QtGui.QPalette, QtGui.QColor], cg=None, cr=None):
    if isinstance(color, QtGui.QColor):
        _color = color
    elif isinstance(color, QtGui.QPalette):
        if cg is None and cr is not None:
            _color = color.color(cr)
        elif cg is not None and cr is not None:
            _color = color.color(cg, cr)
        else:
            _color = color.color(QtGui.QPalette.ColorRole.Window)
    else:
        raise ValueError('not support color object')
    return QtGui.QColor(*hlp_get_harmony_color(_color.red(), _color.green(), _color.blue()))


def hlp_repolish_style(widget: QtWidgets.QWidget, option: EnumRepolishChildOptions = EnumRepolishChildOptions.RepolishIgnoreChildren):
    if widget is None:
        return
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    if option == EnumRepolishChildOptions.RepolishIgnoreChildren:
        return
    _options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly if option == EnumRepolishChildOptions.RepolishDirectChildren else QtCore.Qt.FindChildOption.FindChildrenRecursively
    _children = widget.findChildren(QtWidgets.QWidget, options=_options)
    for x in _children:
        x.style().unpolish(x)
        x.style().polish(x)
