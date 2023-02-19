# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_basic_node_view_item.py
# ------------------------------------------------------------------------------
#
# File          : class_basic_node_view_item.py
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
from collections import OrderedDict
from core.gui.qtimp import QtGui, QtCore, QtWidgets
from ..core.define import ICON_NODE_BASE,EnumLayoutDirection,ITEM_CACHE_MODE
from .class_base_node_view_item import BaseNodeViewItem
from .class_text_item import NodeTextItem
from .class_overlay_disable_item import XDisabledItem


class BasicNodeViewItem(BaseNodeViewItem):

    def __init__(self, node, parent: Optional[QtWidgets.QGraphicsItem] = None, **kwargs):
        super().__init__(node, parent, **kwargs)
        self.iconSize = kwargs.get('icon_size', 16)
        _pixmap = QtGui.QPixmap(ICON_NODE_BASE)
        if _pixmap.size().height() > self.iconSize:
            _pixmap = _pixmap.scaledToHeight(self.iconSize, QtCore.Qt.TransformationMode.SmoothTransformation)
        self._borderRadius = kwargs.get('border_radius', 12)
        self._iconItem = QtWidgets.QGraphicsPixmapItem(_pixmap, self)
        self._iconItem.setTransformationMode(QtCore.Qt.TransformationMode.SmoothTransformation)
        self._textItem = NodeTextItem(self.label, self)
        self._xItem = XDisabledItem(self, 'DISABLED')
        self._widgets = OrderedDict()
        self._proxyMode = False
        self._proxyModeThreshold = 60

    @BaseNodeViewItem.disabled.setter
    def disabled(self, state=False):
        BaseNodeViewItem.disabled.fset(self, state)
        for n, w in self._widgets.items():
            w.widget().setDisabled(state)
        self._tooltip_disable(state)
        self._xItem.setVisible(state)

    @BaseNodeViewItem.label.setter
    def label(self, label=''):
        BaseNodeViewItem.label.fset(self, label)
        self.draw()

    def draw(self):
        """
        Re-draw the node item in the scene with proper
        calculated size and widgets aligned.
        """
        if self.node.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._draw_node_horizontal()
        elif self.node.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._draw_node_vertical()
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def _draw_node_horizontal(self):
        _height = self._textItem.boundingRect().height()

        # setup initial base size.
        self._set_base_size(add_h=_height)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip

        # self._tooltip_disable(self.node.disabled)
        self._tooltip_disable(self._disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label()
        # align icon
        self.align_icon(h_offset=3.0, v_offset=1.0)
        # arrange node widgets
        self.align_widgets(v_offset=_height)

        self.update()

    def _draw_node_vertical(self):
        # setup initial base size.
        self._set_base_size()
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.node.disabled)

        # --- setup node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label(h_offset=2)
        # align icon
        self.align_icon(h_offset=6, v_offset=4)
        # arrange node widgets
        self.align_widgets()
        self.update()

    def _paint_horizontal(self, painter, option, widget):
        painter.save()
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        # base background.
        _margin = 1.0
        _bg_color = QtGui.QColor(self.color)
        _border_color = QtGui.QColor(self.border_color)
        _selected_border_color = QtGui.QColor(self._selectedBorderColor)
        _rect = self.boundingRect()
        _rect = QtCore.QRectF(_rect.left() + _margin,
                              _rect.top() + _margin,
                              _rect.width() - (_margin * 2),
                              _rect.height() - (_margin * 2))

        _radius = self._borderRadius
        painter.setBrush(_bg_color)
        painter.drawRoundedRect(_rect, _radius, _radius)

        # light overlay on background when selected.
        if self.isSelected():
            painter.setBrush(_bg_color.lighter(110))
            painter.drawRoundedRect(_rect, _radius, _radius)

        # node name background.
        painter.setPen(QtGui.QPen(_border_color, 0.8))
        _text_rect = self._textItem.boundingRect()
        painter.drawLine(_rect.left() + _margin, _text_rect.bottom(), _rect.right() - _margin, _text_rect.bottom())
        # _padding = 3.0, 2.0
        # _text_rect = self._textItem.boundingRect()
        # _text_rect = QtCore.QRectF(_text_rect.x() + _padding[0],
        #                            _rect.y() + _padding[1],
        #                            _rect.width() - _padding[0] - _margin,
        #                            _text_rect.height() - (_padding[1] * 2))
        # if self.isSelected():
        #     painter.setBrush(QtGui.QColor(self.color))
        # else:
        #     painter.setBrush(QtGui.QColor(0, 0, 0, 80))
        # painter.drawRoundedRect(_text_rect, 3.0, 3.0)

        # node border
        if self.isSelected():
            _border_width = 1.2
            _border_color = _selected_border_color
        else:
            _border_width = 0.8
            _border_color = _border_color

        _border_rect = QtCore.QRectF(_rect.left(), _rect.top(), _rect.width(), _rect.height())

        _pen = QtGui.QPen(_border_color, _border_width)
        _pen.setCosmetic(self.get_view().get_zoom() < 0.0)
        _path = QtGui.QPainterPath()
        _path.addRoundedRect(_border_rect, _radius, _radius)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(_pen)
        painter.drawPath(_path)

        painter.restore()

    def _paint_vertical(self, painter, option, widget):
        painter.save()
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        # base background.
        _margin = 1.0
        _rect = self.boundingRect()
        _rect = QtCore.QRectF(_rect.left() + _margin,
                              _rect.top() + _margin,
                              _rect.width() - (_margin * 2),
                              _rect.height() - (_margin * 2))

        _radius = 4.0
        painter.setBrush(QtGui.QColor(*self.color))
        painter.drawRoundedRect(_rect, _radius, _radius)

        # light overlay on background when selected.
        if self.isSelected():
            painter.setBrush(
                QtGui.QColor(self.selected_border_color)
            )
            painter.drawRoundedRect(_rect, _radius, _radius)

        # top & bottom edge background.
        _padding = 2.0
        _height = 10
        if self.isSelected():
            painter.setBrush(QtGui.QColor(self.selected_border_color))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 80))
        for y in [_rect.y() + _padding, _rect.height() - _height - 1]:
            _edge_rect = QtCore.QRectF(_rect.x() + _padding, y,
                                       _rect.width() - (_padding * 2), _height)
            painter.drawRoundedRect(_edge_rect, 3.0, 3.0)

        # node border
        _border_width = 0.8
        _border_color = QtGui.QColor(*self.border_color)
        if self.isSelected():
            _border_width = 1.2
            _border_color = QtGui.QColor(self.selected_border_color)
        _border_rect = QtCore.QRectF(_rect.left(), _rect.top(),
                                     _rect.width(), _rect.height())

        _pen = QtGui.QPen(_border_color, _border_width)
        _pen.setCosmetic(self.get_view().get_zoom() < 0.0)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(_pen)
        painter.drawRoundedRect(_border_rect, _radius, _radius)

        painter.restore()

    def paint(self, painter, option, widget=None):
        """
        Draws the node base not the ports.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self.auto_switch_mode()
        if self.node.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._paint_horizontal(painter, option, widget)
        elif self.node.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._paint_vertical(painter, option, widget)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def _tooltip_disable(self, state):
        """
        Updates the node tooltip when the node is enabled/disabled.

        Args:
            state (bool): node disable state.
        """
        if self._textItem.toPlainText() != self.label:
            self._textItem.setPlainText(self.label)
        _tooltip = '<b>{}</b>'.format(self.label)
        if state:
            _tooltip += ' <font color="red"><b>(DISABLED)</b></font>'
        _tooltip += '<br/>{}<br/>'.format(self.node.type_)
        self.setToolTip(_tooltip)

    def _set_base_size(self, add_w=0.0, add_h=0.0):
        """
        Sets the initial base size for the node.

        Args:
            add_w (float): add additional width.
            add_h (float): add additional height.
        """
        _w, _h = self.calc_size(add_w, add_h)
        if _w < self._minWidth:
            self._width = self._minWidth
        else:
            self._width = _w
        if _h < self._minHeight:
            self._height = self._minHeight
        else:
            self._height = _h

    def _align_label_horizontal(self, h_offset, v_offset):
        _rect = self.boundingRect()
        _text_rect = self._textItem.boundingRect()
        _x = _rect.center().x() - (_text_rect.width() / 2)
        self._textItem.setPos(_x + h_offset, _rect.y() + v_offset)

    def _align_label_vertical(self, h_offset, v_offset):
        _rect = self._textItem.boundingRect()
        _x = self.boundingRect().right() + h_offset
        _y = self.boundingRect().center().y() - (_rect.height() / 2) + v_offset
        self._textItem.setPos(_x, _y)

    def align_label(self, h_offset=0.0, v_offset=0.0):
        """
        Center node label text to the top of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        if self.node.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._align_label_horizontal(h_offset, v_offset)
        elif self.node.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._align_label_vertical(h_offset, v_offset)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def _align_icon_horizontal(self, h_offset, v_offset):
        _icon_rect = self._iconItem.boundingRect()
        _text_rect = self._textItem.boundingRect()
        _x = self.boundingRect().left() + 2.0
        _y = _text_rect.center().y() - (_icon_rect.height() / 2)
        self._iconItem.setPos(_x + h_offset, _y + v_offset)

    def _align_icon_vertical(self, h_offset, v_offset):
        _center_y = self.boundingRect().center().y()
        _icon_rect = self._iconItem.boundingRect()
        _text_rect = self._textItem.boundingRect()
        _x = self.boundingRect().right() + h_offset
        _y = _center_y - _text_rect.height() - (_icon_rect.height() / 2) + v_offset
        self._iconItem.setPos(_x, _y)

    def align_icon(self, h_offset=0.0, v_offset=0.0):
        """
        Align node icon to the default top left of the node.

        Args:
            v_offset (float): additional vertical offset.
            h_offset (float): additional horizontal offset.
        """
        if self.node.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._align_icon_horizontal(h_offset, v_offset)
        elif self.node.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._align_icon_vertical(h_offset, v_offset)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def _align_widgets_horizontal(self, v_offset):
        if not self._widgets:
            return
        _rect = self.boundingRect()
        _y = _rect.y() + v_offset
        for widget in self._widgets.values():
            _widget_rect = widget.boundingRect()
            _x = _rect.center().x() - (_widget_rect.width() / 2)
            widget.widget().setTitleAlign('center')
            widget.setPos(_x, _y)
            _y += _widget_rect.height()

    def _align_widgets_vertical(self, v_offset):
        if not self._widgets:
            return
        _rect = self.boundingRect()
        _y = _rect.center().y() + v_offset
        _widget_height = 0.0
        for widget in self._widgets.values():
            _widget_rect = widget.boundingRect()
            _widget_height += _widget_rect.height()
        _y -= _widget_height / 2

        for widget in self._widgets.values():
            _widget_rect = widget.boundingRect()
            _x = _rect.center().x() - (_widget_rect.width() / 2)
            widget.widget().setTitleAlign('center')
            widget.setPos(_x, _y)
            _y += _widget_rect.height()

    def align_widgets(self, v_offset=0.0):
        """
        Align node widgets to the default center of the node.

        Args:
            v_offset (float): vertical offset.
        """
        if self.node.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._align_widgets_horizontal(v_offset)
        elif self.node.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._align_widgets_vertical(v_offset)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def _set_text_color(self, color):
        """
        set text color.

        Args:
            color (tuple): color value in (r, g, b, a).
        """
        _text_color = QtGui.QColor(color)
        self._textItem.setDefaultTextColor(_text_color)

    def _calc_size_horizontal(self):
        # width, height from node name text.
        _text_w = self._textItem.boundingRect().width()
        _text_h = self._textItem.boundingRect().height()

        # width, height from node embedded widgets.
        _widget_width = 0.0
        _widget_height = 0.0
        for widget in self._widgets.values():
            _w_width = widget.boundingRect().width()
            _w_height = widget.boundingRect().height()
            if _w_width > _widget_width:
                _widget_width = _w_width
            _widget_height += _w_height

        _side_padding = 0
        if _widget_width:
            _side_padding = 10

        _width = _text_w + _side_padding
        _height = max([_text_h, _widget_height])
        if _widget_width:
            # add additional width for node widget.
            _width += _widget_width
        if _widget_height:
            # add bottom margin for node widget.
            _height += 4.0
        _height *= 1.05
        return _width, _height

    def _calc_size_vertical(self):
        _widget_width = 0.0
        _widget_height = 0.0
        for widget in self._widgets.values():
            if widget.boundingRect().width() > _widget_width:
                _widget_width = widget.boundingRect().width()
            _widget_height += widget.boundingRect().height()

        _width = max([_widget_width])
        _height = _widget_height
        return _width, _height

    def calc_size(self, add_w=0.0, add_h=0.0):
        """
        Calculates the minimum node size.

        Args:
            add_w (float): additional width.
            add_h (float): additional height.

        Returns:
            tuple(float, float): width, height.
        """
        if self.node.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            _width, _height = self._calc_size_horizontal()
        elif self.node.layout_direction is EnumLayoutDirection.VERTICAL.value:
            _width, _height = self._calc_size_vertical()
        else:
            raise RuntimeError('Node graph layout direction not valid!')

        # additional width, height.
        _width += add_w
        _height += add_h
        return _width, _height

    def auto_switch_mode(self):
        """
        Decide whether to draw the node with proxy mode.
        (this is called at the start in the "self.paint()" function.)
        """
        if ITEM_CACHE_MODE is self.CacheMode.ItemCoordinateCache:
            return

        _rect = self.sceneBoundingRect()
        _l = self.get_view().mapToGlobal(
            self.get_view().mapFromScene(_rect.topLeft()))
        _r = self.get_view().mapToGlobal(
            self.get_view().mapFromScene(_rect.topRight()))
        # width is the node width in screen
        _width = _r.x() - _l.x()

        self.set_proxy_mode(_width < self._proxyModeThreshold)

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

        self._textItem.setVisible(_visible)
        self._iconItem.setVisible(_visible)

    # ---------------------------------------------------
    # override evnet handle
    # ---------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        """
        Re-implemented to emit "node_double_clicked" signal.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:

            # enable text item edit mode.
            _items = self.scene().items(event.scenePos())
            if self._textItem in _items:
                self._textItem.set_editable(True)
                self._textItem.setFocus()
                event.ignore()
                return
        super(BaseSTCStateNodeViewItem, self).mouseDoubleClickEvent(event)
