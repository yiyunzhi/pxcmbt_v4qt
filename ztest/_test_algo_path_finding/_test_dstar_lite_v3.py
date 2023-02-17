# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_dstar_lite_v2.py
# ------------------------------------------------------------------------------
#
# File          : _test_dstar_lite_v2.py
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
import numpy as np


class GridMap:
    def __init__(self, row, col, exploration_setting='4N'):
        self.xRange = row  # size of background
        self.yRange = col
        self.explorationSetting = exploration_setting
        self.u_set = [(-1, 0),  (0, 1),
                       (1, 0), (0, -1)]
        #self.u_set = [(-1, 0), (-1, 1), (0, 1), (1, 1),
        #              (1, 0), (1, -1), (0, -1), (-1, -1)]
        self.obstacleMap = set()

    def get_motion(self):
        pass

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

    def get_neighbors1(self, vertex: (int, int), avoid_obstacles: bool = False) -> list:
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

    def get_neighbors(self, s, avoid_obstacles: bool = False):
        nei_list = set()
        for u in self.u_set:
            s_next = tuple([s[i] + u[i] for i in range(2)])
            if s_next not in self.obstacleMap and self.xRange>s_next[0] > 0 and 0<s_next[1]<self.yRange:
                nei_list.add(s_next)

        return nei_list

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


class DStarLite:
    def __init__(self, s_start, s_goal, grid_map, heuristic_type):
        self.sStart, self.sGoal = s_start, s_goal
        self.heuristicType = heuristic_type
        self.gridMap = grid_map
        # self.Plot = Plotting(s_start, s_goal)

        # self.u_set = self.Env.motions  # feasible input set
        # self.obs = self.Env.obs  # position of obstacles
        # self.x = self.Env.x_range
        # self.y = self.Env.y_range

        self.g, self.rhs, self.U = {}, {}, {}
        self.kMin = 0

        for i in range(self.gridMap.xRange):
            for j in range(self.gridMap.yRange):
                self.rhs[(i, j)] = float("inf")
                self.g[(i, j)] = float("inf")
        # self.rhs = np.ones((grid_map.xRange, grid_map.yRange)) * np.inf
        # self.g = self.rhs.copy()
        self.rhs[self.sGoal] = 0.0
        self.U[self.sGoal] = self.calculate_key(self.sGoal)
        self.visited = set()
        self.count = 0

    def run(self):
        # self.Plot.plot_grid("D* Lite")
        _t = time.time()
        self.compute_path()
        print('time usage:', time.time() - _t)
        self.plot_path(self.extract_path())
        # self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        # plt.show()

    # def on_press(self, event):
    #     x, y = event.xdata, event.ydata
    #     if x < 0 or x > self.x - 1 or y < 0 or y > self.y - 1:
    #         print("Please choose right area!")
    #     else:
    #         x, y = int(x), int(y)
    #         print("Change position: s =", x, ",", "y =", y)
    #
    #         s_curr = self.s_start
    #         s_last = self.s_start
    #         i = 0
    #         path = [self.s_start]
    #
    #         while s_curr != self.s_goal:
    #             s_list = {}
    #
    #             for s in self.get_neighbor(s_curr):
    #                 s_list[s] = self.g[s] + self.cost(s_curr, s)
    #             s_curr = min(s_list, key=s_list.get)
    #             path.append(s_curr)
    #
    #             if i < 1:
    #                 self.km += self.h(s_last, s_curr)
    #                 s_last = s_curr
    #                 if (x, y) not in self.obs:
    #                     self.obs.add((x, y))
    #                     plt.plot(x, y, 'sk')
    #                     self.g[(x, y)] = float("inf")
    #                     self.rhs[(x, y)] = float("inf")
    #                 else:
    #                     self.obs.remove((x, y))
    #                     plt.plot(x, y, marker='s', color='white')
    #                     self.UpdateVertex((x, y))
    #                 for s in self.get_neighbor((x, y)):
    #                     self.UpdateVertex(s)
    #                 i += 1
    #
    #                 self.count += 1
    #                 self.visited = set()
    #                 self.ComputePath()
    #
    #         self.plot_visited(self.visited)
    #         self.plot_path(path)
    #         self.fig.canvas.draw_idle()

    def compute_path(self):
        while True:
            _s, _v = self.get_top_key()
            if _v >= self.calculate_key(self.sStart) and self.rhs[self.sStart] == self.g[self.sStart]:
                break

            _k_old = _v
            self.U.pop(_s)
            self.visited.add(_s)

            if _k_old < self.calculate_key(_s):
                self.U[_s] = self.calculate_key(_s)
            elif self.g[_s] > self.rhs[_s]:
                self.g[_s] = self.rhs[_s]
                for x in self.gridMap.get_neighbors(_s, True):
                    self.update_vertex(x)
            else:
                self.g[_s] = float("inf")
                self.update_vertex(_s)
                for x in self.gridMap.get_neighbors(_s, True):
                    self.update_vertex(x)

    def update_vertex(self, s):
        if s != self.sGoal:
            self.rhs[s] = float("inf")
            for x in self.gridMap.get_neighbors(s, True):
                self.rhs[s] = min(self.rhs[s], self.g[x] + self.cost(s, x))
        if s in self.U:
            self.U.pop(s)

        if self.g[s] != self.rhs[s]:
            self.U[s] = self.calculate_key(s)

    def calculate_key(self, s):
        return [min(self.g[s], self.rhs[s]) + self.h(self.sStart, s) + self.kMin,
                min(self.g[s], self.rhs[s])]

    def get_top_key(self):
        """
        :return: return the min key and its value.
        """

        _s = min(self.U, key=self.U.get)
        return _s, self.U[_s]

    def h(self, s_start, s_goal):
        if self.heuristicType == "manhattan":
            return abs(s_goal[0] - s_start[0]) + abs(s_goal[1] - s_start[1])
        else:
            return math.hypot(s_goal[0] - s_start[0], s_goal[1] - s_start[1])

    def cost(self, s_start, s_goal):
        """
        Calculate Cost for this motion
        :param s_start: starting node
        :param s_goal: end node
        :return:  Cost for this motion
        :note: Cost function could be more complicate!
        """
        if self.is_collision(s_start, s_goal):
            return float("inf")
        return math.hypot(s_goal[0] - s_start[0], s_goal[1] - s_start[1])

    def is_collision(self, s_start, s_end):
        if s_start in self.gridMap.obstacleMap or s_end in self.gridMap.obstacleMap:
            return True
        if s_start[0] != s_end[0] and s_start[1] != s_end[1]:
            if s_end[0] - s_start[0] == s_start[1] - s_end[1]:
                s1 = (min(s_start[0], s_end[0]), min(s_start[1], s_end[1]))
                s2 = (max(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
            else:
                s1 = (min(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
                s2 = (max(s_start[0], s_end[0]), min(s_start[1], s_end[1]))
            if s1 in self.gridMap.obstacleMap or s2 in self.gridMap.obstacleMap:
                return True
        return False

    def extract_path(self):
        """
        Extract the path based on the PARENT set.
        :return: The planning path
        """

        _path = [self.sStart]
        _s = self.sStart
        for i in range(200):
            _g_list = {}
            for x in self.gridMap.get_neighbors(_s):
                if not self.is_collision(_s, x):
                    _g_list[x] = self.g[x]
            _s = min(_g_list, key=_g_list.get)
            _path.append(_s)
            if _s == self.sGoal:
                break

        return list(_path)

    def plot_path(self, path):
        for i in range(self.gridMap.yRange):
            _s = ''
            for j in range(self.gridMap.xRange):
                if (j, i) in path:
                    _s += '*' + ' '
                elif (j, i) in self.gridMap.obstacleMap:
                    _s += '#' + ' '
                else:
                    _s += '.' + ' '
            print(_s)

    def plot_visited(self, visited):
        for i in range(self.gridMap.yRange):
            _s = ''
            for j in range(self.gridMap.xRange):
                if (j, i) in visited:
                    _s += 'v' + ' '
                elif (j, i) in self.gridMap.obstacleMap:
                    _s += '#' + ' '
                else:
                    _s += '.' + ' '
            print(_s)


def main():
    s_start = (1, 2)
    s_goal = (85, 90)
    _map = GridMap(100, 100)
    # _map.add_obstacles([(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(44,5)])
    _dstarl = DStarLite(s_start, s_goal, _map, "euclidean")
    _dstarl.run()


if __name__ == '__main__':
    main()
