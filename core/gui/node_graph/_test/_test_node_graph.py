# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_node_graph.py
# ------------------------------------------------------------------------------
#
# File          : _test_node_graph.py
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
from gui import QtGui,QtCore,QtWidgets
from gui.node_graph.class_node_graph import NodeGraph

app=QtWidgets.QApplication(sys.argv)
g=NodeGraph()
v=g.p_view
v.show()
sys.exit(app.exec())