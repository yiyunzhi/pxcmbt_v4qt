# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : node_item_initial_item.py
# ------------------------------------------------------------------------------
#
# File          : node_item_initial_item.py
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
from gui.node_graph.views.class_base_node_view_item import BaseNodeViewItem
from .define import (DEFAULT_INITIAL_STATE_STYLE)


class STCInitialNodeViewItem(BaseNodeViewItem):
    def __init__(self, node, parent: Optional[QtWidgets.QGraphicsItem] = None, **kwargs):
        super().__init__(node, parent, **DEFAULT_INITIAL_STATE_STYLE, **kwargs)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width + 2, self.height + 2)

    def draw(self, *args, **kwargs):
        pass

    def paint(self, painter, option, widget=None):
        """
        Draws the node base not the ports.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()
        # base background.
        _bg_color = QtGui.QColor(self.color)
        _border_color = QtGui.QColor(self.border_color)
        _selected_border_color = QtGui.QColor(self._selectedBorderColor)
        _rect = self.boundingRect()
        painter.setBrush(_bg_color)
        painter.setPen(QtGui.QPen(_border_color, 0.8))
        if self.isSelected():
            painter.setBrush(_bg_color.lighter(110)),
            painter.setPen(QtGui.QPen(_selected_border_color, 1.2))
        painter.drawEllipse(_rect.center(), self.width / 2, self.height / 2)

        painter.restore()
