# -*- coding: utf-8 -*-

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
import math


class PointLike:
    def __init__(self, row, col):
        self.x = row
        self.y = col


def render_path(grid, path, visited_fore=None, visited_back=None):
    visited_fore = [] if visited_fore is None else visited_fore
    visited_back = [] if visited_back is None else visited_back
    for i in range(grid.yRange):
        _s = ''
        for j in range(grid.xRange):
            _pos = (j, i)

            if _pos in visited_fore:
                if _pos in path:
                    _s += 'F' + ' '
                else:
                    _s += '>' + ' '
            elif _pos in visited_back:
                if _pos in path:
                    _s += 'B' + ' '
                else:
                    _s += '<' + ' '
            elif _pos in grid.obstacleMap:
                _s += '#' + ' '
            else:
                if _pos in path:
                    _s += '+' + ' '
                else:
                    _s += '.' + ' '
        print(_s)


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
