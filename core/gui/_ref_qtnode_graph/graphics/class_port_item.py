# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_port_item.py
# ------------------------------------------------------------------------------
#
# File          : class_port_item.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtGui, QtCore, QtWidgets

from ..core.define import (
    EnumPortType, EnumPortStyleProperty,
    Z_VAL_PORT,
    ITEM_CACHE_MODE)


class PortItem(QtWidgets.QGraphicsItem):
    """
    Base Port Item.
    """

    def __init__(self, parent=None):
        super(PortItem, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self.setCacheMode(ITEM_CACHE_MODE)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges, True)
        self.setZValue(Z_VAL_PORT)
        self._pipes = []
        self._width = EnumPortStyleProperty.SIZE.value
        self._height = EnumPortStyleProperty.SIZE.value
        self._hovered = False
        self._name = 'port'
        self._displayName = True
        self._color = EnumPortStyleProperty.COLOR.value
        self._borderColor = EnumPortStyleProperty.BORDER_COLOR.value
        self._borderSize = 1
        self._portType = None
        self._multiConnection = False
        self._locked = False

    def __str__(self):
        return '{}.PortItem("{}")'.format(self.__module__, self.name)

    def __repr__(self):
        return '{}.PortItem("{}")'.format(self.__module__, self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0,
                             self._width + EnumPortStyleProperty.CLICK_FALLOFF.value,
                             self._height)

    def paint(self, painter, option, widget):
        """
        Draws the circular port.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        #  display falloff collision for debugging
        # ----------------------------------------------------------------------
        # pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 80), 0.8)
        # pen.setStyle(QtCore.Qt.DotLine)
        # painter.setPen(pen)
        # painter.drawRect(self.boundingRect())
        # ----------------------------------------------------------------------

        _rect_w = self._width / 1.8
        _rect_h = self._height / 1.8
        _rect_x = self.boundingRect().center().x() - (_rect_w / 2)
        _rect_y = self.boundingRect().center().y() - (_rect_h / 2)
        _port_rect = QtCore.QRectF(_rect_x, _rect_y, _rect_w, _rect_h)

        if self._hovered:
            _color = QtGui.QColor(*EnumPortStyleProperty.HOVER_COLOR.value)
            _border_color = QtGui.QColor(*EnumPortStyleProperty.HOVER_BORDER_COLOR.value)
        elif self.connected_pipes:
            _color = QtGui.QColor(*EnumPortStyleProperty.ACTIVE_COLOR.value)
            _border_color = QtGui.QColor(*EnumPortStyleProperty.ACTIVE_BORDER_COLOR.value)
        else:
            _color = QtGui.QColor(*self.color)
            _border_color = QtGui.QColor(*self.border_color)

        _pen = QtGui.QPen(_border_color, 1.8)
        painter.setPen(_pen)
        painter.setBrush(_color)
        painter.drawEllipse(_port_rect)

        if self.connected_pipes and not self._hovered:
            painter.setBrush(_border_color)
            _w = _port_rect.width() / 2.5
            _h = _port_rect.height() / 2.5
            _rect = QtCore.QRectF(_port_rect.center().x() - _w / 2,
                                 _port_rect.center().y() - _h / 2,
                                 _w, _h)
            _border_color = QtGui.QColor(*self.border_color)
            _pen = QtGui.QPen(_border_color, 1.6)
            painter.setPen(_pen)
            painter.setBrush(_border_color)
            painter.drawEllipse(_rect)
        elif self._hovered:
            if self.multi_connection:
                _pen = QtGui.QPen(_border_color, 1.4)
                painter.setPen(_pen)
                painter.setBrush(_color)
                _w = _port_rect.width() / 1.8
                _h = _port_rect.height() / 1.8
            else:
                painter.setBrush(_border_color)
                _w = _port_rect.width() / 3.5
                _h = _port_rect.height() / 3.5
            _rect = QtCore.QRectF(_port_rect.center().x() - _w / 2,
                                 _port_rect.center().y() - _h / 2,
                                 _w, _h)
            painter.drawEllipse(_rect)
        painter.restore()

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemScenePositionHasChanged:
            self.redraw_connected_pipes()
        return super(PortItem, self).itemChange(change, value)

    def mousePressEvent(self, event):
        super(PortItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(PortItem, self).mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self._hovered = True
        super(PortItem, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hovered = False
        super(PortItem, self).hoverLeaveEvent(event)

    def view_start_connection(self):
        _view = self.scene().get_view()
        _view.start_live_connection(self)

    def redraw_connected_pipes(self):
        if not self.connected_pipes:
            return
        for pipe in self.connected_pipes:
            if self.port_type == EnumPortType.IN.value:
                pipe.draw_path(self, pipe.output_port)
            elif self.port_type == EnumPortType.OUT.value:
                pipe.draw_path(pipe.input_port, self)

    def add_pipe(self, pipe):
        self._pipes.append(pipe)

    def remove_pipe(self, pipe):
        self._pipes.remove(pipe)

    @property
    def connected_pipes(self):
        return self._pipes

    @property
    def connected_ports(self):
        _ports = []
        _port_types = {
            EnumPortType.IN.value: 'output_port',
            EnumPortType.OUT.value: 'input_port'
        }
        for pipe in self.connected_pipes:
            _ports.append(getattr(pipe, _port_types[self.port_type]))
        return _ports

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value=False):
        self._hovered = value

    @property
    def node(self):
        return self.parentItem()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name=''):
        self._name = name.strip()

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, display=True):
        self._display_name = display

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self._color = color
        self.update()

    @property
    def border_color(self):
        return self._borderColor

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self._borderColor = color

    @property
    def border_size(self):
        return self._borderSize

    @border_size.setter
    def border_size(self, size=2):
        self._borderSize = size

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, value=False):
        self._locked = value
        _conn_type = 'multi' if self.multi_connection else 'single'
        _tooltip = '{}: ({})'.format(self.name, _conn_type)
        if value:
            _tooltip += ' (L)'
        self.setToolTip(_tooltip)

    @property
    def multi_connection(self):
        return self._multiConnection

    @multi_connection.setter
    def multi_connection(self, mode=False):
        _conn_type = 'multi' if mode else 'single'
        self.setToolTip('{}: ({})'.format(self.name, _conn_type))
        self._multiConnection = mode

    @property
    def port_type(self):
        return self._portType

    @port_type.setter
    def port_type(self, port_type):
        self._portType = port_type

    def connect_to(self, port):
        if not port:
            for pipe in self.connected_pipes:
                pipe.delete()
            return
        if self.scene():
            _view = self.scene().get_view()
            _view.establish_connection(self, port)
        # redraw the ports.
        port.update()
        self.update()

    def disconnect_from(self, port):
        _port_types = {
            EnumPortType.IN.value: 'output_port',
            EnumPortType.OUT.value: 'input_port'
        }
        for pipe in self.connected_pipes:
            _connected_port = getattr(pipe, _port_types[self.port_type])
            if _connected_port == port:
                pipe.delete()
                break
        # redraw the ports.
        port.update()
        self.update()


class CustomPortItem(PortItem):
    """
    Custom port item for drawing custom shape port.
    """

    def __init__(self, parent=None, paint_func=None):
        super(CustomPortItem, self).__init__(parent)
        self._portPainter = paint_func

    def set_painter(self, func=None):
        """
        Set custom paint function for drawing.

        Args:
            func (function): paint function.
        """
        self._portPainter = func

    def paint(self, painter, option, widget):
        """
        Draws the port item.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        if self._portPainter:
            _rect_w = self._width / 1.8
            _rect_h = self._height / 1.8
            _rect_x = self.boundingRect().center().x() - (_rect_w / 2)
            _rect_y = self.boundingRect().center().y() - (_rect_h / 2)
            _port_rect = QtCore.QRectF(_rect_x, _rect_y, _rect_w, _rect_h)
            _port_info = {
                'port_type': self.port_type,
                'color': self.color,
                'border_color': self.border_color,
                'multi_connection': self.multi_connection,
                'connected': bool(self.connected_pipes),
                'hovered': self.hovered,
                'locked': self.locked,
            }
            self._portPainter(painter, _port_rect, _port_info)
        else:
            super(CustomPortItem, self).paint(painter, option, widget)
