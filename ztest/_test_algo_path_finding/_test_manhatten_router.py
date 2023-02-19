# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_manhatten_router.py
# ------------------------------------------------------------------------------
#
# File          : _test_manhatten_router.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from bisect import bisect
from core.gui.qtimp import QtCore
import core.gui.module.path_router.util as util
from core.gui.module.path_router import ObstacleMap


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
        _idx = bisect(_sl, item_k)
        self.items.insert(_idx, item_k)

    def pop(self):
        _pop = self.items.pop(0)
        if _pop:
            self.hash[_pop] = self.CLOSE
        return _pop

    def is_open(self, item_k):
        return self.hash[item_k] == self.OPEN if item_k in self.hash else False

    def is_close(self, item_k):
        return self.hash[item_k] == self.CLOSE if item_k in self.hash else False

    def is_empty(self):
        return len(self.items) == 0


# https://github.com/antvis/X6/blob/master/packages/x6/src/registry/router/manhattan/router.ts
def find_route_use_manhattan(pipe, from_, to_, obstacle_map: ObstacleMap, options: util.ResolvedOptions):
    _precision = options.precision
    _start_dir = options.startDirections
    _end_dir = options.endDirections
    _src_end_pt = from_
    # _src_end_pt = None
    _tgt_end_pt = to_
    # _tgt_end_pt = None

    _from_is_rect = isinstance(from_, QtCore.QRectF)
    _to_is_rect = isinstance(to_, QtCore.QRectF)
    #
    # if _from_is_rect:
    #     _src_end_pt = util.point_round(util.get_source_endpoint(pipe, options), _precision)
    # else:
    #     _src_end_pt = util.point_round(from_, _precision)
    #
    # if _to_is_rect:
    #     _tgt_end_pt = util.point_round(util.get_target_endpoint(pipe, options), _precision)
    # else:
    #     _tgt_end_pt = util.point_round(to_, _precision)

    # Get grid for this route.
    # _grid = util.get_grid(options.step, _src_end_pt, _tgt_end_pt)
    _grid = util.get_grid(options.step, from_, to_)

    #  Get pathfinding points
    _start_point = _src_end_pt
    _end_point = _tgt_end_pt
    _start_points = list()
    _end_points = list()

    if _from_is_rect:
        _start_points = util.get_rect_points(_start_point, from_, _start_dir, _grid, options)
    else:
        _start_points.append(_start_point)

    if _to_is_rect:
        _end_points = util.get_rect_points(_end_point, to_, _end_dir, _grid, options)
    else:
        _end_points.append(_end_point)

    # take into account only accessible rect points (those not under obstacles)
    _start_points = list(filter(lambda x: obstacle_map.is_accessible(x), _start_points))
    _end_points = list(filter(lambda x: obstacle_map.is_accessible(x), _end_points))

    # There is an accessible route point on both sides.
    if _start_points and _end_points:
        _open_set = StateSet()
        _points = dict()
        _parents = dict()
        _costs = dict()

        for p in _start_points:
            # startPoint is assumed to be aligned already
            _start_point = p
            _k = util.point_to_string(_start_point)
            _open_set.add(_k, util.get_cost(_start_point, _end_points))
            _points[_k] = _start_point
            _costs[_k] = 0
        _prev_route_dir_angle = options.previousDirectionAngle
        # undefined for first route
        _is_path_beginning = _prev_route_dir_angle is None

        # direction
        _dir = None
        _dir_change = None
        _dirs = util.get_grid_offsets(_grid, options)
        _num_dirs = len(_dirs)
        _end_pt_keys = [util.point_to_string(x) for x in _end_points]

        # main route finding loop
        _same_start_end_points = _start_points == _end_points
        _loops_remaining = options.maxLoopCount
        while not _open_set.is_empty() and _loops_remaining > 0:
            # Get the closest item and mark it CLOSED
            _current_key = _open_set.pop()
            _current_point = _points.get(_current_key)
            _current_parent = _parents.get(_current_key)
            _current_cost = _costs.get(_current_key)
            _is_start_point = _current_point == _start_point
            _is_route_beginning = _current_parent is None

            _prev_dir_angle = 0
            if not _is_route_beginning:
                _prev_dir_angle = util.get_direction_angle(_current_parent, _current_point, _num_dirs, _grid, options)
            elif not _is_path_beginning:
                # a vertex on the route
                _prev_dir_angle = _prev_route_dir_angle
            elif not _is_start_point:
                # beginning of route on the path
                _prev_dir_angle = util.get_direction_angle(_start_point, _current_point, _num_dirs, _grid, options)

            # check if we reached any endpoint
            _skip_end_check = _is_route_beginning and _same_start_end_points
            if not _skip_end_check and _current_key in _end_pt_keys:
                options.previousDirectionAngle = _prev_route_dir_angle
                return util.reconstruct_route(_parents, _points, _current_point, _start_point, _end_point)

            # Go over all possible directions and find neighbors
            for i in range(_num_dirs):
                _dir = _dirs[i]
                _dir_t_angle = _dir.angle
                _dir_change = util.get_direction_change(_prev_dir_angle, _dir_t_angle)

                # Don't use the point changed rapidly.
                if not (_is_path_beginning and _is_start_point) and _dir_change > options.maxDirectionChange:
                    continue
                #

                _neighbor_point = util.align(_current_point+QtCore.QPointF(_dir.gridOffsetX or 0, _dir.gridOffsetY or 0),
                                             _grid, _precision)
                _neighbor_key = util.point_to_string(_neighbor_point)

                #  Closed points were already evaluated.
                if _open_set.is_close(_neighbor_key) or not obstacle_map.is_accessible(_neighbor_point):
                    continue

                # neighbor is an end point
                if _neighbor_key in _end_pt_keys:
                    _is_end_pt = _neighbor_point.equals(_end_point)
                    if not _is_end_pt:
                        _end_dir_angle = util.get_direction_angle(_neighbor_point, _end_point, _num_dirs, _grid, options)
                        _end_dir_change = util.get_direction_change(_dir_t_angle, _end_dir_angle)
                        if _end_dir_change > options.maxDirectionChange:
                            continue

                # The current direction is ok.
                _neighbor_cost = _dir.cost
                _neighbor_penalty = 0 if _is_start_point else options.penalties[_dir_change]
                _cost_from_start = _current_cost + _neighbor_cost + _neighbor_penalty
                # Neighbor point has not been processed yet or the cost of
                # the path from start is lower than previously calculated.
                if not _open_set.is_open(_neighbor_key) or _cost_from_start < _costs[_neighbor_key]:
                    _points[_neighbor_key] = _neighbor_point
                    _parents[_neighbor_key] = _current_point
                    _costs[_neighbor_key] = _cost_from_start
                    _open_set.add(_neighbor_key, _cost_from_start + util.get_cost(_neighbor_point, _end_points))
            _loops_remaining -= 1
        print('_loops_remaining:',_loops_remaining)
    if options.fallbackRoute:
        return options.fallbackRoute(_start_point, _end_point, options)
    return None


def snap(points, grid_size=10):
    if len(points) <= 1:
        return points
    for i in range(len(points) - 1):
        _first = points[i]
        _second = points[i + 1]
        if _first.x == _second.x:
            _x = grid_size * round(_first.x / grid_size)
            if _first.x != _x:
                _first.x = _x
                _second.x = _x
        elif _first.y == _second.y:
            _y = grid_size * round(_first.y / grid_size)
            if _first.y != _y:
                _first.y = _y
                _second.y = _y
    return points


_options = util.resolve_options(util.ManhattanRouterOptions())
_start_pt = QtCore.QPointF(2, 3)
_end_pt = QtCore.QPointF(19, 19)
_obstacle_map = ObstacleMap(_options)
print(find_route_use_manhattan(None, _start_pt, _end_pt, _obstacle_map, _options))
