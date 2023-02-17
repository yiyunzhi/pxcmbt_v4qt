# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_smart_manhattan_route.py
# ------------------------------------------------------------------------------
#
# File          : _test_smart_manhattan_route.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import bisect
import sys

from gui import QtCore
import core.gui.module.path_router.util as util

gridSizeRow = 20
gridSizeCol = 20


class StateSet:
    OPEN = 1
    CLOSE = 2

    def __init__(self):
        self.items = list()
        self.hash = dict()
        self.values = dict()

    def add(self, item_k: str, item_v: int):
        if item_k in self.hash:
            self.hash.pop(item_k)
        else:
            self.hash[item_k] = self.OPEN
        self.values[item_k] = item_v
        _sl = sorted(self.items, key=lambda x: self.values[x])
        _idx = bisect.bisect(_sl, item_k)
        self.items.insert(_idx, item_k)

    def pop(self):
        _pop = self.items.pop(0)
        if _pop:
            self.hash[_pop] = self.CLOSE
        return _pop

    def is_open(self, item_k):
        return self.hash[item_k] == self.OPEN if item_k in self.hash else True

    def is_close(self, item_k):
        return self.hash[item_k] == self.CLOSE if item_k in self.hash else False

    def is_empty(self):
        return len(self.items) == 0


import math

step = 10


def get_direction_angle(start, end, direction_count):
    _quadrant = 360 / direction_count
    _angle_theta = util.get_theta_angle(start, end)
    _normalized_angle = util.Angle.normalize(_angle_theta + _quadrant / 2)
    return _quadrant * math.floor(_normalized_angle / _quadrant)


_dirs = [
    util.DirectionInfo(cost=10, offset_x=10, offset_y=0),
    util.DirectionInfo(cost=10, offset_x=-10, offset_y=0),
    util.DirectionInfo(cost=10, offset_x=0, offset_y=10),
    util.DirectionInfo(cost=10, offset_x=0, offset_y=-10)
]
for x in _dirs:
    _pt1 = QtCore.QPointF(0, 0)
    _pt2 = QtCore.QPointF(x.offsetX, x.offsetY)
    x.angle = util.Angle.normalize(util.get_theta_angle(_pt1, _pt2))
_penalties = {0: 0, 45: step / 2, 90: step / 2}
_maxDirectionChange = 90


def find(start_pt, end_pt):
    _open_set = StateSet()
    _loop_max = 500
    _loop_remain = _loop_max
    _points = dict()
    _parents = dict()
    _costs = dict()

    _start_point = start_pt
    _end_point = end_pt
    _k = util.point_to_string(_start_point)
    _open_set.add(_k, util.get_cost(_start_point, [end_pt]))
    _points[_k] = _start_point
    _costs[_k] = 0

    # _start_points = list(filter(lambda x: obstacle_map.is_accessible(x), _start_points))
    # _end_points = list(filter(lambda x: obstacle_map.is_accessible(x), _end_points))
    # todo: _prev_route_dir_angle in argument expect
    _prev_route_dir_angle = None
    # undefined for first route
    _is_path_beginning = _prev_route_dir_angle is None
    # direction
    _num_dirs = len(_dirs)
    _end_pt_key = util.point_to_string(end_pt)
    # main route finding loop
    _same_start_end_points = _start_point == _end_point
    while not _open_set.is_empty() and _loop_remain > 0:
        # Get the closest item and mark it CLOSED
        _current_key = _open_set.pop()
        _current_point = _points.get(_current_key)
        _current_parent = _parents.get(_current_key)
        _current_cost = _costs.get(_current_key)
        _is_start_point = _current_point == _start_point
        _is_route_beginning = _current_parent is None
        _prev_dir_angle = 0
        if not _is_route_beginning:
            _prev_dir_angle = get_direction_angle(_current_parent, _current_point, _num_dirs)
        elif not _is_path_beginning:
            # a vertex on the route
            _prev_dir_angle = _prev_route_dir_angle
        elif not _is_start_point:
            # beginning of route on the path
            _prev_dir_angle = get_direction_angle(_start_point, _current_point, _num_dirs)
        # check if we reached any endpoint
        _skip_end_check = _is_route_beginning and _same_start_end_points
        if not _skip_end_check and _current_key == _end_pt_key:
            # options.previousDirectionAngle = _prev_route_dir_angle
            return ['FOUND']
        # Go over all possible directions and find neighbors
        for dir_ in _dirs:
            _dir_angle = dir_.angle
            _dir_change = util.get_direction_change(_prev_dir_angle, _dir_angle)

            # Don't use the point changed rapidly.
            if not (_is_path_beginning and _is_start_point) and _dir_change > _maxDirectionChange:
                continue
            if _dir_change==0:
                _neighbor_point = _current_point + QtCore.QPointF(10, 0)
            elif _dir_change==90:
                _neighbor_point = _current_point + QtCore.QPointF(0, 10)
            elif _dir_change==180:
                _neighbor_point = _current_point + QtCore.QPointF(-10, 0)
            else:

                _neighbor_point = _current_point + QtCore.QPointF(0, -10)
            _neighbor_key = util.point_to_string(_neighbor_point)
            #  Closed points were already evaluated.
            _is_obstacle = False
            if _open_set.is_close(_neighbor_key) and not _is_obstacle:
                continue
            # neighbor is an end point
            if _neighbor_key == _end_pt_key:
                _is_end_pt = _neighbor_point==_end_point
                if not _is_end_pt:
                    _end_dir_angle = get_direction_angle(_neighbor_point, _end_point, _num_dirs)
                    _end_dir_change = util.get_direction_change(_dir_angle, _end_dir_angle)
                    if _end_dir_change > _maxDirectionChange:
                        continue
            # The current direction is ok.
            _neighbor_cost = dir_.cost
            _neighbor_penalty = 0 if _is_start_point else _penalties[_dir_change]
            _cost_from_start = _current_cost + _neighbor_cost + _neighbor_penalty
            # Neighbor point has not been processed yet or the cost of
            # the path from start is lower than previously calculated.
            if not _open_set.is_open(_neighbor_key) or _cost_from_start < (_costs.get(_neighbor_key) or sys.maxsize):
                _points[_neighbor_key] = _neighbor_point
                _parents[_neighbor_key] = _current_point
                _costs[_neighbor_key] = _cost_from_start
                _open_set.add(_neighbor_key, _cost_from_start + util.get_cost(_neighbor_point, [_end_point]))

        _loop_remain -= 1


_result = find(QtCore.QPointF(10, 10), QtCore.QPointF(100, 100))
