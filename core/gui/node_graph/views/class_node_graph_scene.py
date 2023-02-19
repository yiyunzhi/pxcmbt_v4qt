# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_scene.py
# ------------------------------------------------------------------------------
#
# File          : class_scene.py
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
from ..core.define import EnumViewGridFeature, EnumViewPalette


class NodeGraphScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent=None, **kwargs):
        super(NodeGraphScene, self).__init__(parent)
        self._gridMode = kwargs.get('grid_mode', EnumViewGridFeature.GRID_DISPLAY_LINES.value)
        self._gridColor = kwargs.get('grid_color', EnumViewPalette.GRID_COLOR)
        self._bgColor = kwargs.get('background_color')
        self._gridSize = kwargs.get('grid_size', EnumViewGridFeature.GRID_SIZE)
        if self._bgColor:
            self.setBackgroundBrush(QtGui.QColor(self._bgColor))

    def __repr__(self):
        cls_name = str(self.__class__.__name__)
        return '<{}("{}") object at {}>'.format(
            cls_name, self.get_view(), hex(id(self)))

    # def _draw_text(self, painter, pen):
    #     font = QtGui.QFont()
    #     font.setPixelSize(48)
    #     painter.setFont(font)
    #     parent = self.viewer()
    #     pos = QtCore.QPoint(20, parent.height() - 20)
    #     painter.setPen(pen)
    #     painter.drawText(parent.mapToScene(pos), 'Not Editable')
    # ----------------------------------------------------------
    # private
    # ----------------------------------------------------------
    def _draw_grid(self, painter: QtGui.QPainter, rect: QtCore.QRectF, pen: QtGui.QPen, grid_size: int) -> None:
        """
        draws the grid lines in the scene.

        Args:
            painter (QtGui.QPainter): painter object.
            rect (QtCore.QRectF): rect object.
            pen (QtGui.QPen): pen object.
            grid_size (int): grid size.
        """
        _left = int(rect.left())
        _right = int(rect.right())
        _top = int(rect.top())
        _bottom = int(rect.bottom())

        _first_left = _left - (_left % grid_size)
        _first_top = _top - (_top % grid_size)

        _lines = []
        _lines.extend([
            QtCore.QLineF(x, _top, x, _bottom)
            for x in range(_first_left, _right, grid_size)
        ])
        _lines.extend([
            QtCore.QLineF(_left, y, _right, y)
            for y in range(_first_top, _bottom, grid_size)]
        )

        painter.setPen(pen)
        painter.drawLines(_lines)

    def _draw_dots(self, painter: QtGui.QPainter, rect: QtCore.QRectF, pen: QtGui.QPen, grid_size: int) -> None:
        """
        draws the grid dots in the scene.

        Args:
            painter (QtGui.QPainter): painter object.
            rect (QtCore.QRectF): rect object.
            pen (QtGui.QPen): pen object.
            grid_size (int): grid size.
        """
        _zoom = self.get_view().get_zoom()
        if _zoom < 0:
            _grid_size = int(abs(_zoom) / 0.3 + 1) * grid_size

        _left = int(rect.left())
        _right = int(rect.right())
        _top = int(rect.top())
        _bottom = int(rect.bottom())

        _first_left = _left - (_left % grid_size)
        _first_top = _top - (_top % grid_size)
        pen.setWidth(int(grid_size / 10))
        painter.setPen(pen)
        [painter.drawPoint(int(x), int(y)) for x in range(_first_left, _right, grid_size) for y in range(_first_top, _bottom, grid_size)]

    # ----------------------------------------------------------
    # override events
    # ----------------------------------------------------------
    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super(NodeGraphScene, self).drawBackground(painter, rect)

        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
        painter.setBrush(self.backgroundBrush())

        if self._gridMode is EnumViewGridFeature.GRID_DISPLAY_DOTS.value:
            _pen = QtGui.QPen(QtGui.QColor(self.grid_color), 0.65)
            self._draw_dots(painter, rect, _pen, self._gridSize)

        elif self._gridMode is EnumViewGridFeature.GRID_DISPLAY_LINES.value:
            _zoom = self.get_view().get_zoom()
            if _zoom > -0.5:
                _pen = QtGui.QPen(QtGui.QColor(self.grid_color), 0.65)
                self._draw_grid(
                    painter, rect, _pen, self._gridSize
                )

            _color = QtGui.QColor(self._bgColor).darker(150)
            if _zoom < -0.0:
                _color = _color.darker(100 - int(_zoom * 110))
            _pen = QtGui.QPen(_color, 0.65)
            self._draw_grid(
                painter, rect, _pen, self._gridSize * 8
            )

        painter.restore()

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        _selected_nodes = self.get_view().get_selected_items()
        if self.get_view():
            self.get_view().sceneMousePressEvent(event)
        super(NodeGraphScene, self).mousePressEvent(event)
        _keep_selection = any([
            event.button() == QtCore.Qt.MouseButton.MiddleButton,
            event.button() == QtCore.Qt.MouseButton.RightButton,
            event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier
        ])
        if _keep_selection:
            for node in _selected_nodes:
                node.setSelected(True)

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        if self.get_view():
            self.get_view().sceneMouseMoveEvent(event)
        super(NodeGraphScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        if self.get_view():
            self.get_view().sceneMouseReleaseEvent(event)
        super(NodeGraphScene, self).mouseReleaseEvent(event)

    def get_view(self) -> 'NodeGraphView':
        return self.views()[0] if self.views() else None

    @property
    def grid_mode(self):
        return self._gridMode

    @grid_mode.setter
    def grid_mode(self, mode: EnumViewGridFeature = None):
        if mode is None:
            mode = EnumViewGridFeature.GRID_DISPLAY_LINES.value
        self._gridMode = mode

    @property
    def grid_color(self):
        return self._gridColor

    @grid_color.setter
    def grid_color(self, color=(0, 0, 0)):
        self._gridColor = color

    @property
    def background_color(self):
        return self._bgColor

    @background_color.setter
    def background_color(self, color=(0, 0, 0)):
        self._bgColor = color
        self.setBackgroundBrush(QtGui.QColor(self._bgColor))
