# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : graphicsitem_state.py
# ------------------------------------------------------------------------------
#
# File          : graphicsitem_state.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from typing import Optional
from gui import QtWidgets
from .node_item_base import BaseSTCStateNodeViewItem


class STCStateItemState(BaseSTCStateNodeViewItem):
    def __init__(self, node, parent: Optional[QtWidgets.QGraphicsItem] = None):
        super().__init__(node, parent)
