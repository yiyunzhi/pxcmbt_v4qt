# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_general.py
# ------------------------------------------------------------------------------
#
# File          : _test_general.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from sys import maxsize
from functools import wraps
import math
import numpy as np
from application.module.dstar_lite_pathplanner import OccupancyGridMap, DStarLite


def time_logger(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        _t = time.time()
        _res = func(*args, **kwargs)
        print('%s time:%2.4f ms' % (func.__name__, (time.time() - _t) * 1000))
        return _res

    return _wrapper


import time
from application.module.dstar_lite_pathplanner.utils import heuristic, Vertex, Vertices


class PointLike:
    def __init__(self, r, c):
        self.x = c
        self.y = r


def get_direction_change(angle1, angle2):
    _change = abs(angle2 - angle1)
    return 360 - _change if _change > 180 else _change


def get_theta_angle(pt1, pt2):
    _y = -(pt2.y - pt1.y)
    _x = pt2.x - pt1.x
    _rad = math.atan2(_y, _x)
    if _rad < 0:
        _rad = 2 * math.pi + _rad
    return 180 * _rad / math.pi


# todo: startpoint, startDir, endpoint, endDir required
def cost_modifier(u, v, grid_map):
    """
    u is start from goal point
    u,v is not occupied point in grid_map
    u: from
    v: to
    grid_map: map
    """
    _ds = 1 if v == goal_pos else heuristic(goal_pos, v)
    _de = 1 if v == start_pos else heuristic(start_pos, v)
    _angle_from_start = goal_angle if v == goal_pos else get_theta_angle(PointLike(*goal_pos),PointLike(*v),)
    #_angle_from_u = get_theta_angle(PointLike(*u), PointLike(*v))
    _angle_to_end = start_angle if v == start_pos else get_theta_angle(PointLike(*start_pos),PointLike(*v))

    _angle_change_from_start = get_direction_change(goal_angle,_angle_from_start)
    _angle_change_to_end = get_direction_change(start_angle, _angle_to_end)
    _cost = _angle_change_from_start / _ds + _angle_change_to_end / _de
    #print('----->angleChangeFromStart:%s;angleChangeToEnd:%s;u->v:%s->%s;cost:%s' % (_angle_change_from_start, _angle_change_to_end, u,v, _cost))
    return _cost


start_pos = (1, 1)
start_angle = 0
goal_angle = 90
goal_pos = (99, 99)


def main(size):
    _s = time.time()
    x_dim = 100
    y_dim = 100

    dstar = DStarLite(x_dim, y_dim, s_start=start_pos, s_goal=goal_pos)
    #dstar.costModifier = cost_modifier
    _t_init = time.time() - _s
    # dstar.sensedMap.set_obstacle((1, 0))
    # dstar.sensedMap.set_obstacle((1, 1))
    # dstar.sensedMap.set_obstacle((1, 2))
    # dstar.sensedMap.set_obstacle((1, 3))
    # dstar.sensedMap.set_obstacle((2, 3))
    # dstar.sensedMap.set_obstacle((3, 3))
    # dstar.sensedMap.set_obstacle((4, 3))
    #dstar.sensedMap.set_obstacle((10, 12))

    # dstar.sensedMap.set_obstacle((1, 2))
    # dstar.sensedMap.set_obstacle((7, 7))
    # dstar.sensedMap.set_obstacle((7, 8))
    # dstar.sensedMap.set_obstacle((7, 9))
    # dstar.sensedMap.set_obstacle((7, 10))
    # dstar.sensedMap.set_obstacle((11, 2))
    # dstar.sensedMap.set_obstacle((12, 2))
    path, g, rhs = dstar.move_and_replan(position=start_pos)

    print('init cost time(ms):', _t_init * 1000)
    print('sum cost time(ms):', (time.time() - _s) * 1000)
    print(len(path))
    dstar.sensedMap.render(path)


if __name__ == '__main__':
    # while True:
    #     _inp = input()
    #     main(int(_inp))
    import cProfile
    cProfile.run('main(20)')
    #main(20)
