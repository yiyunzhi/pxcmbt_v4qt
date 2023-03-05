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
import enum


class EnumRepolishChildOptions(enum.Enum):
    RepolishIgnoreChildren = enum.auto()
    RepolishDirectChildren = enum.auto()
    RepolishChildrenRecursively = enum.auto()


class EnumLayoutModifierPolicy:
    REPLACE = 'replace'
    APPEND = 'append'


class EnumLayoutModifierTarget:
    CENTER_WIDGET = 'centerWidget'
    FLOAT_RIGHT = 'floatRight'
    PROJECT_TREE_VIEW = 'projectTreeView'


class EnumGuiViewName:
    APP_MODE_SEL_SIDEBAR = 'app.modeSelToolbar'
    APP_MODEL_PROJECT_TREEVIEW = 'app.modelProjectTreeView'
    APP_TESTER_PROJECT_TREEVIEW = 'app.testerProjectTreeView'
    APP_MENU_BAR = 'app.menubar'
    APP_WELCOME = 'app.welcome'
    APP_HELP = 'app.help'
