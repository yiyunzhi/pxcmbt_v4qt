# -*- coding: utf-8 -*-
import copy
# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : util.py
# ------------------------------------------------------------------------------
#
# File          : util.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import sys, math
from gui import QtCore


class EnumDirection:
    TOP = 'top'
    RIGHT = 'right'
    BOTTOM = 'bottom'
    LEFT = 'left'


ALL_DIRECTION = [EnumDirection.TOP, EnumDirection.RIGHT, EnumDirection.BOTTOM, EnumDirection.LEFT]


class DirectionInfo:
    def __init__(self, **kwargs):
        self.cost = kwargs.get('cost')
        self.offsetX = kwargs.get('offset_x')
        self.offsetY = kwargs.get('offset_y')
        self.angle = kwargs.get('angle')
        self.gridOffsetX = kwargs.get('grid_offset_x')
        self.gridOffsetY = kwargs.get('grid_offset_y')


class Padding:
    def __init__(self, **kwargs):
        self.top = kwargs.get('top', 0)
        self.right = kwargs.get('right', 0)
        self.bottom = kwargs.get('bottom', 0)
        self.left = kwargs.get('left', 0)


class PointLike:
    def __init__(self, **kwargs):
        self.x = kwargs.get('x')
        self.y = kwargs.get('y')


class Grid:
    def __init__(self, **kwargs):
        self.source = kwargs.get('source')
        self.x = kwargs.get('x')
        self.y = kwargs.get('y')


class Router:
    def __init__(self):
        pass


class ResolvedOptions:
    # The size of step to find a route (the grid of the manhattan pathfinder).
    step: int
    # The number of route finding loops that cause the router to abort returns
    # fallback route instead.
    maxLoopCount: int
    # The number of decimal places to round floating point coordinates.
    precision: int
    # The maximum change of direction.
    maxDirectionChange: int
    # Should the router use perpendicular edgeView option? Does not connect
    # to the anchor of node but rather a point close-by that is orthogonal.
    perpendicular: bool
    # Should the source and/or target not be considered as obstacles?
    excludeTerminals: list
    # Should certain nodes not be considered as obstacles?
    excludeNodes: list
    # Possible starting directions from a node.
    startDirections: [EnumDirection]
    # Possible ending directions from a node.
    endDirections: [EnumDirection]
    # Specify the directions used above and what they mean
    directionMap: dict
    # Returns the cost of an orthogonal step.
    cost: int
    # Returns an array of directions to find next points on the route different
    # from start/end directions.
    directionInfo: [DirectionInfo]
    # A penalty received for direction change.
    penalties: dict
    padding: [Padding]
    # The padding applied on the element bounding boxes.
    paddingBox: QtCore.QRectF
    fallbackRouter: [Router]
    draggingRouter = None
    fallbackRoute = None
    previousDirectionAngle: [int, None]
    # Whether the calculation results are aligned with the grid
    snapToGrid: [int, None]


class ManhattanRouterOptions(ResolvedOptions):
    def __init__(self, **kwargs):
        self.step = kwargs.get('step', 10)
        self.maxLoopCount = kwargs.get('max_loop_count', 2000)
        self.precision = kwargs.get('precision', 1)
        self.maxDirectionChange = kwargs.get('max_direction_change', 90)
        self.perpendicular = kwargs.get('perpendicular', True)
        self.excludeNodes = kwargs.get('step', 10)
        self.startDirections = kwargs.get('start_directions', ALL_DIRECTION)
        self.endDirections = kwargs.get('end_directions', ALL_DIRECTION)
        self.directionMap = kwargs.get('direction_map', {'top': PointLike(x=0, y=-1),
                                                         'right': PointLike(x=1, y=0),
                                                         'bottom': PointLike(x=0, y=1),
                                                         'left': PointLike(x=-1, y=0)})
        self.fallbackRouter = kwargs.get('fall_back_router', None)
        self.snapToGrid = kwargs.get('snap_to_grid', True)
        self.previousDirectionAngle = kwargs.get('previous_direction_angle')
        self._direction_info=kwargs.get('direction_info',[
            DirectionInfo(cost=self.cost, offset_x=self.step, offset_y=0),
            DirectionInfo(cost=self.cost, offset_x=-self.step, offset_y=0),
            DirectionInfo(cost=self.cost, offset_x=0, offset_y=self.step),
            DirectionInfo(cost=self.cost, offset_x=0, offset_y=-self.step)
        ])

    @property
    def cost(self):
        return self.step

    @property
    def direction_info(self):
        return self._direction_info

    @property
    def penalties(self):
        return {0: 0, 45: self.step / 2, 90: self.step / 2}

    @property
    def paddingBox(self):
        return QtCore.QRectF(-self.step, -self.step, 2 * self.step, 2 * self.step)


def get_source_bbox(g_item: 'PipeView', options: ResolvedOptions):
    _bb = g_item.sourceItem.boundingBox()
    _pb = options.paddingBox
    if options and _pb:
        return _bb.getRect().marginsAdded(QtCore.QMarginsF(_pb.left(), _pb.top(), _pb.right(), _pb.bottom()))
    return _bb.getRect()


def get_target_bbox(g_item: 'PipeView', options: ResolvedOptions):
    _bb = g_item.targetItem.boundingBox()
    _pb = options.paddingBox
    if options and _pb:
        return _bb.getRect().marginsAdded(QtCore.QMarginsF(_pb.left(), _pb.top(), _pb.right(), _pb.bottom()))
    return _bb.getRect()


def get_source_endpoint(g_item: 'PipeView', options: ResolvedOptions):
    if g_item.sourceAnchor is not None:
        return g_item.sourceAnchor
    _bb = g_item.sourceItem.boundingBox()
    return _bb.getRect().center()


def get_target_endpoint(g_item: 'PipeView', options: ResolvedOptions):
    if g_item.targetAnchor is not None:
        return g_item.targetAnchor
    _bb = g_item.targetItem.boundingBox()
    return _bb.getRect().center()


class Angle:
    @staticmethod
    def rad2deg(rad):
        return ((180 * rad) / math.pi) % 360

    @staticmethod
    def deg2rad(deg, over_360=False):
        _d = deg if over_360 else deg % 360
        return (_d * math.pi) / 180

    @staticmethod
    def normalize(angle):
        return angle % 360 + (360 if angle < 0 else 0)


def get_direction_angle(start, end, direction_count, grid, options):
    _quadrant = 360 / direction_count
    _angle_theta = get_theta_angle(start,fix_angle_end(start, end, grid, options))
    _normalized_angle = Angle.normalize(_angle_theta + _quadrant / 2)
    return _quadrant * math.floor(_normalized_angle / _quadrant)


def fix_angle_end(start, end, grid, options):
    _step = options.step
    _diff_x = end.x() - start.x()
    _diff_y = end.y() - start.y()
    _grid_steps_x = _diff_x / grid.x
    _grid_steps_y = _diff_y / grid.y
    _distance_x = _grid_steps_x * _step
    _distance_y = _grid_steps_y * _step
    return QtCore.QPointF(start.x() + _distance_x, start.y() + _distance_y)


def get_direction_change(angle1, angle2):
    _change = abs(angle2 - angle1)
    return 360 - _change if _change > 180 else _change


def get_grid(step, source, target):
    return Grid(source=source, x=get_grid_dimension(target.x() - source.x(), step), y=get_grid_dimension(target.y() - source.y(), step))


def get_grid_offsets(grid, options):
    _step = options.step
    for x in options.direction_info:
        x.gridOffsetX = (x.offsetX / _step) * grid.x
        x.gridOffsetY = (x.offsetY / _step) * grid.y
    return options.direction_info


def get_grid_dimension(diff, step):
    if not diff:
        return step
    _abs = abs(diff)
    _count = round(_abs / step)
    if not _count:
        return _abs
    _diff = _count * step
    _remainder = _abs - _diff
    _correction = _remainder / _count
    return step + _correction


def snap_grid(point, grid):
    _src = grid.source
    _x = grid.x * round((point.x() - _src.x()) / grid.x) + _src.x()
    _y = grid.y * round((point.y() - _src.y()) / grid.y) + _src.y()
    return QtCore.QPointF(_x, _y)


def snap_to_grid(point, grid_size):
    _x = grid_size * round(point.x() / grid_size)
    _y = grid_size * round(point.y() / grid_size)
    point.setX(_x)
    point.setY(_y)


def point_round(point, precision):
    if isinstance(point, QtCore.QPointF):
        return QtCore.QPointF(round(point.x(), precision),round(point.x(), precision))
    else:
        return point


def align(point, grid, precision):
    return point_round(snap_grid(copy.copy(point), grid), precision)


def point_to_string(point):
    return '%s_%s' % (point.x(), point.y())


def normalize_point(point):
    return QtCore.QPointF(0 if point.x() == 0 else abs(point.x()) / point.x(), 0 if point.y() == 0 else abs(point.y()) / point.y())


def calc_manhattan_distance(p1, p2):
    return math.dist((p1.x(), p1.y()), (p2.x(), p2.y()))


def get_cost(from_, anchors: list):
    _ret = sys.maxsize
    for a in anchors:
        _dist = calc_manhattan_distance(from_, a)
        if _dist < _ret:
            _ret = _dist
    return _ret


def get_squared_distance(p1: QtCore.QPointF, p2: QtCore.QPointF):
    return math.pow(p1.x() - p2.x(), 2) + math.pow(p1.y() - p2.y(), 2)


def get_rect_points(anchor: QtCore.QPointF, bbox: QtCore.QRectF, direction_list, grid, options):
    """
    Find points around the bbox taking given directions into account
    lines are drawn from anchor in given directions, intersections recorded
    if anchor is outside bbox, only those directions that intersect get a rect point
    the anchor itself is returned as rect point (representing some directions)
    (since those directions are unobstructed by the bbox)
    """
    _precision = options.precision
    _dir_map = options.directionMap
    _center_vk = anchor - bbox.center()
    _res = list()
    if not bbox.contains(anchor):
        _res.append(align(anchor, grid, _precision))
    else:
        for k, v in _dir_map.items():
            if k in direction_list:
                # Create a line that is guaranteed to intersect the bbox if bbox
                # is in the direction even if anchor lies outside of bbox.
                _ending = QtCore.QPointF(anchor.x() + v.x * abs(_center_vk.x()) + bbox.width(),
                                         anchor.y() + v.y * abs(_center_vk.y()) + bbox.height()
                                         )
                _intersection_line = QtCore.QLineF(anchor, _ending)
                _intersections = list()
                _rect_lines = [QtCore.QLineF(bbox.topLeft(), bbox.topRight()),
                               QtCore.QLineF(bbox.topLeft(), bbox.bottomLeft()),
                               QtCore.QLineF(bbox.topRight(), bbox.bottomRight()),
                               QtCore.QLineF(bbox.bottomLeft(), bbox.bottomRight()),
                               ]
                for l in _rect_lines:
                    # todo: watch the intersection type
                    _t, _p = l.intersects(_intersection_line)
                    _intersections.append(_p)
                # Get the farther intersection, in case there are two
                #  (that happens if anchor lies next to bbox)
                _farthest_intersection_distance = None
                _farthest_intersection = None
                for i in _intersections:
                    _dist = get_squared_distance(anchor, i)
                    if _farthest_intersection_distance is None or _dist > _farthest_intersection_distance:
                        _farthest_intersection_distance = _dist
                        _farthest_intersection = i
                # If an intersection was found in this direction, it is our rectPoint
                if _farthest_intersection:
                    _target = align(_farthest_intersection, grid, _precision)
                    # If the rectPoint lies inside the bbox, offset it by one more step
                    if bbox.contains(_target):
                        _target = align(_target + (v.x * grid.x, v.y * grid.y), grid, _precision)
                    _res.append(_target)
    return _res


def reconstruct_route(parents: dict, points: dict, tail_point: QtCore.QPointF, from_: QtCore.QPointF, to_: QtCore.QPointF):
    """
    reconstructs a route by concatenating points with their parents
    """
    _route = []
    _prev_diff = normalize_point(tail_point - to_)
    # tailPoint is assumed to be aligned already
    _current_k = point_to_string(tail_point)
    _parent = parents[_current_k]
    _point = None
    while _parent:
        # point is assumed to be aligned already
        _point = points[_current_k]
        _diff = normalize_point(_parent - _point)
        if _diff != _prev_diff:
            _route.insert(0, _point)
            _prev_diff = _diff
        # parent is assumed to be aligned already
        _current_k = point_to_string(_parent)
        _parent = parents[_current_k]
    # leadPoint is assumed to be aligned already
    _lead_point = points[_current_k]
    _from_diff = normalize_point(from_ - _lead_point)
    if _from_diff != _prev_diff:
        _route.insert(0, _lead_point)
    return _route


def get_theta_angle(pt1, pt2):
    _y = -(pt2.y() - pt1.y())
    _x = pt2.x() - pt1.x()
    _rad = math.atan2(_y, _x)
    if _rad < 0:
        _rad = 2 * math.pi + _rad
    return 180 * _rad / math.pi


def resolve_options(options: ResolvedOptions):
    for x in options.direction_info:
        _pt1 = QtCore.QPointF(0, 0)
        _pt2 = QtCore.QPointF(x.offsetX, x.offsetY)
        x.angle = Angle.normalize(get_theta_angle(_pt1, _pt2))
    return options
