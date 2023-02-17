# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : node_item_region.py
# ------------------------------------------------------------------------------
#
# File          : node_item_region.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui.node_graph.views.class_backdrop_node_item import BackdropNodeViewItem
from .define import DEFAULT_STATE_STYLE


class STCRegionViewItem(BackdropNodeViewItem):
    def __init__(self, node, parent, **kwargs):
        BackdropNodeViewItem.__init__(self, node, parent, **DEFAULT_STATE_STYLE, **kwargs)
