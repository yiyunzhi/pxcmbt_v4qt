# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_stc_editor.py
# ------------------------------------------------------------------------------
#
# File          : pane_stc_editor.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os
from gui import QtGui, QtCore, QtWidgets
from .node_graph.graph_stc import STCNodeGraph
from .node_graph.widget_stc_node_graph_view import STCGraphView
from .node_graph import STC_NODE_FACTORY, STC_GRAPH_VIEW_FACTORY, CLASS_FACTORY_NS_KEY


class STCEditor(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.graph = STCNodeGraph(node_factory=STC_NODE_FACTORY,
                                  view_factory=STC_GRAPH_VIEW_FACTORY,
                                  view_type='{}.{}'.format(getattr(STCGraphView, CLASS_FACTORY_NS_KEY), STCGraphView.__name__))
        self.graph.set_context_menu_from_file(os.path.join(os.path.dirname(__file__), 'node_graph_context_menu_de.json'))
        # layout
        self.mainLayout.addWidget(self.graph.get_view())
        self.setLayout(self.mainLayout)
