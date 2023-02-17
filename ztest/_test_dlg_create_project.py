# -*- coding: utf-8 -*-
import sys

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_dlg_create_project.py
# ------------------------------------------------------------------------------
#
# File          : _test_dlg_create_project.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui.ui.dlg_create_project import CreateProjectDialog
from ztest._test_main_frame import app, TestFrame

frame = TestFrame()
frame.show()
dlg = CreateProjectDialog(None)
dlg.show()
sys.exit(app.exec())
