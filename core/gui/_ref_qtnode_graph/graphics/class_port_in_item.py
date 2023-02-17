# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_port_in_item.py
# ------------------------------------------------------------------------------
#
# File          : class_port_in_item.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtCore, QtGui, QtWidgets

from ..core.define import EnumPortStyleProperty,EnumNodeStyleProperty
from .class_node_item_base import NodeItem


class PortInputNodeItem(NodeItem):
    """
    Input Port Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='group port', parent=None):
        super(PortInputNodeItem, self).__init__(name, parent)
        self._iconItem.setVisible(False)
        self._textItem.set_locked(True)
        self._xItem.text = 'Port Locked'

    def _set_base_size(self, add_w=0.0, add_h=0.0):
        _width, _height = self.calc_size(add_w, add_h)
        self._width = _width + 60
        self._height = _height if _height >= 60 else 60

    def _paint_horizontal(self, painter, option, widget):
        self.auto_switch_mode()

        painter.save()
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)

        _margin = 2.0
        _rect = self.boundingRect()
        _rect = QtCore.QRectF(_rect.left() + _margin,
                             _rect.top() + _margin,
                             _rect.width() - (_margin * 2),
                             _rect.height() - (_margin * 2))

        _text_rect = self._textItem.boundingRect()
        _text_rect = QtCore.QRectF(
            _rect.center().x() - (_text_rect.width() / 2) - 5,
            _rect.center().y() - (_text_rect.height() / 2),
            _text_rect.width() + 10,
            _text_rect.height()
        )

        painter.setBrush(QtGui.QColor(255, 255, 255, 20))
        painter.drawRoundedRect(_rect, 20, 20)

        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.drawRoundedRect(_text_rect, 3, 3)

        _size = int(_rect.height() / 4)
        triangle = QtGui.QPolygonF()
        triangle.append(QtCore.QPointF(-_size, _size))
        triangle.append(QtCore.QPointF(0.0, 0.0))
        triangle.append(QtCore.QPointF(_size, _size))

        transform = QtGui.QTransform()
        transform.translate(_rect.width() - (_size / 6), _rect.center().y())
        transform.rotate(90)
        _poly = transform.map(triangle)
        if self.selected:
            _pen = QtGui.QPen(
                QtGui.QColor(*EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value), 1.3
            )
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
        else:
            _pen = QtGui.QPen(QtGui.QColor(*self.border_color), 1.2)
            painter.setBrush(QtGui.QColor(0, 0, 0, 50))
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
        painter.setPen(_pen)
        painter.drawPolygon(_poly)
        _edge_size = 30
        _edge_rect = QtCore.QRectF(_rect.width() - (_size * 1.7),
                                  _rect.center().y() - (_edge_size / 2),
                                  4, _edge_size)
        painter.drawRect(_edge_rect)
        painter.restore()

    def _paint_vertical(self, painter, option, widget):
        self.auto_switch_mode()

        painter.save()
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)

        _margin = 2.0
        _rect = self.boundingRect()
        _rect = QtCore.QRectF(_rect.left() + _margin,
                             _rect.top() + _margin,
                             _rect.width() - (_margin * 2),
                             _rect.height() - (_margin * 2))

        _text_rect = self._textItem.boundingRect()
        _text_rect = QtCore.QRectF(
            _rect.center().x() - (_text_rect.width() / 2) - 5,
            _rect.top() + _margin,
            _text_rect.width() + 10,
            _text_rect.height()
        )

        painter.setBrush(QtGui.QColor(255, 255, 255, 20))
        painter.drawRoundedRect(_rect, 20, 20)

        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.drawRoundedRect(_text_rect, 3, 3)

        _size = int(_rect.height() / 4)
        triangle = QtGui.QPolygonF()
        triangle.append(QtCore.QPointF(-_size, _size))
        triangle.append(QtCore.QPointF(0.0, 0.0))
        triangle.append(QtCore.QPointF(_size, _size))

        transform = QtGui.QTransform()
        transform.translate(_rect.center().x(), _rect.bottom() - (_size / 3))
        transform.rotate(180)
        _poly = transform.map(triangle)

        if self.selected:
            _pen = QtGui.QPen(
                QtGui.QColor(*EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value), 1.3
            )
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
        else:
            _pen = QtGui.QPen(QtGui.QColor(*self.border_color), 1.2)
            painter.setBrush(QtGui.QColor(0, 0, 0, 50))
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
        painter.setPen(_pen)
        painter.drawPolygon(_poly)
        _edge_size = 30
        _edge_rect = QtCore.QRectF(_rect.center().x() - (_edge_size / 2),
                                  _rect.bottom() - (_size * 1.9),
                                  _edge_size, 4)
        painter.drawRect(_edge_rect)
        painter.restore()

    def set_proxy_mode(self, mode):
        """
        Set whether to draw the node with proxy mode.
        (proxy mode toggles visibility for some qgraphic items in the node.)

        Args:
            mode (bool): true to enable proxy mode.
        """
        if mode is self._proxyMode:
            return
        self._proxyMode = mode

        _visible = not mode

        # disable overlay item.
        self._xItem.proxy_mode = self._proxyMode

        # node widget visibility.
        for w in self._widgets.values():
            w.widget().setVisible(_visible)

        # input port text visibility.
        for port, text in self._inputItems.items():
            if port.display_name:
                text.setVisible(_visible)

        # output port text visibility.
        for port, text in self._outputItems.items():
            if port.display_name:
                text.setVisible(_visible)

        self._textItem.setVisible(_visible)

    def _align_label_horizontal(self, h_offset, v_offset):
        _rect = self.boundingRect()
        _text_rect = self._textItem.boundingRect()
        _x = _rect.center().x() - (_text_rect.width() / 2)
        _y = _rect.center().y() - (_text_rect.height() / 2)
        self._textItem.setPos(_x + h_offset, _y + v_offset)

    def _align_label_vertical(self, h_offset, v_offset):
        _rect = self.boundingRect()
        _text_rect = self._textItem.boundingRect()
        _x = _rect.center().x() - (_text_rect.width() / 1.5) - 2.0
        _y = _rect.center().y() - _text_rect.height() - 2.0
        self._textItem.setPos(_x + h_offset, _y + v_offset)

    def _align_ports_horizontal(self, v_offset):
        """
        Align input, output ports in the node layout.
        """
        v_offset = self.boundingRect().height() / 2
        if self.inputs or self.outputs:
            for ports in [self.inputs, self.outputs]:
                if ports:
                    v_offset -= ports[0].boundingRect().height() / 2
                    break
        super(PortInputNodeItem, self)._align_ports_horizontal(v_offset)

    def _align_ports_vertical(self, v_offset):
        super(PortInputNodeItem, self)._align_ports_vertical(v_offset)

    def _draw_node_horizontal(self):
        """
        Re-draw the node item in the scene.
        (re-implemented for vertical layout design)
        """
        # setup initial base size.
        self._set_base_size()
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label()
        # arrange icon
        self.align_icon()
        # arrange input and output ports.
        self.align_ports()
        # arrange node widgets
        self.align_widgets()

        self.update()
