# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : bi_dir_astar.py
# ------------------------------------------------------------------------------
#
# File          : bi_dir_astar.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import logging
import heapq, math
from .util import get_theta_angle, get_direction_change, PointLike

_log = logging.getLogger('biDirAStar')


class GridMap:
    def __init__(self, row, col, exploration_setting='4N'):
        self.xRange = row  # size of background
        self.yRange = col
        self.explorationSetting = exploration_setting
        # self.u_set = [(-1, 0),  (0, 1),
        #               (1, 0), (0, -1)]
        # self.u_set = [(-1, 0), (-1, 1), (0, 1), (1, 1),
        #              (1, 0), (1, -1), (0, -1), (-1, -1)]
        self.obstacleMap = set()
        self.obstacleChecker = None

    def filter(self, neighbors: list, avoid_obstacles: bool):
        """
        :param neighbors: list of potential neighbors before filtering
        :param avoid_obstacles: if True, filter out obstacle cells in the list
        :return:
        """
        if avoid_obstacles:
            return [node for node in neighbors if self.in_bounds(node) and self.is_unoccupied(node)]
        return [node for node in neighbors if self.in_bounds(node)]

    def is_unoccupied(self, pos: (int, int)) -> bool:
        """
        :param pos: cell position we wish to check
        :return: True if cell is occupied with obstacle, False else
        """
        return pos not in self.obstacleMap

    def get_neighbors(self, vertex: (int, int), avoid_obstacles: bool = False) -> list:
        """
         if avoid_obstacles is true, actually give back the predecessor, otherwise successor
        :param avoid_obstacles: neighbor
        :param vertex: vertex you want to find direct successors from
        :return:
        """
        (_x, _y) = vertex

        if self.explorationSetting == '4N':
            _movements = self.get_movements_4n(x=_x, y=_y)
        else:
            _movements = self.get_movements_8n(x=_x, y=_y)
        _filtered_movements = self.filter(neighbors=_movements, avoid_obstacles=avoid_obstacles)

        return list(_filtered_movements)

    # def get_neighbors(self, s, avoid_obstacles: bool = False):
    #     nei_list = set()
    #     for u in self.u_set:
    #         s_next = tuple([s[i] + u[i] for i in range(2)])
    #         if s_next not in self.obstacleMap and self.xRange > s_next[0] > 0 and 0 < s_next[1] < self.yRange:
    #             nei_list.add(s_next)
    #
    #     return nei_list

    def update_obstacles(self, obstacle: set):
        self.obstacleMap = obstacle

    def add_obstacles(self, point_list: list):
        [self.obstacleMap.add(x) for x in point_list]

    def in_bounds(self, vertex: (int, int)) -> bool:
        """
        Checks if the provided coordinates are within
        the bounds of the grid map
        :param vertex: cell position (col,row)
        :return: True if within bounds, False else
        """
        (_x, _y) = vertex
        return 0 <= _x < self.xRange and 0 <= _y < self.yRange

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

    @staticmethod
    def get_movements_8n(x: int, y: int) -> list:
        """
        get all possible 8-connectivity movements.
        :return: list of movements with cost [(dx, dy, movement_cost)]
        """
        return [(x + 1, y + 0),
                (x + 0, y + 1),
                (x - 1, y + 0),
                (x + 0, y - 1),
                (x + 1, y + 1),
                (x - 1, y + 1),
                (x - 1, y - 1),
                (x + 1, y - 1)]


class BidirectionalAStar:
    def __init__(self, s_start, s_goal, gridmap: GridMap, heuristic_type='manhattan'):
        self.sStart = s_start
        self.sGoal = s_goal
        self.heuristicType = heuristic_type

        self.gridMap = gridmap  # class Env
        self.costModifier = None
        # self.uSet = self.Env.motions  # feasible input set
        # self.obstacles = self.Env.obs  # position of obstacles
        self.distance = self.h(s_start, s_goal)
        self.openFore = []  # OPEN set for forward searching
        self.openBack = []  # OPEN set for backward searching
        self.closedFore = []  # CLOSED set for forward
        self.closedBack = []  # CLOSED set for backward
        self.parentFore = dict()  # recorded parent for forward
        self.parentBack = dict()  # recorded parent for backward
        self.gFore = dict()  # cost to come for forward
        self.gBack = dict()  # cost to come for backward
        self.stop = False
        self.fValueForeModifier = None
        self.fValueBackModifier = None

    def setup(self):
        self.gFore[self.sStart] = 0.0
        self.gFore[self.sGoal] = math.inf
        self.gBack[self.sGoal] = 0.0
        self.gBack[self.sStart] = math.inf
        self.parentFore[self.sStart] = self.sStart
        self.parentBack[self.sGoal] = self.sGoal
        heapq.heappush(self.openFore,
                       (self.f_value_fore(self.sStart), self.sStart))
        heapq.heappush(self.openBack,
                       (self.f_value_back(self.sGoal), self.sGoal))

    def f_value_fore(self, s):
        """
        forward searching: f = g + h. (g: Cost to come, h: heuristic value)
        :param s: current state
        :return: f
        """

        return self.gFore[s] + self.h(s, self.sGoal) * 1 if self.fValueForeModifier is None else self.fValueForeModifier(s, self)

    def f_value_back(self, s):
        """
        backward searching: f = g + h. (g: Cost to come, h: heuristic value)
        :param s: current state
        :return: f
        """

        return self.gBack[s] + self.h(s, self.sStart) * 1 if self.fValueBackModifier is None else self.fValueBackModifier(s, self)

    def h(self, s, goal):
        """
        Calculate heuristic value.
        :param s: current node (state)
        :param goal: goal node (state)
        :return: heuristic value
        """

        heuristic_type = self.heuristicType

        if heuristic_type == "manhattan":
            return abs(goal[0] - s[0]) + abs(goal[1] - s[1])
        else:
            return math.hypot(goal[0] - s[0], goal[1] - s[1])

    def h2(self, s, goal):
        # return math.hypot(goal[0] - s[0], goal[1] - s[1])
        return abs(goal[0] - s[0]) + abs(goal[1] - s[1])

    def h3(self, s, goal):
        return math.hypot(goal[0] - s[0], goal[1] - s[1])

    # def get_neighbor(self, s):
    #     """
    #     find neighbors of state s that not in obstacles.
    #     :param s: state
    #     :return: neighbors
    #     """
    #
    #     return [(s[0] + u[0], s[1] + u[1]) for u in self.uSet]

    def extract_path(self, s_meet):
        """
        extract path from start and goal
        :param s_meet: meet point of bi-direction a*
        :return: path
        """

        # extract path for forward part
        _path_fore = [s_meet]
        _s = s_meet

        while True:
            _s = self.parentFore[_s]
            _path_fore.append(_s)
            if _s == self.sStart:
                break

        # extract path for backward part
        _path_back = []
        _s = s_meet

        while True:
            _s = self.parentBack[_s]
            _path_back.append(_s)
            if _s == self.sGoal:
                break

        return list(reversed(_path_fore)) + list(_path_back)

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
        if self.costModifier is None:
            return self.h2(p_from, p_to)
        else:
            _ret = self.costModifier(p_from, p_to, self)
            if _ret == 0:
                return self.h2(p_from, p_to)
            return self.costModifier(p_from, p_to, self)

    def is_collision(self, s_start, s_end):
        """
        check if the line segment (s_start, s_end) is collision.
        :param s_start: start node
        :param s_end: end node
        :return: True: is collision / False: not collision
        """
        _ret = False
        if s_start in self.gridMap.obstacleMap or s_end in self.gridMap.obstacleMap:
            _ret = True

        if s_start[0] != s_end[0] and s_start[1] != s_end[1]:
            if s_end[0] - s_start[0] == s_start[1] - s_end[1]:
                _s1 = (min(s_start[0], s_end[0]), min(s_start[1], s_end[1]))
                _s2 = (max(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
            else:
                _s1 = (min(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
                _s2 = (max(s_start[0], s_end[0]), min(s_start[1], s_end[1]))

            if _s1 in self.gridMap.obstacleMap or _s2 in self.gridMap.obstacleMap:
                _ret = True
        if self.gridMap.obstacleChecker is not None:
            _ret = self.gridMap.obstacleChecker(s_start) or self.gridMap.obstacleChecker(s_end)
        return _ret

    def search(self):
        """
        Bidirectional A*
        :return: connected path, visited order of forward, visited order of backward
        """
        self.setup()
        _s_meet = self.sStart
        while self.openFore and self.openBack and not self.stop:
            # solve forward-search
            _, _s_fore = heapq.heappop(self.openFore)
            if _s_fore in self.parentBack:
                _s_meet = _s_fore
                break
            self.closedFore.append(_s_fore)
            for s_n in self.gridMap.get_neighbors(_s_fore):
                _new_cost = self.gFore[_s_fore] + self.cost(_s_fore, s_n)
                if s_n not in self.gFore:
                    self.gFore[s_n] = math.inf
                if _new_cost < self.gFore[s_n]:
                    self.gFore[s_n] = _new_cost
                    self.parentFore[s_n] = _s_fore
                    heapq.heappush(self.openFore,
                                   (self.f_value_fore(s_n), s_n))
            # solve backward-search
            _, _s_back = heapq.heappop(self.openBack)
            if _s_back in self.parentFore:
                _s_meet = _s_back
                break
            self.closedBack.append(_s_back)

            for s_n in self.gridMap.get_neighbors(_s_back):
                _new_cost = self.gBack[_s_back] + self.cost(_s_back, s_n)
                if s_n not in self.gBack:
                    self.gBack[s_n] = math.inf
                if _new_cost < self.gBack[s_n]:
                    self.gBack[s_n] = _new_cost
                    self.parentBack[s_n] = _s_back
                    heapq.heappush(self.openBack,
                                   (self.f_value_back(s_n), s_n))

        return self.extract_path(_s_meet), self.closedFore, self.closedBack
