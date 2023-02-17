# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_algo_oth_r.py
# ------------------------------------------------------------------------------
#
# File          : _test_algo_oth_r.py
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
from gui import QtGui, QtCore, QtWidgets

GRID = 10
ZOOM_MIN = 0.1
ZOOM_MAX = 4


def align_point(x, y):
    return GRID * round(x / GRID), GRID * round(y / GRID)


def snap_to_grid(point_like: [QtCore.QRectF, QtCore.QPointF]):
    if isinstance(point_like, QtCore.QPointF):
        _x, _y = align_point(point_like.x(), point_like.y())
        point_like.setX(_x)
        point_like.setY(_y)
    elif isinstance(point_like, QtCore.QRectF):
        point_like.setTopLeft(QtCore.QPointF(*align_point(point_like.left(), point_like.top())))
        _w, _h = align_point(point_like.width(), point_like.height())
        point_like.setWidth(_w)
        point_like.setWidth(_h)


class OCRGrid:
    def __init__(self):
        self.spotMap = dict()
        self.row = 0
        self.col = 0

    def add(self, row, col, val):
        self.spotMap.update({(row, col): val})

    def get_neighbors(self, vertex):
        (_x, _y) = vertex
        _movements = self.get_movements_4n(x=_x, y=_y)
        return _movements

    @staticmethod
    def get_movements_4n(x: int, y: int) -> list:
        """
        get all possible 4-connectivity movements.
        :return: list of movements with cost [(dx, dy, movement_cost)]
        """
        return [(x + 1, y + 0),
                (x + 0, y + 1),
                (x - 1, y + 0),
                (x + 0, y - 1)]


import heapq


class AStar:
    def __init__(self, s_start, s_goal, gridmap, heuristic_type='manhattan', max_loop=500):
        self.maxLoop = max_loop
        self.sStart = s_start
        self.sGoal = s_goal
        self.heuristicType = heuristic_type
        self.gridMap = gridmap
        self.costWeightGetter = None
        self.distance = self.h(s_start, s_goal)
        self.open = []
        self.closed = []
        self.parent = dict()
        self.g = dict()
        self.stop = False

    def setup(self):
        self.g[self.sStart] = 0.0
        self.g[self.sGoal] = math.inf
        self.parent[self.sStart] = self.sStart
        heapq.heappush(self.open,
                       (self.f_value(self.sStart), self.sStart))

    def f_value(self, s):
        """
        forward searching: f = g + h. (g: Cost to come, h: heuristic value)
        :param s: current state
        :return: f
        """
        return self.g[s] + self.h(s, self.sGoal)

    def h(self, s, goal):
        """
        Calculate heuristic value.
        :param s: current node (state)
        :param goal: goal node (state)
        :return: heuristic value
        """
        if self.heuristicType == "manhattan":
            return abs(goal[0] - s[0]) + abs(goal[1] - s[1])
        else:
            return math.hypot(goal[0] - s[0], goal[1] - s[1])

    def cost(self, p_from, p_to):
        """
        Calculate Cost for this motion
        :param p_from: starting node
        :param p_to: end node
        :return:  Cost for this motion
        :note: Cost function could be more complicate!
        """
        if self.is_collision(p_from, p_to):
            return math.inf
        return self.h(p_from, p_to) * 1 if self.costWeightGetter is None else self.costWeightGetter(p_from, p_to, self)

    def is_collision(self, s_start, s_end):
        """
        check if the line segment (s_start, s_end) is collision.
        :param s_start: start node
        :param s_end: end node
        :return: True: is collision / False: not collision
        """
        if self.gridMap.spotMap.get(s_end) is None:
            return True
        if s_start[0] != s_end[0] and s_start[1] != s_end[1]:
            if s_end[0] - s_start[0] == s_start[1] - s_end[1]:
                _s1 = (min(s_start[0], s_end[0]), min(s_start[1], s_end[1]))
                _s2 = (max(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
            else:
                _s1 = (min(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
                _s2 = (max(s_start[0], s_end[0]), min(s_start[1], s_end[1]))
            if self.gridMap.spotMap.get(_s1) is None or self.gridMap.spotMap.get(_s2) is None:
                return True
        return False

    def extract_path(self, s_meet_set):
        """
        extract path from start and goal
        :param s_meet_set: set of parent
        :return: path
        """
        # extract path for forward part
        _path_fore = [self.sGoal]
        _s = self.sGoal
        while True:
            _s = s_meet_set[_s]
            _path_fore.append(_s)
            if _s == self.sStart:
                break
        return _path_fore

    def search(self):
        """
        A*
        :return: connected path, visited order of forward
        """
        self.setup()
        _loop_remain = self.maxLoop
        while self.open and not self.stop and _loop_remain:
            # solve forward-search
            _, _s = heapq.heappop(self.open)
            self.closed.append(_s)
            if _s == self.sGoal:
                break
            for s_n in self.gridMap.get_neighbors(_s):
                _new_cost = self.g[_s] + self.cost(_s, s_n)
                if s_n not in self.g:
                    self.g[s_n] = math.inf
                if _new_cost < self.g[s_n]:
                    self.g[s_n] = _new_cost
                    self.parent[s_n] = _s
                    heapq.heappush(self.open,
                                   (self.f_value(s_n), s_n))
            _loop_remain -= 1
        if _loop_remain == 0:
            return [], None
        return self.extract_path(self.parent), self.closed


class LiveWire(QtWidgets.QGraphicsPathItem):
    def __init__(self, parent):
        super().__init__(parent)
        self._sourcePos = QtCore.QPointF(0, 0)
        self._currentPos = QtCore.QPointF(0, 0)
        self.sourceNode = None
        self.targetNode = None

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

    def get_rect_ruler(self, rect: QtCore.QRectF, grid_rect: [QtCore.QRectF, None]):
        _v_ruler = []
        _h_ruler = []
        _l, _t, _r, _b = rect.getCoords()
        _cx, _cy = rect.center().x(), rect.center().y()
        if grid_rect is None or True:
            _gl, _gt, _gr, _gb = _l, _t, _r, _b
        else:
            _gl, _gt, _gr, _gb = grid_rect.getCoords()
            _gl = _l  # min(_gl, _l)
            _gt = min(_gt, _t)
            _gr = _gr  # min(_gr, _r)
            _gb = min(_gb, _b)
        if abs(rect.height()) > 0 or True:
            # W
            _v_ruler.append(QtCore.QLineF(QtCore.QPointF(*align_point(_l, _gt)), QtCore.QPointF(*align_point(_l, _gb))))
            # E
            _v_ruler.append(QtCore.QLineF(QtCore.QPointF(*align_point(_r, _gt)), QtCore.QPointF(*align_point(_r, _gb))))
        if abs(rect.width()) > 0 or True:
            # N
            _h_ruler.append(QtCore.QLineF(QtCore.QPointF(*align_point(_gl, _t)), QtCore.QPointF(*align_point(_gr, _t))))
            # S
            _h_ruler.append(QtCore.QLineF(QtCore.QPointF(*align_point(_gl, _b)), QtCore.QPointF(*align_point(_gr, _b))))
        if grid_rect is not None:
            _v_ruler.append(QtCore.QLineF(QtCore.QPointF(*align_point(_cx, _gt)), QtCore.QPointF(*align_point(_cx, _gb))))
            _h_ruler.append(QtCore.QLineF(QtCore.QPointF(*align_point(_gl, _cy)), QtCore.QPointF(*align_point(_gr, _cy))))
        return _v_ruler, _h_ruler

    def get_rule(self, grid_rect: QtCore.QRectF, items: [QtWidgets.QGraphicsItem]):
        _v_ruler = []
        _h_ruler = []
        # united the grid rect and source node
        _src_br=self.sourceNode.boundingRect()
        _src_rect=QtCore.QRectF(_src_br.topLeft()+self.sourceNode.pos(),QtCore.QSize(_src_br.width(),_src_br.height()))
        _used_grid_rect = grid_rect.united(_src_rect)
        _vr, _hr = self.get_rect_ruler(grid_rect.marginsAdded(QtCore.QMargins(-GRID, 0, 0, 0)), None)
        _v_ruler.extend(_vr)
        _h_ruler.extend(_hr)
        # get ruler of source node
        _s_src_rect=_src_rect.marginsAdded(QtCore.QMargins(*[GRID] * 4))
        _svr, _shr = self.get_rect_ruler(_s_src_rect, None)
        if _svr:
            if self.ANCHOR_PT_FACE == 'E':
                self.FACE_RULER = _svr.pop(1)
            elif self.ANCHOR_PT_FACE == 'W':
                self.FACE_RULER = _svr.pop(0)
        if _shr:
            if self.ANCHOR_PT_FACE == 'S':
                self.FACE_RULER = _shr.pop(1)
            elif self.ANCHOR_PT_FACE == 'N':
                self.FACE_RULER = _shr.pop(0)
        _v_ruler.extend(_svr)
        _h_ruler.extend(_shr)
        # get ruler of obstacles
        for x in items:
            _pos = x.pos()
            _br = x.boundingRect().marginsAdded(QtCore.QMargins(*[GRID] * 4))
            _rect = QtCore.QRectF(_pos+_br.topLeft(), QtCore.QSize(_br.width(), _br.height()))
            _vr, _hr = self.get_rect_ruler(_rect, grid_rect)
            _v_ruler.extend(_vr)
            _h_ruler.extend(_hr)
        return _v_ruler, _h_ruler, _used_grid_rect

    ANCHOR_PT_FACE = 'E'
    FACE_RULER = None
    ALL_ANCHOR_PT_FACE = ['N', 'S', 'E', 'W']

    def _pt_product(self, l):
        from itertools import product
        _res = list()
        _xs = list()
        _ys = list()
        for x in l:
            heapq.heappush(_xs, x.p1().x())
            heapq.heappush(_xs, x.p2().x())
            heapq.heappush(_ys, x.p1().y())
            heapq.heappush(_ys, x.p2().y())
        _xs = list(set(_xs))
        _ys = list(set(_ys))
        for x in list(set(product(_xs, _ys))):
            _res.append(QtCore.QPointF(*align_point(*x)))
        return _res

    def calc_cost_weight(self, p_from, p_to, algo: AStar):
        _l_cur = QtCore.QLineF(algo.gridMap.spotMap[p_from], algo.gridMap.spotMap[p_to])
        if p_from == algo.sStart:
            if self.ANCHOR_PT_FACE == 'E':
                _l_prev = QtCore.QLineF(algo.gridMap.spotMap[p_from] + QtCore.QPointF(-GRID, 0), algo.gridMap.spotMap[p_from])
        else:
            _l_prev = QtCore.QLineF(algo.gridMap.spotMap[algo.parent[p_from]], algo.gridMap.spotMap[p_from])
        _angle_change = _l_prev.angleTo(_l_cur)
        if _angle_change == 0:
            return 1
        else:
            return _angle_change

    def update_ocr_wire(self, rect: QtCore.QRectF, obstacles: [QtGui.QPainterPath]):
        # todo: if rect is a line like, width==0 or height==0???
        _1, _2, _r, _b = rect.getCoords()
        _t0 = time.time()
        self.scene().clear_rulers()
        _vr, _hr, _grid_rect = self.get_rule(rect, obstacles)
        _u_vr = list()
        _u_hr = list()
        for x in _vr:
            if x not in _u_vr and not x.isNull():
                _u_vr.append(x)
        for x in _hr:
            if x not in _u_hr and not x.isNull():
                _u_hr.append(x)
        self.scene().vPathGridRulers.extend(_u_vr)
        self.scene().hPathGridRulers.extend(_u_hr)
        # todo: for test purpose, always one GRID EAST orientated:
        _source_con_pt_next_path_pt = self._sourcePos + QtCore.QPointF(GRID, 0)
        _source_grid_pos = None
        _destination_grid_pos = None
        _face_pt_extend_ruler = QtCore.QLineF(self._sourcePos, QtCore.QPointF(max(self._sourcePos.x() + GRID, rect.right()), self._sourcePos.y()))
        self.scene().hPathGridRulers.append(_face_pt_extend_ruler)
        _pt_product = self._pt_product(self.scene().hPathGridRulers + self.scene().vPathGridRulers)

        _filtered_pt = list(filter(lambda x: _grid_rect.contains(x), _pt_product))
        self.scene().pathGridPoints = _filtered_pt
        _along_x_sorted = sorted(_filtered_pt, key=lambda x: x.x())
        _along_y_sorted = sorted(_filtered_pt, key=lambda x: x.y())
        _x_col = sorted(list(set([x.x() for x in _along_x_sorted])))
        _y_col = sorted(list(set([x.y() for x in _along_y_sorted])))
        _grid = OCRGrid()
        _obstacle_pt = []
        for p in _filtered_pt:
            _x, _y = _x_col.index(p.x()), _y_col.index(p.y())

            if any([o.contains(self.mapToItem(o,p)) for o in obstacles + [self.sourceNode]]):
                _grid.add(_x, _y, None)
            else:
                if p == _source_con_pt_next_path_pt:
                    _source_grid_pos = _x, _y
                if p == QtCore.QPointF(_r, _b):
                    _destination_grid_pos = (_x, _y)
                _grid.add(_x, _y, p)
        # print('-->start searching: src={},dst={},gridCnt:{},row:{},col:{}'.format(_source_grid_pos,
        #                                                                           _destination_grid_pos,
        #                                                                           len(_filtered_pt),
        #                                                                           len(_x_col),
        #                                                                           len(_y_col)))
        if _source_grid_pos is not None and _destination_grid_pos is not None:
            _algo = AStar(_source_grid_pos, _destination_grid_pos, _grid)
            _algo.costWeightGetter = self.calc_cost_weight
            _path, _closed = _algo.search()
            # print('---------->routed path:',_path,_algo.gridMap.spotMap)
            _painter_path = QtGui.QPainterPath()
            for idx, x in enumerate(_path):
                _p = _grid.spotMap.get(x)
                if idx == 0:
                    _painter_path.moveTo(_p)
                else:
                    _painter_path.lineTo(_p)
            self.setPath(_painter_path)
        _t1 = time.time()
        print('----->time cost:', _t1 - _t0)


class TestScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)
        self._bgColor = (105, 105, 105)
        self._gridColor = (75, 75, 75)
        self.vPathGridRulers = []
        self.hPathGridRulers = []
        self.pathGridPoints = list()
        self.setBackgroundBrush(QtGui.QColor(*self._bgColor))

    def clear_rulers(self):
        self.vPathGridRulers.clear()
        self.hPathGridRulers.clear()
        self.pathGridPoints.clear()

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

    def draw_path_grid_rulers(self, painter: QtGui.QPainter, pen: QtGui.QPen) -> None:
        _pen = QtGui.QPen(QtCore.Qt.GlobalColor.green)
        painter.setPen(_pen)
        painter.drawLines(self.vPathGridRulers)
        _pen.setColor(QtCore.Qt.GlobalColor.blue)
        painter.setPen(_pen)
        painter.drawLines(self.hPathGridRulers)
        _pen.setColor(QtCore.Qt.GlobalColor.red)
        painter.setPen(_pen)
        painter.drawPoints(QtGui.QPolygonF(self.pathGridPoints))
        painter.setPen(pen)

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
        self.draw_path_grid_rulers(painter, _pen)
        painter.restore()


class ConnectableItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.green))
        self.setRect(QtCore.QRectF(0, 0, width, height))

    def get_connection_points(self, pos):
        return self.x(), self.y()


class MyRectItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h, parent=None):
        QtWidgets.QGraphicsRectItem.__init__(self, x, y, w, h, parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable | self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value):
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged:
            pass
        return super().itemChange(change, value)


class TestView(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setScene(TestScene(self))
        self._lastSize = self.size()
        self._lastScenePos = QtCore.QPointF(0, 0)
        self._sceneRange = QtCore.QRectF(0, 0, self.size().width(), self.size().height())
        self._liveWire = LiveWire(None)
        self._liveWire.setVisible(False)
        # self._liveRect = QtWidgets.QGraphicsRectItem(0, 0, 0, 0)
        # self._liveRect.setVisible(False)
        # self.scene().addItem(self._liveRect)
        self.scene().addItem(self._liveWire)
        self._obstacle1 = QtWidgets.QGraphicsRectItem(0, 0, 50, 100)
        self._obstacle2 = MyRectItem(100, 60, 100, 50)
        self._obstacle1.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.red))
        self._obstacle2.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.gray))
        self.scene().addItem(self._obstacle1)
        self.scene().addItem(self._obstacle2)
        for i in range(10):
            _item=MyRectItem(120, 60+i*10, 100, 50)
            self.scene().addItem(_item)

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

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        _pos = self.mapToScene(event.position().toPoint())
        _item_under_mouse = self.scene().itemAt(_pos, self.transform())
        if _item_under_mouse:
            _aligned_pos = QtCore.QPointF(*align_point(_pos.x(), _pos.y()))
            self._lastScenePos = _pos
            self._liveWire.sourceNode = _item_under_mouse
            self._liveWire._sourcePos = _aligned_pos
            self._liveWire.draw_path(self._liveWire._sourcePos, self._liveWire._sourcePos)
            self._liveWire.setVisible(True)
            # self._liveRect.setVisible(True)
        super(TestView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._liveWire.setVisible(False)
        self._liveWire.sourceNode = None
        self.scene().clear_rulers()
        self._update_scene()
        # self._liveRect.setVisible(False)
        super(TestView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        _pos = self.mapToScene(event.position().toPoint())
        if self._liveWire.sourceNode is not None:
            _diff = _pos - self._lastScenePos
            _aligned_pos = QtCore.QPointF(*align_point(_pos.x(), _pos.y()))
            if abs(_diff.x()) >= GRID or abs(_diff.y()) >= GRID:
                _path_target_pos = QtCore.QPoint(*align_point(_pos.x(), _pos.y()))
                _rect = QtCore.QRectF(self._liveWire._sourcePos, _path_target_pos)
                _item_under_rect = self.scene().items(_rect, QtCore.Qt.ItemSelectionMode.IntersectsItemBoundingRect)
                if _rect.width() == 0 or _rect.height() == 0:
                    _path = QtGui.QPainterPath()
                    _path.moveTo(self._liveWire._sourcePos)
                    _path.lineTo(_path_target_pos)
                    _path_intersected_items = self.scene().items(_path, QtCore.Qt.ItemSelectionMode.IntersectsItemBoundingRect)
                    _item_under_rect.extend(_path_intersected_items)
                _live_wire_obstacle_path = list()
                for x in _item_under_rect:
                    if x in [self._liveWire, self._liveWire.sourceNode]:
                        continue
                    if isinstance(x, QtWidgets.QGraphicsLineItem):
                        continue

                    _live_wire_obstacle_path.append(x)
                self._liveWire.update_ocr_wire(_rect, _live_wire_obstacle_path)
                # for presentation purpose
                if self._obstacle2 in _item_under_rect:
                    self._obstacle2.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.cyan))
                else:
                    self._obstacle2.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.gray))
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


import sys

app = QtWidgets.QApplication(sys.argv)
v = TestView(None)
v.resize(1000, 720)
v.show()
sys.exit(app.exec())
