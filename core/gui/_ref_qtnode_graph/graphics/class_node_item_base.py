# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_node_item_base.py
# ------------------------------------------------------------------------------
#
# File          : class_node_item_base.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from collections import OrderedDict

from gui import QtGui, QtCore, QtWidgets

from ..core.define import (
    ITEM_CACHE_MODE,
    ICON_NODE_BASE,
    EnumLayoutDirection,
    EnumNodeStyleProperty,
    EnumPortStyleProperty,
    EnumPortType,
    Z_VAL_NODE
)
from ..core.exceptions import NodeWidgetError
from .class_base import BaseNodeItem
from .class_overlay_disable_item import XDisabledItem
from .class_text_node_item import NodeTextItem
from .class_port_item import PortItem, CustomPortItem


class NodeItem(BaseNodeItem):
    """
    Base Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='node', parent=None):
        super(NodeItem, self).__init__(name, parent)
        _pixmap = QtGui.QPixmap(ICON_NODE_BASE)
        if _pixmap.size().height() > EnumNodeStyleProperty.ICON_SIZE.value:
            _pixmap = _pixmap.scaledToHeight(EnumNodeStyleProperty.ICON_SIZE.value, QtCore.Qt.TransformationMode.SmoothTransformation)
        self._properties['icon'] = ICON_NODE_BASE
        self._iconItem = QtWidgets.QGraphicsPixmapItem(_pixmap, self)
        self._iconItem.setTransformationMode(QtCore.Qt.TransformationMode.SmoothTransformation)
        self._textItem = NodeTextItem(self.name, self)
        self._xItem = XDisabledItem(self, 'DISABLED')
        self._inputItems = OrderedDict()
        self._outputItems = OrderedDict()
        self._widgets = OrderedDict()
        self._proxyMode = False
        self._proxyModeThreshold = 70

    # def post_init(self, viewer, pos=None):
    #     """
    #     Called after node has been added into the scene.
    #
    #     Args:
    #         viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer
    #         pos (tuple): the cursor pos if node is called with tab search.
    #     """
    #     if self.layout_direction == EnumLayoutDirection.VERTICAL.value:
    #         _font = QtGui.QFont()
    #         _font.setPointSize(15)
    #         self._textItem.setFont(_font)
    #
    #         # hide port text items for vertical layout.
    #         if self.layout_direction is EnumLayoutDirection.VERTICAL.value:
    #             for text_item in self._inputItems.values():
    #                 text_item.setVisible(False)
    #             for text_item in self._outputItems.values():
    #                 text_item.setVisible(False)

    def _paint_horizontal(self, painter, option, widget):
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
        if self.selected:
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
            painter.drawRoundedRect(_rect, _radius, _radius)

        # node name background.
        _padding = 3.0, 2.0
        _text_rect = self._textItem.boundingRect()
        _text_rect = QtCore.QRectF(_text_rect.x() + _padding[0],
                                   _rect.y() + _padding[1],
                                   _rect.width() - _padding[0] - _margin,
                                   _text_rect.height() - (_padding[1] * 2))
        if self.selected:
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 80))
        painter.drawRoundedRect(_text_rect, 3.0, 3.0)

        # node border
        if self.selected:
            _border_width = 1.2
            _border_color = QtGui.QColor(
                *EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value
            )
        else:
            _border_width = 0.8
            _border_color = QtGui.QColor(*self.border_color)

        _border_rect = QtCore.QRectF(_rect.left(), _rect.top(),
                                     _rect.width(), _rect.height())

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
        if self.selected:
            painter.setBrush(
                QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value)
            )
            painter.drawRoundedRect(_rect, _radius, _radius)

        # top & bottom edge background.
        _padding = 2.0
        _height = 10
        if self.selected:
            painter.setBrush(QtGui.QColor(*EnumNodeStyleProperty.SELECTED_COLOR.value))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 80))
        for y in [_rect.y() + _padding, _rect.height() - _height - 1]:
            _edge_rect = QtCore.QRectF(_rect.x() + _padding, y,
                                      _rect.width() - (_padding * 2), _height)
            painter.drawRoundedRect(_edge_rect, 3.0, 3.0)

        # node border
        _border_width = 0.8
        _border_color = QtGui.QColor(*self.border_color)
        if self.selected:
            _border_width = 1.2
            _border_color = QtGui.QColor(
                *EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value
            )
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
        if self.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._paint_horizontal(painter, option, widget)
        elif self.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._paint_vertical(painter, option, widget)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def mousePressEvent(self, event):
        """
        Re-implemented to ignore event if LMB is over port collision area.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            for p in self._inputItems.keys():
                if p.hovered:
                    event.ignore()
                    return
            for p in self._outputItems.keys():
                if p.hovered:
                    event.ignore()
                    return
        super(NodeItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Re-implemented to ignore event if Alt modifier is pressed.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        if event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier:
            event.ignore()
            return
        super(NodeItem, self).mouseReleaseEvent(event)

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

            _view = self.get_view()
            if _view:
                _view.sigNodeDoubleClicked.emit(self.id)
        super(NodeItem, self).mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        """
        Re-implemented to update pipes on selection changed.

        Args:
            change:
            value:
        """
        if change == self.GraphicsItemChange.ItemSelectedChange and self.scene():
            self.reset_pipes()
            if value:
                self.highlight_pipes()
            self.setZValue(Z_VAL_NODE)
            if not self.selected:
                self.setZValue(Z_VAL_NODE + 1)

        return super(NodeItem, self).itemChange(change, value)

    def _tooltip_disable(self, state):
        """
        Updates the node tooltip when the node is enabled/disabled.

        Args:
            state (bool): node disable state.
        """
        _tooltip = '<b>{}</b>'.format(self.name)
        if state:
            _tooltip += ' <font color="red"><b>(DISABLED)</b></font>'
        _tooltip += '<br/>{}<br/>'.format(self.type_)
        self.setToolTip(_tooltip)

    def _set_base_size(self, add_w=0.0, add_h=0.0):
        """
        Sets the initial base size for the node.

        Args:
            add_w (float): add additional width.
            add_h (float): add additional height.
        """
        self._width, self._height = self.calc_size(add_w, add_h)
        if self._width < EnumNodeStyleProperty.WIDTH.value:
            self._width = EnumNodeStyleProperty.WIDTH.value
        if self._height < EnumNodeStyleProperty.HEIGHT.value:
            self._height = EnumNodeStyleProperty.HEIGHT.value

    def _set_text_color(self, color):
        """
        set text color.

        Args:
            color (tuple): color value in (r, g, b, a).
        """
        _text_color = QtGui.QColor(*color)
        for port, text in self._inputItems.items():
            text.setDefaultTextColor(_text_color)
        for port, text in self._outputItems.items():
            text.setDefaultTextColor(_text_color)
        self._textItem.setDefaultTextColor(_text_color)

    def activate_pipes(self):
        """
        active pipe color.
        """
        _ports = self.inputs + self.outputs
        for port in _ports:
            for pipe in port.connected_pipes:
                pipe.activate()

    def highlight_pipes(self):
        """
        Highlight pipe color.
        """
        _ports = self.inputs + self.outputs
        for port in _ports:
            for pipe in port.connected_pipes:
                pipe.highlight()

    def reset_pipes(self):
        """
        Reset all the pipe colors.
        """
        _ports = self.inputs + self.outputs
        for port in _ports:
            for pipe in port.connected_pipes:
                pipe.reset()

    def _calc_size_horizontal(self):
        # width, height from node name text.
        _text_w = self._textItem.boundingRect().width()
        _text_h = self._textItem.boundingRect().height()

        # width, height from node ports.
        _port_width = 0.0
        _p_input_text_width = 0.0
        _p_output_text_width = 0.0
        _p_input_height = 0.0
        _p_output_height = 0.0
        for port, text in self._inputItems.items():
            if not port.isVisible():
                continue
            if not _port_width:
                _port_width = port.boundingRect().width()
            _t_width = text.boundingRect().width()
            if text.isVisible() and _t_width > _p_input_text_width:
                _p_input_text_width = text.boundingRect().width()
            _p_input_height += port.boundingRect().height()
        for port, text in self._outputItems.items():
            if not port.isVisible():
                continue
            if not _port_width:
                _port_width = port.boundingRect().width()
            _t_width = text.boundingRect().width()
            if text.isVisible() and _t_width > _p_output_text_width:
                _p_output_text_width = text.boundingRect().width()
            _p_output_height += port.boundingRect().height()

        _port_text_width = _p_input_text_width + _p_output_text_width

        # width, height from node embedded widgets.
        _widget_width = 0.0
        _widget_height = 0.0
        for widget in self._widgets.values():
            _w_width = widget.boundingRect().width()
            _w_height = widget.boundingRect().height()
            if _w_width > _widget_width:
                _widget_width = _w_width
            _widget_height += _w_height

        _side_padding = 0.0
        if all([_widget_width, _p_input_text_width, _p_output_text_width]):
            _port_text_width = max([_p_input_text_width, _p_output_text_width])
            _port_text_width *= 2
        elif _widget_width:
            _side_padding = 10

        _width = _port_width + max([_text_w, _port_text_width]) + _side_padding
        _height = max([_text_h, _p_input_height, _p_output_height, _widget_height])
        if _widget_width:
            # add additional width for node widget.
            _width += _widget_width
        if _widget_height:
            # add bottom margin for node widget.
            _height += 4.0
        _height *= 1.05
        return _width, _height

    def _calc_size_vertical(self):
        _p_input_width = 0.0
        _p_output_width = 0.0
        _p_input_height = 0.0
        _p_output_height = 0.0
        for port in self._inputItems.keys():
            if port.isVisible():
                _p_input_width += port.boundingRect().width()
                if not _p_input_height:
                    _p_input_height = port.boundingRect().height()
        for port in self._outputItems.keys():
            if port.isVisible():
                _p_output_width += port.boundingRect().width()
                if not _p_output_height:
                    _p_output_height = port.boundingRect().height()

        _widget_width = 0.0
        _widget_height = 0.0
        for widget in self._widgets.values():
            if widget.boundingRect().width() > _widget_width:
                _widget_width = widget.boundingRect().width()
            _widget_height += widget.boundingRect().height()

        _width = max([_p_input_width, _p_output_width, _widget_width])
        _height = _p_input_height + _p_output_height + _widget_height
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
        if self.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            _width, _height = self._calc_size_horizontal()
        elif self.layout_direction is EnumLayoutDirection.VERTICAL.value:
            _width, _height = self._calc_size_vertical()
        else:
            raise RuntimeError('Node graph layout direction not valid!')

        # additional width, height.
        _width += add_w
        _height += add_h
        return _width, _height

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
        if self.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._align_icon_horizontal(h_offset, v_offset)
        elif self.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._align_icon_vertical(h_offset, v_offset)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

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
        if self.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._align_label_horizontal(h_offset, v_offset)
        elif self.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._align_label_vertical(h_offset, v_offset)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def _align_widgets_horizontal(self, v_offset):
        if not self._widgets:
            return
        _rect = self.boundingRect()
        _y = _rect.y() + v_offset
        _inputs = [p for p in self.inputs if p.isVisible()]
        _outputs = [p for p in self.outputs if p.isVisible()]
        for widget in self._widgets.values():
            _widget_rect = widget.boundingRect()
            if not _inputs:
                _x = _rect.left() + 10
                widget.widget().setTitleAlign('left')
            elif not _outputs:
                _x = _rect.right() - _widget_rect.width() - 10
                widget.widget().setTitleAlign('right')
            else:
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
        if self.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._align_widgets_horizontal(v_offset)
        elif self.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._align_widgets_vertical(v_offset)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def _align_ports_horizontal(self, v_offset):
        _width = self._width
        _txt_offset = EnumPortStyleProperty.CLICK_FALLOFF.value - 2
        _spacing = 1

        # adjust input position
        _inputs = [p for p in self.inputs if p.isVisible()]
        if _inputs:
            _port_width = _inputs[0].boundingRect().width()
            _port_height = _inputs[0].boundingRect().height()
            _port_x = (_port_width / 2) * -1
            _port_y = v_offset
            for port in _inputs:
                port.setPos(_port_x, _port_y)
                _port_y += _port_height + _spacing
        # adjust input text position
        for port, text in self._inputItems.items():
            if port.isVisible():
                _txt_x = port.boundingRect().width() / 2 - _txt_offset
                text.setPos(_txt_x, port.y() - 1.5)

        # adjust output position
        _outputs = [p for p in self.outputs if p.isVisible()]
        if _outputs:
            _port_width = _outputs[0].boundingRect().width()
            _port_height = _outputs[0].boundingRect().height()
            _port_x = _width - (_port_width / 2)
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
            _port_y = (_port_height / 2) * -1
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
            _port_y = self._height - (_port_height / 2)
            for port in _outputs:
                port.setPos(_port_x - _half_width, _port_y)
                _port_x += _delta

    def align_ports(self, v_offset=0.0):
        """
        Align input, output ports in the node layout.

        Args:
            v_offset (float): port vertical offset.
        """
        if self.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._align_ports_horizontal(v_offset)
        elif self.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._align_ports_vertical(v_offset)
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def _draw_node_horizontal(self):
        _height = self._textItem.boundingRect().height() + 4.0

        # update port text items in visibility.
        for port, text in self._inputItems.items():
            text.setVisible(port.display_name)
        for port, text in self._outputItems.items():
            text.setVisible(port.display_name)

        # setup initial base size.
        self._set_base_size(add_h=_height)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label()
        # align icon
        self.align_icon(h_offset=2.0, v_offset=1.0)
        # arrange input and output ports.
        self.align_ports(v_offset=_height)
        # arrange node widgets
        self.align_widgets(v_offset=_height)

        self.update()

    def _draw_node_vertical(self):
        # hide the port text items in vertical layout.
        for port, text in self._inputItems.items():
            text.setVisible(False)
        for port, text in self._outputItems.items():
            text.setVisible(False)

        # setup initial base size.
        self._set_base_size()
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- setup node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label(h_offset=6)
        # align icon
        self.align_icon(h_offset=6, v_offset=4)
        # arrange input and output ports.
        self.align_ports()
        # arrange node widgets
        self.align_widgets()

        self.update()

    def draw_node(self):
        """
        Re-draw the node item in the scene with proper
        calculated size and widgets aligned.
        """
        if self.layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            self._draw_node_horizontal()
        elif self.layout_direction is EnumLayoutDirection.VERTICAL.value:
            self._draw_node_vertical()
        else:
            raise RuntimeError('Node graph layout direction not valid!')

    def post_init(self, viewer=None, pos=None):
        """
        Called after node has been added into the scene.
        Adjust the node layout and form after the node has been added.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): not used
            pos (tuple): cursor position.
        """
        self.draw_node()

        # set initial node position.
        if pos:
            self.xy_pos = pos

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

        # input port text visibility.
        for port, text in self._inputItems.items():
            if port.display_name:
                text.setVisible(_visible)

        # output port text visibility.
        for port, text in self._outputItems.items():
            if port.display_name:
                text.setVisible(_visible)

        self._textItem.setVisible(_visible)
        self._iconItem.setVisible(_visible)

    @property
    def icon(self):
        return self._properties['icon']

    @icon.setter
    def icon(self, path=None):
        self._properties['icon'] = path
        path = path or ICON_NODE_BASE
        _pixmap = QtGui.QPixmap(path)
        if _pixmap.size().height() > EnumNodeStyleProperty.ICON_SIZE.value:
            _pixmap = _pixmap.scaledToHeight(
                EnumNodeStyleProperty.ICON_SIZE.value,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
        self._iconItem.setPixmap(_pixmap)
        if self.scene():
            self.post_init()
        self.update()

    @BaseNodeItem.layout_direction.setter
    def layout_direction(self, value=0):
        BaseNodeItem.layout_direction.fset(self, value)
        self.draw_node()

    @BaseNodeItem.width.setter
    def width(self, width=0.0):
        _w, _h = self.calc_size()
        width = width if width > _w else _w
        BaseNodeItem.width.fset(self, width)

    @BaseNodeItem.height.setter
    def height(self, height=0.0):
        _w, _h = self.calc_size()
        _h = 70 if _h < 70 else _h
        height = height if height > _h else _h
        BaseNodeItem.height.fset(self, height)

    @BaseNodeItem.disabled.setter
    def disabled(self, state=False):
        BaseNodeItem.disabled.fset(self, state)
        for n, w in self._widgets.items():
            w.widget().setDisabled(state)
        self._tooltip_disable(state)
        self._xItem.setVisible(state)

    @BaseNodeItem.selected.setter
    def selected(self, selected=False):
        BaseNodeItem.selected.fset(self, selected)
        if selected:
            self.highlight_pipes()

    @BaseNodeItem.name.setter
    def name(self, name=''):
        BaseNodeItem.name.fset(self, name)
        if name == self._textItem.toPlainText():
            return
        self._textItem.setPlainText(name)
        if self.scene():
            self.align_label()
        self.update()

    @BaseNodeItem.color.setter
    def color(self, color=(100, 100, 100, 255)):
        BaseNodeItem.color.fset(self, color)
        if self.scene():
            self.scene().update()
        self.update()

    @BaseNodeItem.text_color.setter
    def text_color(self, color=(100, 100, 100, 255)):
        BaseNodeItem.text_color.fset(self, color)
        self._set_text_color(color)
        self.update()

    @property
    def text_item(self):
        """
        Get the node name text qgraphics item.

        Returns:
            NodeTextItem: node text object.
        """
        return self._textItem

    @property
    def inputs(self):
        """
        Returns:
            list[PortItem]: input port graphic items.
        """
        return list(self._inputItems.keys())

    @property
    def outputs(self):
        """
        Returns:
            list[PortItem]: output port graphic items.
        """
        return list(self._outputItems.keys())

    def _add_port(self, port):
        """
        Adds a port qgraphics item into the node.

        Args:
            port (PortItem): port item.

        Returns:
            PortItem: port qgraphics item.
        """
        _text = QtWidgets.QGraphicsTextItem(port.name, self)
        _text.font().setPointSize(8)
        _text.setFont(_text.font())
        _text.setVisible(port.display_name)
        _text.setCacheMode(ITEM_CACHE_MODE)
        if port.port_type == EnumPortType.IN.value:
            self._inputItems[port] = _text
        elif port.port_type == EnumPortType.OUT.value:
            self._outputItems[port] = _text
        if self.scene():
            self.post_init()
        return port

    def add_input(self, name='input', multi_port=False, display_name=True,
                  locked=False, painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        IN_PORT.

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): display the port name.
            locked (bool): locked state.
            painter_func (function): custom paint function.

        Returns:
            PortItem: input port qgraphics item.
        """
        if painter_func:
            _port = CustomPortItem(self, painter_func)
        else:
            _port = PortItem(self)
        _port.name = name
        _port.port_type = EnumPortType.IN.value
        _port.multi_connection = multi_port
        _port.display_name = display_name
        _port.locked = locked
        return self._add_port(_port)

    def add_output(self, name='output', multi_port=False, display_name=True,
                   locked=False, painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        OUT_PORT.

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): display the port name.
            locked (bool): locked state.
            painter_func (function): custom paint function.

        Returns:
            PortItem: output port qgraphics item.
        """
        if painter_func:
            _port = CustomPortItem(self, painter_func)
        else:
            _port = PortItem(self)
        _port.name = name
        _port.port_type = EnumPortType.OUT.value
        _port.multi_connection = multi_port
        _port.display_name = display_name
        _port.locked = locked
        return self._add_port(_port)

    def _delete_port(self, port, text):
        """
        Removes port item and port text from node.

        Args:
            port (PortItem): port object.
            text (QtWidgets.QGraphicsTextItem): port text object.
        """
        port.setParentItem(None)
        text.setParentItem(None)
        self.scene().removeItem(port)
        self.scene().removeItem(text)
        del port
        del text

    def delete_input(self, port):
        """
        Remove input port from node.

        Args:
            port (PortItem): port object.
        """
        self._delete_port(port, self._inputItems.pop(port))

    def delete_output(self, port):
        """
        Remove output port from node.

        Args:
            port (PortItem): port object.
        """
        self._delete_port(port, self._outputItems.pop(port))

    def get_input_text_item(self, port_item):
        """
        Args:
            port_item (PortItem): port item.

        Returns:
            QGraphicsTextItem: graphic item used for the port text.
        """
        return self._inputItems[port_item]

    def get_output_text_item(self, port_item):
        """
        Args:
            port_item (PortItem): port item.

        Returns:
            QGraphicsTextItem: graphic item used for the port text.
        """
        return self._outputItems[port_item]

    @property
    def widgets(self):
        return self._widgets.copy()

    def add_widget(self, widget):
        self._widgets[widget.get_name()] = widget

    def get_widget(self, name):
        _widget = self._widgets.get(name)
        if _widget:
            return _widget
        raise NodeWidgetError('node has no widget "{}"'.format(name))

    def has_widget(self, name):
        return name in self._widgets.keys()

    def from_dict(self, node_dict):
        super(NodeItem, self).from_dict(node_dict)
        _widgets = node_dict.pop('widgets', {})
        for name, value in _widgets.items():
            if self._widgets.get(name):
                self._widgets[name].set_value(value)
