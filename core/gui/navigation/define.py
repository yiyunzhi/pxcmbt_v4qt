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

class EnumAppModeMenuIDs:
    WELCOME = 1000
    MODEL = 1010
    BLOCKS = 1020
    ENV = 1030
    TESTER = 1040
    HELP = 1050


class EnumMainMenuIDs:
    FILE = 100
    FILE_NEW_PROJECT = 101
    FILE_OPEN_PROJECT = 102
    FILE_SAVE_PROJECT = 103
    FILE_SAVE_PROJECT_AS = 104
    FILE_EXIT = 105

    EDIT = 200
    EDIT_UNDO = 201
    EDIT_REDO = 202
    EDIT_CUT = 203
    EDIT_COPY = 204
    EDIT_PASTE = 205
    EDIT_REMOVE = 206
    EDIT_DELETE = 207

    VIEW = 300
    VIEW_WINDOWS = 301

    TOOL = 400
    TOOL_EXTERNAL = 401
    TOOL_EXTERNAL_CALCULATOR = 402
    TOOL_EXTERNAL_TXT_EDITOR = 403
    TOOL_EXTERNAL_SCR_SHOOT = 404
    TOOL_OPTION = 410

    WINDOWS = 500
    WINDOWS_SAVE_PERSP = 501
    WINDOWS_LOAD_PERSP = 502

    HELP = 600
    HELP_HELP = 601
    HELP_ABOUT = 610