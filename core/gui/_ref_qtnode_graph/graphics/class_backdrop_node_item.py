# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_backdrop_node_item.py
# ------------------------------------------------------------------------------
#
# File          : class_backdrop_node_item.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtGui, QtCore, QtWidgets

from ..core.define import Z_VAL_PIPE, EnumNodeStyleProperty
from .class_node_item_base import BaseNodeItem
from .class_pipe_item import PipeItem
from .class_port_item import PortItem


class BackdropSizer(QtWidgets.QGraphicsItem):
    """
    Sizer item for resizing a backdrop item.

    Args:
        parent (BackdropNodeItem): the parent node item.
        size (float): sizer size.
    """

    def __init__(self, parent=None, size=6.0):
        super(BackdropSizer, self).__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeFDiagCursor))
        self.setToolTip('double-click auto resize')
        self._size = size

    @property
    def size(self):
        return self._size

    def set_pos(self, x, y):
        x -= self._size
        y -= self._size
        self.setPos(x, y)

    def boundingRect(self):
        return QtCore.QRectF(0.5, 0.5, self._size, self._size)

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemPositionChange:
            _item = self.parentItem()
            _mx, _my = _item.minimum_size
            _x = _mx if value.x() < _mx else value.x()
            _y = _my if value.y() < _my else value.y()
            _value = QtCore.QPointF(_x, _y)
            _item.on_sizer_pos_changed(value)
            return value
        return super(BackdropSizer, self).itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        _item = self.parentItem()
        _item.on_sizer_double_clicked()
        super(BackdropSizer, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        self.__prev_xy = (self.pos().x(), self.pos().y())
        super(BackdropSizer, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        _current_xy = (self.pos().x(), self.pos().y())
        if _current_xy != self.__prev_xy:
            _item = self.parentItem()
            _item.on_sizer_pos_mouse_release()
        del self.__prev_xy
        super(BackdropSizer, self).mouseReleaseEvent(event)

    def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, widget:QtWidgets.QWidget=None):
        """
        Draws the backdrop sizer on the bottom right corner.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        _margin = 1.0
        _rect = self.boundingRect()
        _rect = QtCore.QRectF(_rect.left() + _margin,
                              _rect.top() + _margin,
                              _rect.width() - (_margin * 2),
                              _rect.height() - (_margin * 2))

        _item = self.parentItem()
        if _item and _item.selected:
            _color = QtGui.QColor(*EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value)
        else:
            _color = QtGui.QColor(*_item.color)
            _color = _color.darker(110)
        _path = QtGui.QPainterPath()
        _path.moveTo(_rect.topRight())
        _path.lineTo(_rect.bottomRight())
        _path.lineTo(_rect.bottomLeft())
        painter.setBrush(_color)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.fillPath(_path, painter.brush())
        painter.restore()


class BackdropNodeItem(BaseNodeItem):
    """
    Base backdrop item.

    Args:
        name (str): name displayed on the node.
        text (str): backdrop text.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='backdrop', text='', parent=None):
        super(BackdropNodeItem, self).__init__(name, parent)
        self.setZValue(Z_VAL_PIPE - 1)
        self._properties['backdropText'] = text
        self._minSize = 80, 80
        self._sizer = BackdropSizer(self, 26.0)
        self._sizer.set_pos(*self._minSize)
        self._nodes = [self]

    def _combined_rect(self, nodes):
        _group = self.scene().createItemGroup(nodes)
        _rect = _group.boundingRect()
        self.scene().destroyItemGroup(_group)
        return _rect

    def mouseDoubleClickEvent(self, event):
        _view = self.get_view()
        if _view:
            _view.sigNodeDoubleClicked.emit(self.id)
        super(BackdropNodeItem, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            _pos = event.scenePos()
            _rect = QtCore.QRectF(_pos.x() - 5, _pos.y() - 5, 10, 10)
            _item = self.scene().items(_rect)[0]

            if isinstance(_item, (PortItem, PipeItem)):
                self.setFlag(self.GraphicsItemFlag.ItemIsMovable, False)
                return
            if self.selected:
                return

            _view = self.get_view()
            [n.setSelected(False) for n in _view.get_selected_nodes()]

            self._nodes += self.get_nodes(False)
            [n.setSelected(True) for n in self._nodes]

    def mouseReleaseEvent(self, event):
        super(BackdropNodeItem, self).mouseReleaseEvent(event)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        [n.setSelected(True) for n in self._nodes]
        self._nodes = [self]

    def on_sizer_pos_changed(self, pos):
        self._width = pos.x() + self._sizer.size
        self._height = pos.y() + self._sizer.size

    def on_sizer_pos_mouse_release(self):
        _size = {
            'pos': self.xy_pos,
            'width': self._width,
            'height': self._height}
        self.get_view().sigBackdropNodeUpdated.emit(
            self.id, 'sizer_mouse_release', _size)

    def on_sizer_double_clicked(self):
        _size = self.calc_backdrop_size()
        self.get_view().sigBackdropNodeUpdated.emit(
            self.id, 'sizer_double_clicked', _size)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: QtWidgets.QWidget = None):
        """
        Draws the backdrop rect.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        _margin = 1.0
        _rect = self.boundingRect()
        _rect = QtCore.QRectF(_rect.left() + _margin,
                              _rect.top() + _margin,
                              _rect.width() - (_margin * 2),
                              _rect.height() - (_margin * 2))

        _radius = 2.6
        _color = (self.color[0], self.color[1], self.color[2], 50)
        painter.setBrush(QtGui.QColor(*_color))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(_rect, _radius, _radius)

        _top_rect = QtCore.QRectF(_rect.x(), _rect.y(), _rect.width(), 26.0)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(*self.color)))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(_top_rect, _radius, _radius)
        for pos in [_top_rect.left(), _top_rect.right() - 5.0]:
            painter.drawRect(
                QtCore.QRectF(pos, _top_rect.bottom() - 5.0, 5.0, 5.0))

        if self.backdrop_text:
            painter.setPen(QtGui.QColor(*self.text_color))
            _txt_rect = QtCore.QRectF(
                _top_rect.x() + 5.0, _top_rect.height() + 3.0,
                _rect.width() - 5.0, _rect.height())
            painter.setPen(QtGui.QColor(*self.text_color))
            painter.drawText(_txt_rect,
                             QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.TextFlag.TextWordWrap,
                             self.backdrop_text)

        if self.selected:
            _sel_color = [x for x in EnumNodeStyleProperty.SELECTED_COLOR.value]
            _sel_color[-1] = 15
            painter.setBrush(QtGui.QColor(*_sel_color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRoundedRect(_rect, _radius, _radius)

        _txt_rect = QtCore.QRectF(_top_rect.x(), _top_rect.y(),
                                  _rect.width(), _top_rect.height())
        painter.setPen(QtGui.QColor(*self.text_color))
        painter.drawText(_txt_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.name)

        _border = 0.8
        _border_color = self.color
        if self.selected and EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value:
            _border = 1.0
            _border_color = EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor(*_border_color), _border))
        painter.drawRoundedRect(_rect, _radius, _radius)

        painter.restore()

    def get_nodes(self, inc_intersects=False):
        _mode = {True: QtCore.Qt.ItemSelectionMode.IntersectsItemShape,
                 False: QtCore.Qt.ItemSelectionMode.ContainsItemShape}
        _nodes = []
        if self.scene():
            _polygon = self.mapToScene(self.boundingRect())
            _rect = _polygon.boundingRect()
            _items = self.scene().items(_rect, mode=_mode[inc_intersects])
            for item in _items:
                if item == self or item == self._sizer:
                    continue
                if isinstance(item, BaseNodeItem):
                    _nodes.append(item)
        return _nodes

    def calc_backdrop_size(self, nodes=None):
        nodes = nodes or self.get_nodes(True)
        _padding = 40
        _nodes_rect = self._combined_rect(nodes)
        return {
            'pos': [
                _nodes_rect.x() - _padding, _nodes_rect.y() - _padding
            ],
            'width': _nodes_rect.width() + (_padding * 2),
            'height': _nodes_rect.height() + (_padding * 2)
        }

    @property
    def minimum_size(self):
        return self._minSize

    @minimum_size.setter
    def minimum_size(self, size=(50, 50)):
        self._minSize = size

    @property
    def backdrop_text(self):
        return self._properties['backdropText']

    @backdrop_text.setter
    def backdrop_text(self, text):
        self._properties['backdropText'] = text
        self.update(self.boundingRect())

    @BaseNodeItem.width.setter
    def width(self, width=0.0):
        BaseNodeItem.width.fset(self, width)
        self._sizer.set_pos(self._width, self._height)

    @BaseNodeItem.height.setter
    def height(self, height=0.0):
        BaseNodeItem.height.fset(self, height)
        self._sizer.set_pos(self._width, self._height)
