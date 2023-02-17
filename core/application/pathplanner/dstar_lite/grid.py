# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : grid.py
# ------------------------------------------------------------------------------
#
# File          : grid.py
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
from typing import Dict, List
from .utils import get_movements_4n, get_movements_8n, heuristic, Vertices, Vertex
from .define import UNOCCUPIED, OBSTACLE


class OccupancyGridMap:
    def __init__(self, x_dim, y_dim, exploration_setting='4N'):
        """
        set initial values for the map occupancy grid
        |----------> y, column
        |           (x=0,y=2)
        |
        V (x=2, y=0)
        x, row
        :param x_dim: dimension in the x direction
        :param y_dim: dimension in the y direction
        """
        self.xDim = x_dim
        self.yDim = y_dim

        # the map extents in units [m]
        self.mapExtents = (x_dim, y_dim)

        # the obstacle map
        self.occupancyGridMapData = np.zeros(self.mapExtents, dtype=np.uint8)

        # obstacles
        self.visited = {}
        self.explorationSetting = exploration_setting

    def get_map(self):
        """
        :return: return the current occupancy grid map
        """
        return self.occupancyGridMapData

    def set_map(self, new_grid):
        """
        :param new_grid:
        :return: None
        """
        self.occupancyGridMapData = new_grid

    def is_unoccupied(self, pos: (int, int)) -> bool:
        """
        :param pos: cell position we wish to check
        :return: True if cell is occupied with obstacle, False else
        """
        (_x, _y) = (round(pos[0]), round(pos[1]))  # make sure pos is int
        (_row, _col) = (_x, _y)

        # if not self.in_bounds(cell=(x, y)):
        #    raise IndexError("Map index out of bounds")

        return self.occupancyGridMapData[_row][_col] == UNOCCUPIED

    def in_bounds(self, cell: (int, int)) -> bool:
        """
        Checks if the provided coordinates are within
        the bounds of the grid map
        :param cell: cell position (x,y)
        :return: True if within bounds, False else
        """
        (_x, _y) = cell
        return 0 <= _x < self.xDim and 0 <= _y < self.yDim

    def filter(self, neighbors: List, avoid_obstacles: bool):
        """
        :param neighbors: list of potential neighbors before filtering
        :param avoid_obstacles: if True, filter out obstacle cells in the list
        :return:
        """
        if avoid_obstacles:
            return [node for node in neighbors if self.in_bounds(node) and self.is_unoccupied(node)]
        return [node for node in neighbors if self.in_bounds(node)]

    def get_successor(self, vertex: (int, int), avoid_obstacles: bool = False) -> list:
        """
         if avoid_obstacles is true, actually give back the predecessor, otherwise successor
        :param avoid_obstacles:
        :param vertex: vertex you want to find direct successors from
        :return:
        """
        (_x, _y) = vertex

        if self.explorationSetting == '4N':
            _movements = get_movements_4n(x=_x, y=_y)
        else:
            _movements = get_movements_8n(x=_x, y=_y)

        # not needed. Just makes aesthetics to the path
        #if (_x + _y) % 2 == 0: _movements.reverse()

        _filtered_movements = self.filter(neighbors=_movements, avoid_obstacles=avoid_obstacles)
        return list(_filtered_movements)

    def set_obstacle(self, pos: (int, int)):
        """
        :param pos: cell position we wish to set obstacle
        :return: None
        """
        (_x, _y) = (round(pos[0]), round(pos[1]))  # make sure pos is int
        (_row, _col) = (_x, _y)
        self.occupancyGridMapData[_row, _col] = OBSTACLE

    def set_obstacles(self, pos_list):
        [self.set_obstacle(x) for x in pos_list]

    def remove_obstacle(self, pos: (int, int)):
        """
        :param pos: position of obstacle
        :return: None
        """
        (_x, _y) = (round(pos[0]), round(pos[1]))  # make sure pos is int
        (_row, _col) = (_x, _y)
        self.occupancyGridMapData[_row, _col] = UNOCCUPIED

    def local_observation(self, global_position: (int, int), view_range: int = 2) -> Dict:
        """
        :param global_position: position of robot in the global map frame
        :param view_range: how far ahead we should look
        :return: dictionary of new observations
        """
        (_px, _py) = global_position
        _nodes = [(x, y) for x in range(_px - view_range, _px + view_range + 1)
                  for y in range(_py - view_range, _py + view_range + 1)
                  if self.in_bounds((x, y))]
        return {node: UNOCCUPIED if self.is_unoccupied(pos=node) else OBSTACLE for node in _nodes}

    def render(self, path: list):
        if not path:
            return
        for i in range(self.xDim):
            _s = ''
            for j in range(self.yDim):
                if (i, j) in path:
                    _s += '*' + ' '
                elif self.occupancyGridMapData[i, j] == OBSTACLE:
                    _s += '#' + ' '
                else:
                    _s += '.' + ' '
            print(_s)
