# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : node_item_base.py
# ------------------------------------------------------------------------------
#
# File          : node_item_base.py
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
from gui import QtGui, QtCore, QtWidgets
from gui.node_graph.views.class_basic_node_view_item import BasicNodeViewItem
from .define import (DEFAULT_STATE_STYLE)


class BaseSTCStateNodeViewItem(BasicNodeViewItem):

    def __init__(self, node, parent: Optional[QtWidgets.QGraphicsItem] = None, **kwargs):
        super().__init__(node, parent, **DEFAULT_STATE_STYLE, **kwargs)
