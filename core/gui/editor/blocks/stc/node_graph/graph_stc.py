# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : graph_stc.py
# ------------------------------------------------------------------------------
#
# File          : graph_stc.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtGui, QtCore, QtWidgets
from gui.node_graph.class_node_graph import NodeGraph


class STCNodeGraph(NodeGraph):
    serializeTag = '!STCNodeGraph'
    def __init__(self, parent: QtCore.QObject = None, **kwargs):
        NodeGraph.__init__(self, parent, **kwargs)
        self.setObjectName('STCNodeGraph')
        self._undoStack.setParent(self)
