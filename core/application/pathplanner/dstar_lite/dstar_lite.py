# -*- coding: utf-8 -*-
import time

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : dstar_lite.py
# ------------------------------------------------------------------------------
#
# File          : dstar_lite.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import numpy as np
from .utils import heuristic, Vertices
from .priority_queue import VertexPriorityQueue, Prioritizable
from .grid import OccupancyGridMap


class DStarLite:
    def __init__(self, map_x_dim: int, map_y_dim: int, s_start: (int, int), s_goal: (int, int), exploration_setting='4N'):
        """
        :param map_x_dim: OccupancyGridMap x dimension
        :param map_y_dim: OccupancyGridMap y dimension
        :param s_start: start position
        :param s_goal: end position
        :param exploration_setting: str, explor mode
        """
        self.newEdgesAndOldCosts: [Vertices, None] = None
        self.costModifier = None
        # algorithm start
        self.sStart = s_start
        self.sGoal = s_goal
        self.sLast = s_start
        self.kMin = 0  # accumulation
        self.gOld = 0  # accumulation
        self.U = VertexPriorityQueue()
        # right hand side
        # This value is equal to the cost to the parent of a node plus the cost to travel to that node
        self.rhs = np.ones((map_x_dim, map_y_dim)) * np.inf
        # self.g used save the history state
        self.g = self.rhs.copy()
        self.rhs[self.sGoal] = 0
        self.U.insert(self.sGoal, Prioritizable(heuristic(self.sStart, self.sGoal), 0))
        self.sensedMap = OccupancyGridMap(x_dim=map_x_dim,
                                          y_dim=map_y_dim,
                                          exploration_setting=exploration_setting)

    def calculate_key(self, s: (int, int)):
        """
        :param s: the vertex we want to calculate key
        :return: Priority class of the two keys
        """
        _k1 = min(self.g[s], self.rhs[s]) + heuristic(self.sStart, s) + self.kMin
        _k2 = min(self.g[s], self.rhs[s])
        return Prioritizable(_k1, _k2)

    def calc_cost(self, u: (int, int), v: (int, int)) -> float:
        """
        calculate the cost between nodes
        :param u: from vertex
        :param v: to vertex
        :return: euclidean distance to traverse. inf if obstacle in path
        """
        if not self.sensedMap.is_unoccupied(u) or not self.sensedMap.is_unoccupied(v):
            return float('inf')
        else:
            return heuristic(u, v) + 0 if self.costModifier is None else self.costModifier(u, v, self.sensedMap)

    def contain(self, u: (int, int)) -> (int, int):
        return u in self.U.verticesInHeap

    def update_vertex(self, u: (int, int)):
        _is_contained = self.contain(u)
        _g_rhs_equal = self.g[u] == self.rhs[u]
        if not _g_rhs_equal and _is_contained:
            self.U.update(u, self.calculate_key(u))
        elif not _g_rhs_equal and not _is_contained:
            self.U.insert(u, self.calculate_key(u))
        elif _g_rhs_equal and _is_contained:
            self.U.remove(u)

    def compute_shortest_path(self):
        _start_k = self.calculate_key(self.sStart)
        while self.U.top_key() < _start_k or self.rhs[self.sStart] > self.g[self.sStart]:
            _u = self.U.top()
            _k_old = self.U.top_key()
            _k_new = self.calculate_key(_u)
            #_predecessor = self.sensedMap.get_successor(vertex=_u,avoid_obstacles=True)
            _predecessor = self.sensedMap.get_successor(vertex=_u)
            if _k_old < _k_new:
                self.U.update(_u, _k_new)
            elif self.g[_u] > self.rhs[_u]:
                self.g[_u] = self.rhs[_u]
                self.U.remove(_u)
                for s in _predecessor:
                    if s != self.sGoal:
                        self.rhs[s] = min(self.rhs[s], self.calc_cost(s, _u) + self.g[_u])
                    self.update_vertex(s)
            else:
                self.gOld = self.g[_u]
                self.g[_u] = float('inf')
                _predecessor.append(_u)
                for s in _predecessor:
                    if self.rhs[s] == (self.calc_cost(s, _u) + self.gOld):
                        if s != self.sGoal:
                            _successor = self.sensedMap.get_successor(vertex=s)
                            self.rhs[s] = min([float('inf')]+[self.calc_cost(s, s_) + self.g[s_] for s_ in _successor])
                    self.update_vertex(s)

    def rescan(self) -> Vertices:
        _new_edges_and_old_costs = self.newEdgesAndOldCosts
        self.newEdgesAndOldCosts = None
        return _new_edges_and_old_costs

    def move_and_replan(self, position: (int, int)):
        _path = [position]
        self.sStart = position
        self.sLast = self.sStart
        self.compute_shortest_path()

        while self.sStart != self.sGoal:
            assert (self.rhs[self.sStart] != float('inf')), "There is no known path!"
            _successor = self.sensedMap.get_successor(self.sStart)
            _min_s = float('inf')
            _arg_min = None
            for s_ in _successor:
                _temp = self.calc_cost(self.sStart, s_) + self.g[s_]
                if _temp < _min_s:
                    _min_s = _temp
                    _arg_min = s_

            ### algorithm sometimes gets stuck here for some reason !!! FIX
            self.sStart = _arg_min
            _path.append(self.sStart)
            # scan graph for any changed costs
            _changed_edges_with_old_cost = self.rescan()
            # print("len path: {}".format(len(path)))
            # if any edge costs changed while searching
            if _changed_edges_with_old_cost:
                print('--->rescan')
                self.kMin += heuristic(self.sLast, self.sStart)
                self.sLast = self.sStart

                # for all directed edges (u,v) with changed edge costs
                _vertices = _changed_edges_with_old_cost.vertices
                for vertex in _vertices:
                    _v = vertex.pos
                    _succ_v = vertex.edges_and_c_old
                    for u, c_old in _succ_v.items():
                        _c_new = self.calc_cost(u, _v)
                        if c_old > _c_new:
                            if u != self.sGoal:
                                self.rhs[u] = min(self.rhs[u], self.calc_cost(u, _v) + self.g[_v])
                        elif self.rhs[u] == c_old + self.g[_v]:
                            if u != self.sGoal:
                                _min_s = float('inf')
                                _successor_u = self.sensedMap.get_successor(vertex=u)
                                for s_ in _successor_u:
                                    _temp = self.calc_cost(u, s_) + self.g[s_]
                                    if _min_s > _temp:
                                        _min_s = _temp
                                self.rhs[u] = _min_s
                            self.update_vertex(u)
            self.compute_shortest_path()
        print("path found!")
        return _path, self.g, self.rhs
