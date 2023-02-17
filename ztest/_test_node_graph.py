# -*- coding: utf-8 -*-
import os.path
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
from gui import QtWidgets
from core.gui._ref_qtnode_graph.class_node_graph import NodeGraph
from gui._ref_qtnode_graph.nodes.class_base_node import BaseNode
from gui._ref_qtnode_graph.nodes.class_group_node import GroupNode
from gui._ref_qtnode_graph.widgets.class_minimap_view import MiniMapGraphicsView
from ztest._test_main_frame import TestFrame, app


# from ztest._test_main_frame_no_css import TestFrame,app


class MyNode(BaseNode):
    __identifier__ = 'com.chantasticvfx'
    NODE_NAME = 'My Node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.add_input('foo', color=(180, 80, 0))
        self.add_input('foo2', color=(180, 80, 0))
        self.add_output('bar')


class MyNode2(BaseNode):
    __identifier__ = 'com.chantasticvfx'
    NODE_NAME = 'My Node2'

    def __init__(self):
        super(MyNode2, self).__init__()


class MyGroupNode(GroupNode):
    """
    example test group node with a in port and out port.
    """

    # set a unique node identifier.
    __identifier__ = 'nodes.group'

    # set the initial default node name.
    NODE_NAME = 'group node'

    def __init__(self):
        super(MyGroupNode, self).__init__()
        self.set_color(50, 8, 25)

        # create input and output port.
        self.add_input('in')
        self.add_output('out')


_minimap_frame = QtWidgets.QFrame()

_main_win = TestFrame()
g = NodeGraph()
g.set_context_menu_from_file(os.path.join(os.path.dirname(__file__), '_test_node_graph', 'node_graph_context_menu_de.json'))
g.register_node(MyNode)
g.register_node(MyNode2)
g.register_node(MyGroupNode)
node_a = g.create_node('com.chantasticvfx.MyNode', name='Node A')
_mini_map = MiniMapGraphicsView(_minimap_frame, g.get_view())
g.fit_to_selection()
w = g.widget
_main_win.setCentralWidget(w)
_main_win.show()
_minimap_frame.show()

sys.exit(app.exec())
