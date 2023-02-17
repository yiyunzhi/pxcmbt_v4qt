# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : node_item_composite_state.py
# ------------------------------------------------------------------------------
#
# File          : node_item_composite_state.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .node_item_base import BaseSTCStateNodeViewItem
from .node_item_region import STCRegionViewItem


class STCCompositeStateViewItemState(BaseSTCStateNodeViewItem):

    def __init__(self, node, parent=None):
        BaseSTCStateNodeViewItem.__init__(self, node, parent)
        self.regionItem = STCRegionViewItem(self.node, self, backdrop_text='Region',titlebar_visible=False)
