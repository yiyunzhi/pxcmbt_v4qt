# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_pipe_item.py
# ------------------------------------------------------------------------------
#
# File          : class_pipe_item.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import math

from core.gui.qtimp import QtCore, QtGui, QtWidgets

from ..core.define import (
    EnumLayoutDirection,
    EnumPipeShape,
    EnumPipeStyleProperty,
    EnumPortType,
    ITEM_CACHE_MODE,
    Z_VAL_PIPE,
    Z_VAL_NODE_WIDGET
)
from .class_port_item import PortItem

PIPE_STYLES = {
    EnumPipeStyleProperty.DRAW_TYPE_DEFAULT.value: QtCore.Qt.PenStyle.SolidLine,
    EnumPipeStyleProperty.DRAW_TYPE_DASHED.value: QtCore.Qt.PenStyle.DashLine,
    EnumPipeStyleProperty.DRAW_TYPE_DOTTED.value: QtCore.Qt.PenStyle.DotLine
}


class PipeHandle(QtWidgets.QGraphicsRectItem):
    def __init__(self, parent: 'PipeItem'):
        super().__init__()
        if parent is not None:
            self.setParentItem(parent)
        self.setZValue(parent.zValue() + 1)
        self.setAcceptHoverEvents(True)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable | self.GraphicsItemFlag.ItemIsMovable)
        self._color = EnumPipeStyleProperty.COLOR.value
        self._size = 6
        self.setCacheMode(ITEM_CACHE_MODE)
        self.setRect(0, 0, 6, 6)

    def activate(self):
        if self.parentItem() is None:
            return
        if self.parentItem().scene() is None:
            return
        if self.scene() is None:
            self.parentItem().scene().addItem(self)
        self.show()
        print('--->activate')

    def deactivate(self):
        self.hide()
        print('--->deactivate')

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        print('---->mousePressed')
        event.ignore()

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: QtWidgets.QWidget = None) -> None:
        painter.save()
        _color = QtGui.QColor(*self._color)
        _pen_width = EnumPipeStyleProperty.WIDTH.value
        _pen = QtGui.QPen(_color, _pen_width, QtCore.Qt.PenStyle.SolidLine)
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)

        painter.save()
        painter.setPen(_pen)
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        painter.drawRect(self.rect())
        painter.restore()


class PipeItem(QtWidgets.QGraphicsPathItem):
    """
    Base Pipe item used for drawing node connections.
    """

    def __init__(self, input_port=None, output_port=None):
        super(PipeItem, self).__init__()
        self.setZValue(Z_VAL_PIPE)
        self.setAcceptHoverEvents(True)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self._color = EnumPipeStyleProperty.COLOR.value
        self._style = EnumPipeStyleProperty.DRAW_TYPE_DEFAULT.value
        self._active = False
        self._highlight = False
        self._inputPort = input_port
        self._outputPort = output_port
        _size = 6.0
        self._arrow = QtGui.QPolygonF()
        self._arrow.append(QtCore.QPointF(-_size, _size))
        self._arrow.append(QtCore.QPointF(0.0, -_size * 1.5))
        self._arrow.append(QtCore.QPointF(_size, _size))
        self.setCacheMode(ITEM_CACHE_MODE)
        self._wayPoints = [PipeHandle(self), PipeHandle(self)]

    def __repr__(self):
        _in_name = self._inputPort.name if self._inputPort else ''
        _out_name = self._outputPort.name if self._outputPort else ''
        return '{}.Pipe(\'{}\', \'{}\')'.format(
            self.__module__, _in_name, _out_name)

    def hoverEnterEvent(self, event):
        self.activate()
        _wp_x = self.path().pointAtPercent(0.25).x()
        _wp_y = self.path().pointAtPercent(0.25).y()
        self._wayPoints[0].setPos(_wp_x, _wp_y)
        self._wayPoints[0].activate()
        _wp_x = self.path().pointAtPercent(0.75).x()
        _wp_y = self.path().pointAtPercent(0.75).y()
        self._wayPoints[1].setPos(_wp_x, _wp_y)
        self._wayPoints[1].activate()

    def hoverLeaveEvent(self, event):
        self._wayPoints[0].deactivate()
        self._wayPoints[1].deactivate()
        self.reset()
        if self.input_port and self.output_port:
            if self.input_port.node.selected:
                self.highlight()
            elif self.output_port.node.selected:
                self.highlight()
        if self.isSelected():
            self.highlight()

    def paint(self, painter, option, widget=None):
        """
        Draws the connection line between nodes.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        _color = QtGui.QColor(*self._color)
        _pen_style = PIPE_STYLES.get(self.style)
        _pen_width = EnumPipeStyleProperty.WIDTH.value
        if self._active:
            _color = QtGui.QColor(*EnumPipeStyleProperty.ACTIVE_COLOR.value)
            if _pen_style == QtCore.Qt.PenStyle.DashDotDotLine:
                _pen_width += 1
            else:
                _pen_width += 0.35
        elif self._highlight:
            _color = QtGui.QColor(*EnumPipeStyleProperty.HIGHLIGHT_COLOR.value)
            _pen_style = PIPE_STYLES.get(EnumPipeStyleProperty.DRAW_TYPE_DEFAULT.value)

        if self.is_disabled():
            if not self._active:
                _color = QtGui.QColor(*EnumPipeStyleProperty.DISABLED_COLOR.value)
            _pen_width += 0.2
            _pen_style = PIPE_STYLES.get(EnumPipeStyleProperty.DRAW_TYPE_DOTTED.value)

        _pen = QtGui.QPen(_color, _pen_width, _pen_style)
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)

        painter.save()
        painter.setPen(_pen)
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        painter.drawPath(self.path())

        # draw arrow
        if self.input_port and self.output_port:
            _cen_x = self.path().pointAtPercent(0.5).x()
            _cen_y = self.path().pointAtPercent(0.5).y()
            _loc_pt = self.path().pointAtPercent(0.49)
            _tgt_pt = self.path().pointAtPercent(0.51)

            _dist = math.hypot(_tgt_pt.x() - _cen_x, _tgt_pt.y() - _cen_y)
            if _dist < 0.5:
                painter.restore()
                return

            _color.setAlpha(255)
            if self._highlight:
                painter.setBrush(QtGui.QBrush(_color.lighter(150)))
            elif self._active or self.is_disabled():
                painter.setBrush(QtGui.QBrush(_color.darker(200)))
            else:
                painter.setBrush(QtGui.QBrush(_color.darker(130)))

            _pen_width = 0.6
            if _dist < 1.0:
                _pen_width *= (1.0 + _dist)

            _pen = QtGui.QPen(_color, _pen_width)
            _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
            painter.setPen(_pen)

            _transform = QtGui.QTransform()
            _transform.translate(_cen_x, _cen_y)
            _radians = math.atan2(_tgt_pt.y() - _loc_pt.y(),
                                  _tgt_pt.x() - _loc_pt.x())
            _degrees = math.degrees(_radians) - 90
            _transform.rotate(_degrees)
            if _dist < 1.0:
                _transform.scale(_dist, _dist)
            painter.drawPolygon(_transform.map(self._arrow))

        # QPaintDevice: Cannot destroy paint device that is being painted.
        painter.restore()

    def __draw_path_vertical(self, start_port, pos1, pos2, path):
        """
        Draws the vertical path between ports.

        Args:
            start_port (PortItem): port used to draw the starting point.
            pos1 (QPointF): start port position.
            pos2 (QPointF): end port position.
            path (QPainterPath): path to draw.
        """
        if self.get_view_pipe_layout() == EnumPipeShape.CURVED.value:
            _ctr_offset_y1, _ctr_offset_y2 = pos1.y(), pos2.y()
            _tangent = abs(_ctr_offset_y1 - _ctr_offset_y2)

            _max_height = start_port.node.boundingRect().height()
            _tangent = min(_tangent, _max_height)
            if start_port.port_type == EnumPortType.IN.value:
                _ctr_offset_y1 -= _tangent
                _ctr_offset_y2 += _tangent
            else:
                _ctr_offset_y1 += _tangent
                _ctr_offset_y2 -= _tangent

            _ctr_point1 = QtCore.QPointF(pos1.x(), _ctr_offset_y1)
            _ctr_point2 = QtCore.QPointF(pos2.x(), _ctr_offset_y2)
            path.cubicTo(_ctr_point1, _ctr_point2, pos2)
            self.setPath(path)
        elif self.get_view_pipe_layout() == EnumPipeShape.ANGLE.value:
            _ctr_offset_y1, _ctr_offset_y2 = pos1.y(), pos2.y()
            _distance = abs(_ctr_offset_y1 - _ctr_offset_y2) / 2
            if start_port.port_type == EnumPortType.IN.value:
                _ctr_offset_y1 -= _distance
                _ctr_offset_y2 += _distance
            else:
                _ctr_offset_y1 += _distance
                _ctr_offset_y2 -= _distance

            _ctr_point1 = QtCore.QPointF(pos1.x(), _ctr_offset_y1)
            _ctr_point2 = QtCore.QPointF(pos2.x(), _ctr_offset_y2)
            path.lineTo(_ctr_point1)
            path.lineTo(_ctr_point2)
            path.lineTo(pos2)
            self.setPath(path)

    def __draw_path_horizontal(self, start_port, pos1, pos2, path):
        """
        Draws the horizontal path between ports.

        Args:
            start_port (PortItem): port used to draw the starting point.
            pos1 (QPointF): start port position.
            pos2 (QPointF): end port position.
            path (QPainterPath): path to draw.
        """
        if self.get_view_pipe_layout() == EnumPipeShape.CURVED.value:
            _ctr_offset_x1, _ctr_offset_x2 = pos1.x(), pos2.x()
            _tangent = abs(_ctr_offset_x1 - _ctr_offset_x2)

            _max_width = start_port.node.boundingRect().width()
            _tangent = min(_tangent, _max_width)
            if start_port.port_type == EnumPortType.IN.value:
                _ctr_offset_x1 -= _tangent
                _ctr_offset_x2 += _tangent
            else:
                _ctr_offset_x1 += _tangent
                _ctr_offset_x2 -= _tangent

            _ctr_point1 = QtCore.QPointF(_ctr_offset_x1, pos1.y())
            _ctr_point2 = QtCore.QPointF(_ctr_offset_x2, pos2.y())
            path.cubicTo(_ctr_point1, _ctr_point2, pos2)
            self.setPath(path)
        elif self.get_view_pipe_layout() == EnumPipeShape.ANGLE.value:
            _ctr_offset_x1, _ctr_offset_x2 = pos1.x(), pos2.x()
            _distance = abs(_ctr_offset_x1 - _ctr_offset_x2) / 2
            if start_port.port_type == EnumPortType.IN.value:
                _ctr_offset_x1 -= _distance
                _ctr_offset_x2 += _distance
            else:
                _ctr_offset_x1 += _distance
                _ctr_offset_x2 -= _distance

            _ctr_point1 = QtCore.QPointF(_ctr_offset_x1, pos1.y())
            _ctr_point2 = QtCore.QPointF(_ctr_offset_x2, pos2.y())
            path.lineTo(_ctr_point1)
            path.lineTo(_ctr_point2)
            path.lineTo(pos2)
            self.setPath(path)

    def draw_path(self, start_port, end_port=None, cursor_pos=None):
        """
        Draws the path between ports.

        Args:
            start_port (PortItem): port used to draw the starting point.
            end_port (PortItem): port used to draw the end point.
            cursor_pos (QtCore.QPointF): cursor position if specified this
                will be the draw end point.
        """
        if not start_port:
            return
        _pos1 = start_port.scenePos()
        _pos1.setX(_pos1.x() + (start_port.boundingRect().width() / 2))
        _pos1.setY(_pos1.y() + (start_port.boundingRect().height() / 2))
        if cursor_pos:
            _pos2 = cursor_pos
        elif end_port:
            _pos2 = end_port.scenePos()
            _pos2.setX(_pos2.x() + (start_port.boundingRect().width() / 2))
            _pos2.setY(_pos2.y() + (start_port.boundingRect().height() / 2))
        else:
            return

        _line = QtCore.QLineF(_pos1, _pos2)
        _path = QtGui.QPainterPath()
        _path.moveTo(_line.x1(), _line.y1())

        if self.get_view_pipe_layout() == EnumPipeShape.STRAIGHT.value:
            _path.lineTo(_pos2)
            self.setPath(_path)
            return

        if self.get_view_layout_direction() is EnumLayoutDirection.VERTICAL.value:
            self.__draw_path_vertical(start_port, _pos1, _pos2, _path)
        elif self.get_view_layout_direction() is EnumLayoutDirection.HORIZONTAL.value:
            self.__draw_path_horizontal(start_port, _pos1, _pos2, _path)

    def reset_path(self):
        _path = QtGui.QPainterPath(QtCore.QPointF(0.0, 0.0))
        self.setPath(_path)

    @staticmethod
    def calc_distance(p1, p2):
        _x = math.pow((p2.x() - p1.x()), 2)
        _y = math.pow((p2.y() - p1.y()), 2)
        return math.sqrt(_x + _y)

    def get_port_at(self, pos, reverse=False):
        _inport_pos = self.input_port.scenePos()
        _outport_pos = self.output_port.scenePos()
        _input_dist = self.calc_distance(_inport_pos, pos)
        _output_dist = self.calc_distance(_outport_pos, pos)
        if _input_dist < _output_dist:
            _port = self.output_port if reverse else self.input_port
        else:
            _port = self.input_port if reverse else self.output_port
        return _port

    def get_view_pipe_layout(self):
        if self.scene():
            _view = self.scene().get_view()
            return _view.get_pipe_layout()

    def get_view_layout_direction(self):
        if self.scene():
            _view = self.scene().get_view()
            return _view.get_layout_direction()

    def activate(self):
        self._active = True
        _color = QtGui.QColor(*EnumPipeStyleProperty.ACTIVE_COLOR.value)
        _pen = QtGui.QPen(
            _color, 2.5, PIPE_STYLES.get(EnumPipeStyleProperty.DRAW_TYPE_DEFAULT.value)
        )
        self.setPen(_pen)

    def active(self):
        return self._active

    def highlight(self):
        self._highlight = True
        _color = QtGui.QColor(*EnumPipeStyleProperty.HIGHLIGHT_COLOR.value)
        _pen = QtGui.QPen(
            _color, 2, PIPE_STYLES.get(EnumPipeStyleProperty.DRAW_TYPE_DEFAULT.value)
        )
        self.setPen(_pen)

    def is_highlighted(self):
        return self._highlight

    def reset(self):
        self._active = False
        self._highlight = False
        _color = QtGui.QColor(*self.color)
        _pen = QtGui.QPen(_color, 2, PIPE_STYLES.get(self.style))
        self.setPen(_pen)

    def set_connections(self, port1, port2):
        _ports = {
            port1.port_type: port1,
            port2.port_type: port2
        }
        self.input_port = _ports[EnumPortType.IN.value]
        self.output_port = _ports[EnumPortType.OUT.value]
        _ports[EnumPortType.IN.value].add_pipe(self)
        _ports[EnumPortType.OUT.value].add_pipe(self)

    def is_disabled(self):
        if self.input_port and self.input_port.node.disabled:
            return True
        if self.output_port and self.output_port.node.disabled:
            return True
        return False

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemSelectedChange and self.scene():
            self.reset()
            if value:
                self.highlight()
        return super(PipeItem, self).itemChange(change, value)

    @property
    def input_port(self):
        return self._inputPort

    @input_port.setter
    def input_port(self, port):
        if isinstance(port, PortItem) or not port:
            self._inputPort = port
        else:
            self._inputPort = None

    @property
    def output_port(self):
        return self._outputPort

    @output_port.setter
    def output_port(self, port):
        if isinstance(port, PortItem) or not port:
            self._outputPort = port
        else:
            self._outputPort = None

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style):
        self._style = style

    def delete(self):
        if self.input_port and self.input_port.connected_pipes:
            self.input_port.remove_pipe(self)
        if self.output_port and self.output_port.connected_pipes:
            self.output_port.remove_pipe(self)
        if self.scene():
            self.scene().removeItem(self)


class LivePipeItem(PipeItem):

    def __init__(self):
        super(LivePipeItem, self).__init__()
        self.setZValue(Z_VAL_NODE_WIDGET + 1)
        self.shiftSelected = False

    def paint(self, painter, option, widget=None):
        """
        Draws the connection line.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        _color = QtGui.QColor(*EnumPipeStyleProperty.ACTIVE_COLOR.value)
        _pen_style = PIPE_STYLES.get(EnumPipeStyleProperty.DRAW_TYPE_DASHED.value)
        _pen_width = EnumPipeStyleProperty.WIDTH.value + 0.35

        _pen = QtGui.QPen(_color, _pen_width)
        _pen.setStyle(_pen_style)
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)

        painter.save()
        painter.setPen(_pen)
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        painter.drawPath(self.path())

        _cen_x = self.path().pointAtPercent(0.5).x()
        _cen_y = self.path().pointAtPercent(0.5).y()
        _loc_pt = self.path().pointAtPercent(0.9)
        _tgt_pt = self.path().pointAtPercent(1.0)
        _start_pt = self.path().pointAtPercent(0.0)

        _dist = math.hypot(_tgt_pt.x() - _cen_x, _tgt_pt.y() - _cen_y)
        if _dist < 0.05:
            painter.restore()
            return

        # draw start circle
        _size = 5.0
        _rect = QtCore.QRectF(_start_pt.x() - (_size / 2),
                              _start_pt.y() - (_size / 2),
                              _size, _size)
        painter.setBrush(_color)
        painter.drawEllipse(_rect)

        # draw middle circle
        _size = 10.0
        if _dist < 50.0:
            _size *= (_dist / 50.0)
        _rect = QtCore.QRectF(_cen_x - (_size / 2), _cen_y - (_size / 2), _size, _size)
        painter.setBrush(_color)
        painter.setPen(QtGui.QPen(_color.darker(130), _pen_width))
        painter.drawEllipse(_rect)

        # draw arrow
        _color.setAlpha(255)
        painter.setBrush(_color.darker(200))

        _pen_width = 0.6
        if _dist < 1.0:
            _pen_width *= 1.0 + _dist
        painter.setPen(QtGui.QPen(_color, _pen_width))

        _transform = QtGui.QTransform()
        _transform.translate(_tgt_pt.x(), _tgt_pt.y())

        _radians = math.atan2(_tgt_pt.y() - _loc_pt.y(),
                              _tgt_pt.x() - _loc_pt.x())
        _degrees = math.degrees(_radians) + 90
        _transform.rotate(_degrees)

        _scale = 1.0
        if _dist < 20.0:
            _scale = _dist / 20.0
        _transform.scale(_scale, _scale)
        painter.drawPolygon(_transform.map(self._arrow))
        painter.restore()
