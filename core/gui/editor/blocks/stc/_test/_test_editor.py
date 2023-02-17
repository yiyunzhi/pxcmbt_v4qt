# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_editor.py
# ------------------------------------------------------------------------------
#
# File          : _test_editor.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import sys
from gui import QtGui, QtCore, QtWidgets
from core.gui.editor.blocks import STCEditor
from ztest._test_main_frame import TestFrame, app

_main_frame = TestFrame()

_main_frame.setCentralWidget(STCEditor(_main_frame))
_main_frame.show()
sys.exit(app.exec())
