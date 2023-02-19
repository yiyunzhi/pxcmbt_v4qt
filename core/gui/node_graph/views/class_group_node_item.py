# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_group_node_item.py
# ------------------------------------------------------------------------------
#
# File          : class_group_node_item.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtCore, QtGui, QtWidgets
from .class_basic_node_view_item import BasicNodeViewItem


class GroupNodeViewItem(BasicNodeViewItem):
    """
    Group Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, node, parent=None, **kwargs):
        super(GroupNodeViewItem, self).__init__(node, parent, **kwargs)

    def _paint_horizontal(self, painter, option, widget):
        painter.save()
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)

        # base background.
        _margin = 6.0
        _rect = self.boundingRect()
        _rect = QtCore.QRectF(_rect.left() + _margin,
                              _rect.top() + _margin,
                              _rect.width() - (_margin * 2),
                              _rect.height() - (_margin * 2))

        # draw the base color
        _offset = 3.0
        _rect_1 = QtCore.QRectF(_rect.x() + (_offset / 2),
                                _rect.y() + _offset + 2.0,
                                _rect.width(), _rect.height())
        _rect_2 = QtCore.QRectF(_rect.x() - _offset,
                                _rect.y() - _offset,
                                _rect.width(), _rect.height())
        _poly = QtGui.QPolygonF()
        _poly.append(_rect_1.topRight())
        _poly.append(_rect_2.topRight())
        _poly.append(_rect_2.bottomLeft())
        _poly.append(_rect_1.bottomLeft())

        painter.setBrush(QtGui.QColor(*self.color).darker(180))
        painter.drawRect(_rect_1)
        painter.drawPolygon(_poly)

        painter.setBrush(QtGui.QColor(*self.color))
        painter.drawRect(_rect_2)

        if self.selected:
            _border_color = QtGui.QColor(
                *EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value
            )
            # light overlay on background when selected.
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
            painter.drawRect(_rect_2)
        else:
            _border_color = QtGui.QColor(*self.border_color)

        # node name background
        _padding = 2.0, 2.0
        _text_rect = self._textItem.boundingRect()
        _text_rect = QtCore.QRectF(_rect_2.left() + _padding[0],
                                   _rect_2.top() + _padding[1],
                                   _rect.right() - (_padding[0] * 2) - _margin,
                                   _text_rect.height() - (_padding[1] * 2))
        if self.selected:
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 80))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRect(_text_rect)

        # draw the outlines.
        _pen = QtGui.QPen(_border_color.darker(120), 0.8)
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(_pen)
        painter.drawLines([_rect_1.topRight(), _rect_2.topRight(),
                           _rect_1.topRight(), _rect_1.bottomRight(),
                           _rect_1.bottomRight(), _rect_1.bottomLeft(),
                           _rect_1.bottomLeft(), _rect_2.bottomLeft()])
        painter.drawLine(_rect_1.bottomRight(), _rect_2.bottomRight())

        _pen = QtGui.QPen(_border_color, 0.8)
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(_pen)
        painter.drawRect(_rect_2)

        painter.restore()

    def _paint_vertical(self, painter, option, widget):
        painter.save()
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)

        # base background.
        _margin = 6.0
        _rect = self.boundingRect()
        _rect = QtCore.QRectF(_rect.left() + _margin,
                              _rect.top() + _margin,
                              _rect.width() - (_margin * 2),
                              _rect.height() - (_margin * 2))

        # draw the base color
        _offset = 3.0
        _rect_1 = QtCore.QRectF(_rect.x() + _offset,
                                _rect.y() + (_offset / 2),
                                _rect.width(), _rect.height())
        _rect_2 = QtCore.QRectF(_rect.x() - _offset,
                                _rect.y() - _offset,
                                _rect.width(), _rect.height())
        _poly = QtGui.QPolygonF()
        _poly.append(_rect_1.topRight())
        _poly.append(_rect_2.topRight())
        _poly.append(_rect_2.bottomLeft())
        _poly.append(_rect_1.bottomLeft())

        painter.setBrush(QtGui.QColor(*self.color).dark(180))
        painter.drawRect(_rect_1)
        painter.drawPolygon(_poly)
        painter.setBrush(QtGui.QColor(*self.color))
        painter.drawRect(_rect_2)

        if self.selected:
            _border_color = QtGui.QColor(
                *EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value
            )
            # light overlay on background when selected.
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
            painter.drawRect(_rect_2)
        else:
            _border_color = QtGui.QColor(*self.border_color)

        # top & bottom edge background.
        _padding = 2.0
        _height = 10
        if self.selected:
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 80))

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        for y in [_rect_2.top() + _padding, _rect_2.bottom() - _height - _padding]:
            _top_rect = QtCore.QRectF(_rect.x() + _padding - _offset, y,
                                      _rect.width() - (_padding * 2), _height)
            painter.drawRect(_top_rect)

        # draw the outlines.
        _pen = QtGui.QPen(_border_color.darker(120), 0.8)
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(_pen)
        painter.drawLines([_rect_1.topRight(), _rect_2.topRight(),
                           _rect_1.topRight(), _rect_1.bottomRight(),
                           _rect_1.bottomRight(), _rect_1.bottomLeft(),
                           _rect_1.bottomLeft(), _rect_2.bottomLeft()])
        painter.drawLine(_rect_1.bottomRight(), _rect_2.bottomRight())

        _pen = QtGui.QPen(_border_color, 0.8)
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(_pen)
        painter.drawRect(_rect_2)

        painter.restore()

    def _align_icon_horizontal(self, h_offset, v_offset):
        super(GroupNodeItem, self)._align_icon_horizontal(h_offset, v_offset)

    def _align_icon_vertical(self, h_offset, v_offset):
        _y = self._height / 2
        _y -= self._iconItem.boundingRect().height()
        self._iconItem.setPos(self._width + h_offset, _y + v_offset)

    def _align_label_horizontal(self, h_offset, v_offset):
        super(GroupNodeItem, self)._align_label_horizontal(h_offset, v_offset)

    def _align_label_vertical(self, h_offset, v_offset):
        _y = self._height / 2
        _y -= self.text_item.boundingRect().height() / 2
        self._textItem.setPos(self._width + h_offset, _y + v_offset)

    def _align_ports_horizontal(self, v_offset):
        _width = self._width
        _txt_offset = EnumPortStyleProperty.CLICK_FALLOFF.value - 2
        _spacing = 1

        # adjust input position
        _inputs = [p for p in self.inputs if p.isVisible()]
        if _inputs:
            _port_width = _inputs[0].boundingRect().width()
            _port_height = _inputs[0].boundingRect().height()
            _port_x = _port_width / 2 * -1
            _port_x += 3.0
            _port_y = v_offset
            for port in _inputs:
                port.setPos(_port_x, _port_y)
                _port_y += _port_height + _spacing
        # adjust input text position
        for port, text in self._inputItems.items():
            if port.isVisible():
                _txt_x = port.boundingRect().width() / 2 - _txt_offset
                _txt_x += 3.0
                text.setPos(_txt_x, port.y() - 1.5)

        # adjust output position
        _outputs = [p for p in self.outputs if p.isVisible()]
        if _outputs:
            _port_width = _outputs[0].boundingRect().width()
            _port_height = _outputs[0].boundingRect().height()
            _port_x = _width - (_port_width / 2)
            _port_x -= 9.0
            _port_y = v_offset
            for port in _outputs:
                port.setPos(_port_x, _port_y)
                _port_y += _port_height + _spacing
        # adjust output text position
        for port, text in self._outputItems.items():
            if port.isVisible():
                _txt_width = text.boundingRect().width() - _txt_offset
                _txt_x = port.x() - _txt_width
                text.setPos(_txt_x, port.y() - 1.5)

    def _align_ports_vertical(self, v_offset):
        # adjust input position
        _inputs = [p for p in self.inputs if p.isVisible()]
        if _inputs:
            _port_width = _inputs[0].boundingRect().width()
            _port_height = _inputs[0].boundingRect().height()
            _half_width = _port_width / 2
            _delta = self._width / (len(_inputs) + 1)
            _port_x = _delta
            _port_y = -_port_height / 2 + 3.0
            for port in _inputs:
                port.setPos(_port_x - _half_width, _port_y)
                _port_x += _delta

        # adjust output position
        _outputs = [p for p in self.outputs if p.isVisible()]
        if _outputs:
            _port_width = _outputs[0].boundingRect().width()
            _port_height = _outputs[0].boundingRect().height()
            _half_width = _port_width / 2
            _delta = self._width / (len(_outputs) + 1)
            _port_x = _delta
            _port_y = self._height - (_port_height / 2) - 9.0
            for port in _outputs:
                port.setPos(_port_x - _half_width, _port_y)
                _port_x += _delta

    def _draw_node_horizontal(self):
        _height = self._textItem.boundingRect().height()

        # update port text items in visibility.
        for port, text in self._inputItems.items():
            text.setVisible(port.display_name)
        for port, text in self._outputItems.items():
            text.setVisible(port.display_name)

        # setup initial base size.
        self._set_base_size(add_w=8.0, add_h=_height + 10)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label()
        # arrange icon
        self.align_icon(h_offset=2.0, v_offset=3.0)
        # arrange input and output ports.
        self.align_ports(v_offset=_height)
        # arrange node widgets
        self.align_widgets(v_offset=_height)

        self.update()

    def _draw_node_vertical(self):
        _height = self._textItem.boundingRect().height()

        # hide the port text items in vertical layout.
        for port, text in self._inputItems.items():
            text.setVisible(False)
        for port, text in self._outputItems.items():
            text.setVisible(False)

        # setup initial base size.
        self._set_base_size(add_w=8.0)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label(h_offset=7, v_offset=6)
        # align icon
        self.align_icon(h_offset=4, v_offset=-2)
        # arrange input and output ports.
        self.align_ports(v_offset=_height + (_height / 2))
        # arrange node widgets
        self.align_widgets(v_offset=_height / 2)

        self.update()
