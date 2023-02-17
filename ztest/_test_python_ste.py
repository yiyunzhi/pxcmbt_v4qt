# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_python_ste.py
# ------------------------------------------------------------------------------
#
# File          : _test_python_ste.py
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
from gui import QtWidgets
from core.gui.components.widget_ste_python import PythonSTE

app = QtWidgets.QApplication(sys.argv)
_main_win=QtWidgets.QMainWindow()
w=PythonSTE(_main_win)
_main_win.setCentralWidget(w)
_main_win.show()

sys.exit(app.exec())