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
from core.gui import ClassFactory
from .node_state import STCStateNode, STCCompositeStateNode, STCBackdropNode, STCInitialStateNode
from .node_base import BaseSTCNode
from .node_item_simple_state import STCStateItemState
from .node_item_composite_state import STCCompositeStateViewItemState
from .node_item_backdrop_item import STCBackdropViewItem
from .node_item_initial_item import STCInitialNodeViewItem
from .widget_stc_node_graph_view import STCGraphView
from .define import (NODE_GRAPH_STATE_NS, NODE_GRAPH_PSEUDO_NS, NODE_GRAPH_NS, NODE_GRAPH_TOOL_NS, CLASS_FACTORY_NS_KEY)
from .class_factory import STC_NODE_VIEW_FACTORY, STC_GRAPH_VIEW_FACTORY, STC_NODE_FACTORY

STC_GRAPH_VIEW_FACTORY.register(STCGraphView, STCGraphView.__name__, NODE_GRAPH_NS, True)
STC_NODE_VIEW_FACTORY.register(STCStateItemState, STCStateItemState.__name__, NODE_GRAPH_STATE_NS, True)
STC_NODE_VIEW_FACTORY.register(STCCompositeStateViewItemState, STCCompositeStateViewItemState.__name__, NODE_GRAPH_STATE_NS, True)
STC_NODE_VIEW_FACTORY.register(STCBackdropViewItem, STCBackdropViewItem.__name__, NODE_GRAPH_TOOL_NS, True)
STC_NODE_VIEW_FACTORY.register(STCInitialNodeViewItem, STCInitialNodeViewItem.__name__, NODE_GRAPH_STATE_NS, True)

STC_NODE_FACTORY.register(STCStateNode, 'state', NODE_GRAPH_STATE_NS, True)
STC_NODE_FACTORY.register(STCBackdropNode, 'backdrop', NODE_GRAPH_TOOL_NS, True)
STC_NODE_FACTORY.register(STCCompositeStateNode, 'compositeState', NODE_GRAPH_STATE_NS, True)
STC_NODE_FACTORY.register(STCInitialStateNode, 'initialState', NODE_GRAPH_STATE_NS, True)
