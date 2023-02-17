# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_stc_node_graph_view.py
# ------------------------------------------------------------------------------
#
# File          : widget_stc_node_graph_view.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from typing import Union, Any
from gui import QtGui, QtCore, QtWidgets
from gui.node_graph.views.class_node_graph_view import NodeGraphView
from .widget_stc_node_graph_scene import STCNodeGraphScene


class STCGraphView(NodeGraphView):
    def __init__(self,graph, parent=None, undo_stack=None):
        NodeGraphView.__init__(self,graph, parent, undo_stack)
        self.setScene(STCNodeGraphScene(self))
        self._currentMousePos = QtCore.QPointF(0, 0)

    def _draw_static_text(self, painter: QtGui.QPainter, rect: Union[QtCore.QRectF, QtCore.QRect]):
        _t = painter.transform()
        painter.save()
        painter.setTransform(QtGui.QTransform(1, _t.m12(), _t.m13(), _t.m21(), 1, _t.m23(), 1,
                                              1, _t.m33()))

        painter.drawText(10, 20, 'XY: [{} , {}] '.format(self._currentMousePos.x(), self._currentMousePos.y()))
        painter.drawText(10, 35, 'Scale: {}'.format(self.get_zoom()))
        painter.restore()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self._currentMousePos = event.pos()

    def drawForeground(self, painter: QtGui.QPainter, rect: Union[QtCore.QRectF, QtCore.QRect]) -> None:
        super().drawForeground(painter, rect)
        self._draw_static_text(painter, rect)
