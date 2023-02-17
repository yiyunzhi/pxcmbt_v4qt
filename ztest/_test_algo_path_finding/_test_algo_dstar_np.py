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


def time_logger(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        _t = time.time()
        _res = func(*args, **kwargs)
        print('%s time:%2.4f ms' % (func.__name__, (time.time() - _t) * 1000))
        return _res

    return _wrapper


MODE = '4N'
# START_DIR = 90
# END_DIR = 0
penalties = {0: 0, 90: 10, 180: 0, 270: 10}
s_penalties = {0: 0, 90: 10, 180: 0, 270: 10}
e_penalties = {0: 0, 90: 10, 180: 0, 270: 10}


# 搜索的起点是设定的终点，所以180 是向左，向上是90，向下是270
# todo 惩罚的算法需要改进-// 起点dirChange 惩罚和终点dirChange惩罚


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


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.parent = None
        self.state = "."
        self.t = "new"
        self.h = 0
        self.k = 0
        self.x = row
        self.y = col
        self.setup_coordinate()

    def __repr__(self):
        return 'Cell(%s,%s), coord= (%s,%s)' % (self.row, self.col, self.x,self.y)

    def setup_coordinate(self):
        self.x=self.col
        self.y=self.row

    def cost(self, cell: 'Cell'):
        # Euclidean distance
        if self.state == "#" or cell.state == "#":
            return maxsize
        _dir_change = get_theta_angle(self, cell)
        _s_dir_change = get_theta_angle(self, Cell(*_start_p))
        _e_dir_change = get_theta_angle(self, Cell(*_end_p))
        _penalties = penalties.get(int(_dir_change))
        _s_penalties = s_penalties.get(int(_s_dir_change))
        _e_penalties = e_penalties.get(int(_e_dir_change))
        if _s_penalties is None:
            # print('s dir changed at:%s->%s, degree=%s' % (self, cell, _s_dir_change))
            _s_penalties = 10
        if _e_penalties is None:
            # print('e dir changed at:%s->%s, degree=%s' % (self, cell, _e_dir_change))
            _e_penalties = 10

        print('dir changed at:%s->%s, degree=%s,penalties=%s' % (self, cell, _dir_change, _penalties))
        return math.dist((self.x,self.y), (cell.x,cell.y)) + _penalties + _s_penalties + _e_penalties

    def set_state(self, state):
        if state not in ["s", ".", "#", "e", "*"]:
            return
        self.state = state


class Map:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.cellArray = None
        self._init_cell()
        self.debug = False

    def _init_cell(self):
        _cell_list = [[Cell(row, col) for col in range(self.col)] for row in range(self.row)]
        self.cellArray = _cell_list

    def print_map(self):
        if self.debug:
            self.render()

    def get_neighbors(self, cell):
        _cell_list = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                # if allow the diagonal then replace this condition with if i==0 and j==0
                if i == j or (i + j) == 0:
                    continue
                if cell.row + i < 0 or cell.row + i >= self.row:
                    continue
                if cell.col + j < 0 or cell.col + j >= self.col:
                    continue
                _cell_list.append(self.cellArray[cell.row + i][cell.col + j])

        return _cell_list

    def set_obstacle(self, point_list):
        for row, col in point_list:
            if row < 0 or row >= self.row or col < 0 or col >= self.col:
                continue
            self.cellArray[row][col].set_state("#")

    def render(self):
        for i in range(self.row):
            _tmp = ""
            for j in range(self.col):
                if i > self.row - 1 or j > self.col - 1:
                    _tmp += '?' + ' '
                else:
                    _tmp += self.cellArray[i][j].state + " "
            print(_tmp)


class DStar(object):

    def __init__(self, maps):
        self.map = maps
        self.openList = set()

    def process_cell(self):
        _min_k_cell = self.min_k_cell()
        if _min_k_cell is None:
            return -1
        _k_old = _min_k_cell.k
        self.remove(_min_k_cell)
        if _k_old < _min_k_cell.h:
            for y in self.map.get_neighbors(_min_k_cell):
                if y.h <= _k_old and _min_k_cell.h > y.h + _min_k_cell.cost(y):
                    y.parent = _min_k_cell
                    _min_k_cell.h = y.h + _min_k_cell.cost(y)
        elif _k_old == _min_k_cell.h:
            for y in self.map.get_neighbors(_min_k_cell):
                if y.t == "new" or y.parent == _min_k_cell and y.h != _min_k_cell.h + _min_k_cell.cost(y) \
                        or y.parent != _min_k_cell and y.h > _min_k_cell.h + _min_k_cell.cost(y):
                    y.parent = _min_k_cell
                    self.insert(y, _min_k_cell.h + _min_k_cell.cost(y))
        else:
            for y in self.map.get_neighbors(_min_k_cell):
                if y.t == "new" or y.parent == _min_k_cell and y.h != _min_k_cell.h + _min_k_cell.cost(y):
                    y.parent = _min_k_cell
                    self.insert(y, _min_k_cell.h + _min_k_cell.cost(y))
                else:
                    if y.parent != _min_k_cell and y.h > _min_k_cell.h + _min_k_cell.cost(y):
                        self.insert(y, _min_k_cell.h)
                    else:
                        if y.parent != _min_k_cell and _min_k_cell.h > y.h + _min_k_cell.cost(y) \
                                and y.t == "close" and y.h > _k_old:
                            self.insert(y, y.h)
        return self.get_min_k()

    def min_k_cell(self):
        if not self.openList:
            return None
        _min_cell = min(self.openList, key=lambda x: x.k)
        return _min_cell

    def get_min_k(self):
        if not self.openList:
            return -1
        _k_min = min([x.k for x in self.openList])
        return _k_min

    def insert(self, cell, h_new):
        if cell.t == "new":
            cell.k = h_new
        elif cell.t == "open":
            cell.k = min(cell.k, h_new)
        elif cell.t == "close":
            cell.k = min(cell.h, h_new)
        cell.h = h_new
        cell.t = "open"
        self.openList.add(cell)

    def remove(self, cell):
        if cell.t == "open":
            cell.t = "close"
        self.openList.remove(cell)

    def modify_cost(self, cell):
        if cell.t == "close":
            self.insert(cell, cell.parent.h + cell.cost(cell.parent))

    def run(self, start_cell, end_cell):
        if self.map.debug:
            self.map.print_map()
        self.openList.add(end_cell)
        while True:
            self.process_cell()
            if start_cell.t == "close":
                break

        start_cell.set_state("s")
        _s = start_cell
        while _s != end_cell:
            _s.set_state("s")
            _s = _s.parent
        _s.set_state("e")
        self.map.print_map()
        _tmp = start_cell
        while _tmp != end_cell:
            _tmp.set_state("*")
            self.map.print_map()
            if self.map.debug:
                print("")
            if _tmp.parent.state == "#":
                self.modify(_tmp)
                continue
            _tmp = _tmp.parent
        _tmp.set_state("e")

    def modify(self, cell):
        self.modify_cost(cell)
        while True:
            _k_min = self.process_cell()
            if _k_min >= cell.h:
                break


import time

_start_p = (0, 0)
_end_p = (87, 92)


def main(size=50):
    _s = time.time()
    m = Map(size, size)
    m.debug = False
    # m.set_obstacle([(4, 3), (4, 4), (4, 5), (4, 6), (5, 3), (6, 3), (7, 3), (5, 7)])
    # m.set_obstacle([(9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8)])
    start = m.cellArray[_start_p[0]][_start_p[1]]
    end = m.cellArray[_end_p[0]][_end_p[1]]
    _init_time_usage = time.time() - _s
    dstar = DStar(m)
    dstar.run(start, end)
    # m.print_map()
    print('ready time usage:', _init_time_usage)
    print('run time usage:', time.time() - _s)
    m.render()


if __name__ == '__main__':

    while True:
        _inp = input()
        main(int(_inp))
