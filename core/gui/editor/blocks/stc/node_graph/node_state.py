# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : node_state.py
# ------------------------------------------------------------------------------
#
# File          : node_state.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.node_graph.class_backdrop_node import BackdropNode

from .class_factory import STC_NODE_VIEW_FACTORY
from .node_base import BaseSTCNode
from .node_item_simple_state import STCStateItemState
from .node_item_composite_state import STCCompositeStateViewItemState
from .node_item_backdrop_item import STCBackdropViewItem
from .node_item_initial_item import STCInitialNodeViewItem


class STCInitialStateNode(BaseSTCNode):
    serializeTag = '!STCInitialStateNode'

    def __init__(self, **kwargs):
        if 'view_type' not in kwargs:
            kwargs['view_type'] = '{}.{}'.format(self.nodeNamespace, STCInitialNodeViewItem.__name__)
        BaseSTCNode.__init__(self, **kwargs, label='initial', view_factory=STC_NODE_VIEW_FACTORY)


class STCStateNode(BaseSTCNode):
    serializeTag = '!STCStateNode'

    def __init__(self, **kwargs):
        if 'view_type' not in kwargs:
            kwargs['view_type'] = '{}.{}'.format(self.nodeNamespace, STCStateItemState.__name__)
        BaseSTCNode.__init__(self, **kwargs, view_factory=STC_NODE_VIEW_FACTORY)


class STCBackdropNode(BackdropNode):
    serializeTag = '!STCBackdropNode'

    def __init__(self, **kwargs):
        if 'view_type' not in kwargs:
            kwargs['view_type'] = '{}.{}'.format(self.nodeNamespace, STCBackdropViewItem.__name__)
        BackdropNode.__init__(self, **kwargs, view_factory=STC_NODE_VIEW_FACTORY)


class STCCompositeStateNode(BaseSTCNode):
    serializeTag = '!STCCompositeStateNode'

    def __init__(self, **kwargs):
        if 'view_type' not in kwargs:
            kwargs['view_type'] = '{}.{}'.format(self.nodeNamespace, STCCompositeStateViewItemState.__name__)
        BaseSTCNode.__init__(self, **kwargs, view_factory=STC_NODE_VIEW_FACTORY)
