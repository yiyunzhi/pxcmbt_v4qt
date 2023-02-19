# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : __init__.py.py
# ------------------------------------------------------------------------------
#
# File          : __init__.py.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from solutions.stc.gui.editor_stc import STCEditor

SOLUTION_DEF = {
    'icon': None,
    'namespace': 'StateChart',
    'type': 'stc',
    'version': '1.0.1',
    'editor': STCEditor,
    'builtinEntitiesPath': '',
}
