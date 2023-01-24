# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_flag.py
# ------------------------------------------------------------------------------
#
# File          : _test_flag.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui.qtads.util import testFlag
from gui.qtads.define import EnumDockMgrConfigFlag,DOCK_MANAGER_DEFAULT_CONFIG,EnumSideBarLocation


print(testFlag(DOCK_MANAGER_DEFAULT_CONFIG,EnumDockMgrConfigFlag.DockAreaHasCloseButton))
print(EnumDockMgrConfigFlag.DockAreaHasCloseButton in DOCK_MANAGER_DEFAULT_CONFIG)
print(EnumDockMgrConfigFlag.OpaqueUndocking in DOCK_MANAGER_DEFAULT_CONFIG)
print(str(EnumSideBarLocation.TOP.value))
print(EnumSideBarLocation(0))