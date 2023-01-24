# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : define.py
# ------------------------------------------------------------------------------
#
# File          : define.py
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
import enum

evtAppThemeChanged = QtCore.QEvent.registerEventType()


class EnumRepolishChildOptions(enum.Enum):
    RepolishIgnoreChildren = enum.auto()
    RepolishDirectChildren = enum.auto()
    RepolishChildrenRecursively = enum.auto()