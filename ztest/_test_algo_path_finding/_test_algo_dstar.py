# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_algo_dstar.py
# ------------------------------------------------------------------------------
#
# File          : _test_algo_dstar.py
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
from sys import maxsize


class State(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.state = "."
        self.t = "new"
        self.h = 0
        self.k = 0

    def cost(self, state):
        if self.state == "#" or state.state == "#":
            return maxsize
        return math.sqrt(math.pow((self.x - state.x), 2) +
                         math.pow((self.y - state.y), 2))

    def cost1(self, state):
        # # is an obstacle,give back the maximal cost
        if self.state == "#" or state.state == "#":
            return maxsize
        _dx = abs(self.x - state.x)
        _dy = abs(self.y - state.y)
        return _dy + _dx

    def set_state(self, state):
        if state not in ["s", ".", "#", "e", "*"]:
            return
        self.state = state


class Map(object):

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.map = self.init_map()
        self.debug=False

    def init_map(self):
        map_list = []
        for i in range(self.row):
            tmp = []
            for j in range(self.col):
                tmp.append(State(i, j))
            map_list.append(tmp)
        return map_list

    def print_map(self):
        if self.debug:
            for i in range(self.row):
                tmp = ""
                for j in range(self.col):
                    tmp += self.map[i][j].state + " "
                print(tmp)

    def get_neighbors(self, state):
        state_list = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                # if allow the diagonal then replace this condition with if i==0 and j==0
                if i == j or (i + j) == 0:
                    continue
                if state.x + i < 0 or state.x + i >= self.row:
                    continue
                if state.y + j < 0 or state.y + j >= self.col:
                    continue
                state_list.append(self.map[state.x + i][state.y + j])

        return state_list

    def set_obstacle(self, point_list):
        for x, y in point_list:
            if x < 0 or x >= self.row or y < 0 or y >= self.col:
                continue
            self.map[x][y].set_state("#")


from functools import wraps


def time_logger(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        _t = time.time()
        _res = func(*args, **kwargs)
        print('%s time:%2.4f ms' % (func.__name__, (time.time() - _t)*1000))
        return _res

    return _wrapper


class Dstar(object):

    def __init__(self, maps):
        self.map = maps
        self.open_list = set()

    @time_logger
    def process_state(self):
        x = self.min_state()
        if x is None:
            return -1
        k_old = self.get_kmin()
        self.remove(x)
        if k_old < x.h:
            for y in self.map.get_neighbors(x):
                if y.h <= k_old and x.h > y.h + x.cost(y):
                    x.parent = y
                    x.h = y.h + x.cost(y)
        elif k_old == x.h:
            for y in self.map.get_neighbors(x):
                if y.t == "new" or y.parent == x and y.h != x.h + x.cost(y) \
                        or y.parent != x and y.h > x.h + x.cost(y):
                    y.parent = x
                    self.insert(y, x.h + x.cost(y))
        else:
            for y in self.map.get_neighbors(x):
                if y.t == "new" or y.parent == x and y.h != x.h + x.cost(y):
                    y.parent = x
                    self.insert(y, x.h + x.cost(y))
                else:
                    if y.parent != x and y.h > x.h + x.cost(y):
                        self.insert(y, x.h)
                    else:
                        if y.parent != x and x.h > y.h + x.cost(y) \
                                and y.t == "close" and y.h > k_old:
                            self.insert(y, y.h)
        return self.get_kmin()

    def min_state(self):
        if not self.open_list:
            return None
        min_state = min(self.open_list, key=lambda x: x.k)
        return min_state

    def get_kmin(self):
        if not self.open_list:
            return -1
        k_min = min([x.k for x in self.open_list])
        return k_min

    def insert(self, state, h_new):
        if state.t == "new":
            state.k = h_new
        elif state.t == "open":
            state.k = min(state.k, h_new)
        elif state.t == "close":
            state.k = min(state.h, h_new)
        state.h = h_new
        state.t = "open"
        self.open_list.add(state)

    def remove(self, state):
        if state.t == "open":
            state.t = "close"
        self.open_list.remove(state)

    def modify_cost(self, x):
        if x.t == "close":
            self.insert(x, x.parent.h + x.cost(x.parent))

    @time_logger
    def run(self, start, end):
        self.open_list.add(end)
        while True:
            self.process_state()
            if start.t == "close":
                break

        start.set_state("s")
        s = start
        while s != end:
            s.set_state("s")
            s = s.parent
        s.set_state("e")
        # self.map.print_map()
        tmp = start
        while tmp != end:
            tmp.set_state("*")
            self.map.print_map()
            if self.map.debug:
                print("")
            if tmp.parent.state == "#":
                self.modify(tmp)
                continue
            tmp = tmp.parent
        tmp.set_state("e")
    @time_logger
    def modify(self, state):
        self.modify_cost(state)
        while True:
            k_min = self.process_state()
            if k_min >= state.h:
                break


if __name__ == '__main__':
    import time

    _s = time.time()
    m = Map(100, 100)
    m.set_obstacle([(4, 3), (4, 4), (4, 5), (4, 6), (5, 3), (6, 3), (7, 3), (5, 7)])
    m.set_obstacle([(9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8)])
    start = m.map[1][2]
    end = m.map[5][4]
    print('ready cost:', time.time() - _s)
    dstar = Dstar(m)

    dstar.run(start, end)
    # m.print_map()
    print('sum cost:',time.time() - _s)
    print([(x.x, x.y) for x in dstar.open_list if x.state == '*'])
