# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : node_item_backdrop_item.py
# ------------------------------------------------------------------------------
#
# File          : node_item_backdrop_item.py
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


class STCBackdropViewItem(BackdropNodeViewItem):

    def __init__(self, node, parent=None, **kwargs):
        BackdropNodeViewItem.__init__(self, node, parent, **DEFAULT_STATE_STYLE, **kwargs, titlebar_visible=False)

    def draw(self, *args, **kwargs):
        pass
