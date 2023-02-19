# -*- coding: utf-8 -*-
import sys

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       :
# Sourcefile(s) : _test_algo_dstar_qtgraph.py
# ------------------------------------------------------------------------------
#
# File          : _test_algo_dstar_qtgraph.py
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
import time

from application.module.pathplanner.bi_dir_astar import (GridMap,
                                                         BidirectionalAStar,
                                                         render_path,
                                                         get_theta_angle,
                                                         get_direction_change,
                                                         PointLike)
from core.gui.qtimp import QtGui, QtCore, QtWidgets

GRID = 10
ZOOM_MIN = 0.1
ZOOM_MAX = 4


class LiveWire(QtWidgets.QGraphicsPathItem):
    def __init__(self, parent):
        super().__init__(parent)
        self._sourcePos = QtCore.QPointF(0, 0)
        self._currentPos = QtCore.QPointF(0, 0)
        self.quadrantBase = None
        self.pathFindMap = GridMap(0, 0)
        self.pathFindMap.debug = True
        self.pathFinder = BidirectionalAStar((0, 0), (0, 0), self.pathFindMap)
        self.pathFinderCellSize = 50

    def paint(self, painter, option, widget=None) -> None:
        _pen = QtGui.QPen(QtGui.QColor('red'), 2)
        painter.save()
        painter.setPen(_pen)
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        painter.drawPath(self.path())
        painter.restore()

    def draw_path(self, start_pos, cursor_pos=None):
        _pos1 = start_pos
        if cursor_pos:
            _pos2 = cursor_pos
            self._currentPos = _pos2
        else:
            return
        _line = QtCore.QLineF(_pos1, _pos2)
        _path = QtGui.QPainterPath()
        _path.moveTo(_line.x1(), _line.y1())

        _path.lineTo(_pos2)
        self.setPath(_path)

    def reset_path(self):
        _path = QtGui.QPainterPath(QtCore.QPointF(0.0, 0.0))
        self.setPath(_path)

    def _mapToGlobal(self, pt):
        return self.scene().views()[0].mapFromScene(pt)

    def _determine_grid_count(self, w, h):
        return round(w / GRID), round(h / GRID)

    def obstacle_checker(self, pos):
        _ret = False
        _s_base, _u = self.quadrantBase
        if self.obstacles is not None:
            for x in self.obstacles:
                _pos = _s_base + QtCore.QPointF(pos[0] * _u[0], pos[1] * _u[1]) * GRID
                _ret = x.boundingRect().contains(_pos)
                if _ret:
                    break
        return _ret

    def f_value_fore_modifier(self, s, algo: BidirectionalAStar):
        if s == algo.sStart:
            return 0
        _parent_p = algo.parentFore[s]
        if _parent_p == algo.sStart:
            _previous_angle = self.start_angle
            _angle = get_theta_angle(PointLike(*_parent_p), PointLike(*s))
        else:
            _grand_parent_p = algo.parentFore[_parent_p]
            _previous_angle = get_theta_angle(PointLike(*_grand_parent_p), PointLike(*_parent_p))
            _angle = get_theta_angle(PointLike(*_parent_p), PointLike(*s))
        _d = algo.h2(s, (int((algo.sStart[0] + algo.sGoal[0]) / 2), int((algo.sStart[1] + algo.sGoal[1]) / 2)))
        _d2 = algo.h2(s, algo.sStart)
        _d3 = algo.h2(s, algo.sGoal)
        # return get_direction_change(_angle, _previous_angle) /90+_d/(algo.distance+_d2+_d3)
        return 1

    def f_value_back_modifier(self, s, algo: BidirectionalAStar):
        if s == algo.sGoal:
            return 0
        _parent_p = algo.parentBack[s]
        if _parent_p == algo.sGoal:
            _previous_angle = self.goal_angle
            _angle = get_theta_angle(PointLike(*_parent_p), PointLike(*s))
        else:
            _grand_parent_p = algo.parentBack[_parent_p]
            _previous_angle = get_theta_angle(PointLike(*_grand_parent_p), PointLike(*_parent_p))
            _angle = get_theta_angle(PointLike(*_parent_p), PointLike(*s))
        _d = algo.h2(s, (int((algo.sStart[0] + algo.sGoal[0]) / 2), int((algo.sStart[1] + algo.sGoal[1]) / 2)))
        _d2 = algo.h2(s, algo.sGoal)
        _d3 = algo.h2(s, algo.sStart)
        # return get_direction_change(_angle, _previous_angle) /90+_d/(algo.distance+_d2+_d3)
        return 1

    def cost_modifier(self, p_from, p_to, algo: BidirectionalAStar):
        """
        p_from: from
        p_to: to
        algo: instance of algorithm
        """
        if algo.distance <= GRID:
            return 0
        _ds = 1 if p_from == algo.sStart else algo.h2(algo.sStart, p_to)
        _de = 1 if p_to == algo.sGoal else algo.h2(algo.sGoal, p_to)
        _ds = 1 if _ds == 0 else _ds
        _de = 1 if _de == 0 else _de
        # _angle = get_theta_angle(PointLike(*p_from), PointLike(*p_to))
        if p_from == algo.sStart:
            _previous_angle = self.start_angle
            _dir = 'F'
        elif p_from == algo.sGoal:
            _previous_angle = self.goal_angle
            _dir = 'B'
        else:
            if p_from in algo.parentFore:
                _parent_p = algo.parentFore[p_from]
                _dir = 'F'
            else:
                _parent_p = algo.parentBack[p_from]
                _dir = 'B'
            _previous_angle = get_theta_angle(PointLike(*_parent_p), PointLike(*p_from))
        _move_angle = get_theta_angle(PointLike(*p_from), PointLike(*p_to))
        if _dir == 'F':
            _d = _ds
            _angle_change = get_direction_change(self.start_angle, _move_angle)
            _cost = self.START_CHANGE_ANGLE_COST[_angle_change] + _de
        else:
            _d = _de
            _angle_change = get_direction_change(self.goal_angle, _move_angle)
            _cost = self.END_CHANGE_ANGLE_COST[_angle_change] + _ds

        # print('DIR:{} MoveAngle:{}\tCost:{},\tFrom:{},To:{}'.format(_dir, _move_angle, _cost, p_from, p_to))
        return _cost

    start_angle = 0
    goal_angle = 180
    obstacles = None
    START_CHANGE_ANGLE_COST = {90.0: 10, 180.0: 20, 0.0: 1, 270.0: 10}
    END_CHANGE_ANGLE_COST = {90.0: 10, 180.0: 20, 0.0: 1, 270.0: 20}

    def update_wire(self, rect: QtCore.QRectF, obstacles: [QtGui.QPainterPath]):
        _t0 = time.time()
        if self.pathFinder is not None:
            self.pathFinder.stop = True
        _w = abs(rect.width())
        _h = abs(rect.height())
        if _w == 0 and _h == 0:
            self.path().clear()
        _grid_x_count, _grid_y_count = self._determine_grid_count(_w, _h)
        _grid_x_range, _grid_y_range = _grid_x_count + 1, _grid_y_count + 1
        _s_base = rect.topLeft()
        _e_base = rect.bottomRight()
        _diff = _e_base - _s_base
        if _diff.x() < 0 and _diff.y() < 0:
            _u = (-1, -1)
        elif _diff.x() < 0 < _diff.y():
            _u = (-1, 1)
        elif _diff.x() > 0 > _diff.y():
            _u = (1, -1)
        else:
            if _diff.x() == 0:
                if _diff.y() > 0:
                    _u = (1, 1)
                else:
                    _u = (1, -1)
            elif _diff.y() == 0:
                if _diff.x() > 0:
                    _u = (1, 1)
                else:
                    _u = (-1, 1)
            else:
                _u = (1, 1)
        self.obstacles = obstacles
        self.quadrantBase = (_s_base, _u)
        _s_start, _s_end = (0, 0), (round(abs(_diff.x()) / GRID), round(abs(_diff.y()) / GRID))
        self.pathFindMap = GridMap(_grid_x_range, _grid_y_range)
        self.pathFinder = BidirectionalAStar(_s_start, _s_end, self.pathFindMap)
        # self.pathFinder.costModifier = self.cost_modifier
        self.pathFinder.fValueForeModifier = self.f_value_fore_modifier
        self.pathFinder.fValueBackModifier = self.f_value_back_modifier
        self.pathFindMap.obstacleChecker = self.obstacle_checker

        _path, _visit_fore, _visit_back = self.pathFinder.search()
        _t1 = time.time()
        # print(_path)
        render_path(self.pathFindMap, _path, _visit_fore, _visit_back)
        print('----->time cost:', _t1 - _t0)
        if _path:
            _painter_path = QtGui.QPainterPath()
            for idx, x in enumerate(_path):
                _p = _s_base + QtCore.QPointF(x[0] * _u[0], x[1] * _u[1]) * GRID
                if idx == 0:
                    _painter_path.moveTo(_p)
                else:
                    _painter_path.lineTo(_p)
            self.setPath(_painter_path)


class TestScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)
        self._bgColor = (105, 105, 105)
        self._gridColor = (75, 75, 75)
        self.setBackgroundBrush(QtGui.QColor(*self._bgColor))

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

    def get_view(self):
        return self.views()[0] if self.views() else None

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)

        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
        painter.setBrush(self.backgroundBrush())

        _zoom = self.get_view().get_zoom()
        if _zoom > -0.5:
            _pen = QtGui.QPen(QtGui.QColor(*self._gridColor), 0.65)
            self._draw_grid(
                painter, rect, _pen, GRID
            )

        _color = QtGui.QColor(*self._bgColor).darker(150)
        if _zoom < -0.0:
            _color = _color.darker(100 - int(_zoom * 110))
        _pen = QtGui.QPen(_color, 0.65)
        self._draw_grid(
            painter, rect, _pen, GRID * 8
        )
        painter.restore()


class MyItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.green))
        self.setRect(QtCore.QRectF(0, 0, width, height))

    def get_connection_points(self, pos):
        return self.x(), self.y()


class TestView(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setScene(TestScene(self))
        self._lastSize = self.size()
        self._lastScenePos = QtCore.QPointF(0, 0)
        self._sceneRange = QtCore.QRectF(0, 0, self.size().width(), self.size().height())
        self._liveWire = LiveWire(None)
        self._liveWire.setVisible(False)
        self._liveRect = QtWidgets.QGraphicsRectItem(0, 0, 0, 0)
        self._liveRect.setVisible(False)
        self.scene().addItem(self._liveRect)
        self.scene().addItem(self._liveWire)
        self._obstacle1 = QtWidgets.QGraphicsRectItem(0, 0, 50, 100)
        self._obstacle2 = QtWidgets.QGraphicsRectItem(100, 60, 100, 50)
        self._obstacle1.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.red))
        self._obstacle2.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.gray))
        self.scene().addItem(self._obstacle1)
        self.scene().addItem(self._obstacle2)

    def resizeEvent(self, event):
        _w, _h = self.size().width(), self.size().height()
        if 0 in [_w, _h]:
            self.resize(self._lastSize)
        if 0 in [self._lastSize.width(), self._lastSize.height()]:
            return
        _delta = max(_w / self._lastSize.width(), _h / self._lastSize.height())
        self._set_view_zoom(_delta)
        self._lastSize = self.size()
        super().resizeEvent(event)

    def wheelEvent(self, event):
        try:
            _delta = event.delta()
        except AttributeError:
            # For PyQt5
            _delta = event.angleDelta().y()
            if _delta == 0:
                _delta = event.angleDelta().x()
        self._set_view_zoom(_delta, pos=event.position().toPoint())

    def align_point(self, x, y):
        return GRID * round(x / GRID), GRID * round(y / GRID)

    def snap_to_grid(self, point_like: [QtCore.QRectF, QtCore.QPointF]):
        if isinstance(point_like, QtCore.QPointF):
            _x, _y = self.align_point(point_like.x(), point_like.y())
            point_like.setX(_x)
            point_like.setY(_y)
        elif isinstance(point_like, QtCore.QRectF):
            point_like.setTopLeft(QtCore.QPointF(*self.align_point(point_like.left(), point_like.top())))
            _w, _h = self.align_point(point_like.width(), point_like.height())
            point_like.setWidth(_w)
            point_like.setWidth(_h)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        _pos = self.mapToScene(event.position().toPoint())
        _aligned_pos = QtCore.QPointF(*self.align_point(_pos.x(), _pos.y()))
        self._lastScenePos = _pos
        self._liveWire._sourcePos = _aligned_pos
        self._liveWire.draw_path(self._liveWire._sourcePos, self._liveWire._sourcePos)
        self._liveWire.setVisible(True)
        self._liveRect.setVisible(True)
        super(TestView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._liveWire.setVisible(False)
        self._liveRect.setVisible(False)
        super(TestView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        _pos = self.mapToScene(event.position().toPoint())
        _diff = _pos - self._lastScenePos
        _aligned_pos = QtCore.QPointF(*self.align_point(_pos.x(), _pos.y()))
        if abs(_diff.x()) >= GRID or abs(_diff.y()) >= GRID:
            _item_under_mouse = self.scene().itemAt(_aligned_pos, self.transform())
            if not _item_under_mouse or _item_under_mouse is self._liveWire or _item_under_mouse is self._liveRect:
                _path_target_pos = QtCore.QPoint(*self.align_point(_pos.x(), _pos.y()))
            else:
                if isinstance(_item_under_mouse, MyItem):
                    _pos = _item_under_mouse.get_connection_points(_pos)
                    _path_target_pos = QtCore.QPoint(*self.align_point(*_pos))
                else:
                    _path_target_pos = QtCore.QPoint(*self.align_point(_pos.x(), _pos.y()))
            _rect = QtCore.QRectF(self._liveWire._sourcePos, _path_target_pos)
            self._liveRect.setRect(_rect)
            _item_under_rect = self.scene().items(_rect, QtCore.Qt.ItemSelectionMode.IntersectsItemShape)
            _live_wire_obstacle_path = list()
            if _item_under_rect:
                for x in _item_under_rect:
                    if x in [self._liveRect, self._liveWire, _item_under_mouse]:
                        continue
                    _xbr = x.boundingRect().toRect()
                    _p = QtGui.QPainterPath()
                    _p.moveTo(_xbr.topLeft())
                    _p.addRect(_xbr)
                    _live_wire_obstacle_path.append(_p)
            self._liveWire.update_wire(_rect, _live_wire_obstacle_path)
            self._update_scene()
        super(TestView, self).mouseMoveEvent(event)

    def get_zoom(self):
        """
        Returns the viewer zoom level.

        Returns:
            float: zoom level.
        """
        _transform = self.transform()
        _cur_scale = (_transform.m11(), _transform.m22())
        return float('{:0.2f}'.format(_cur_scale[0] - 1.0))

    def set_zoom(self, value=0.0):
        """
        Set the viewer zoom level.

        Args:
            value (float): zoom level
        """
        if value == 0.0:
            self.reset_zoom()
            return
        _zoom = self.get_zoom()
        if _zoom < 0.0:
            if not (ZOOM_MIN <= _zoom <= ZOOM_MAX):
                return
        else:
            if not (ZOOM_MIN <= value <= ZOOM_MAX):
                return
        value = value - _zoom
        self._set_view_zoom(value, 0.0)

    def _set_view_zoom(self, value, sensitivity=None, pos=None):
        """
        Sets the zoom level.

        Args:
            value (float): zoom factor.
            sensitivity (float): zoom sensitivity.
            pos (QtCore.QPoint): mapped position.
        """
        if pos:
            pos = self.mapToScene(pos)
        if sensitivity is None:
            _scale = 1.001 ** value
            self.scale(_scale, _scale, pos)
            return

        if value == 0.0:
            return

        _scale = (0.9 + sensitivity) if value < 0.0 else (1.1 - sensitivity)
        _zoom = self.get_zoom()
        if ZOOM_MIN >= _zoom:
            if _scale == 0.9:
                return
        if ZOOM_MAX <= _zoom:
            if _scale == 1.1:
                return
        self.scale(_scale, _scale, pos)

    def scale(self, sx, sy, pos=None):
        _scale = [sx, sx]
        _center = pos or self._sceneRange.center()
        _w = self._sceneRange.width() / _scale[0]
        _h = self._sceneRange.height() / _scale[1]
        self._sceneRange = QtCore.QRectF(
            _center.x() - (_center.x() - self._sceneRange.left()) / _scale[0],
            _center.y() - (_center.y() - self._sceneRange.top()) / _scale[1],
            _w, _h
        )
        self._update_scene()

    def _update_scene(self):
        """
        Redraw the scene.
        """
        self.setSceneRect(self._sceneRange)
        self.fitInView(self._sceneRange, QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def reset_zoom(self, cent=None):
        """
        Reset the viewer zoom level.

        Args:
            cent (QtCore.QPoint): specified center.
        """
        self._sceneRange = QtCore.QRectF(0, 0,
                                         self.size().width(),
                                         self.size().height())
        if cent:
            self._sceneRange.translate(cent - self._sceneRange.center())
        self._update_scene()


app = QtWidgets.QApplication(sys.argv)
v = TestView(None)
v.resize(1000, 720)
v.show()
sys.exit(app.exec())
