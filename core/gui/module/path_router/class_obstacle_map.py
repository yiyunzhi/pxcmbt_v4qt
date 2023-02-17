# -*- coding: utf-8 -*-
import copy

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_obstacle_map.py
# ------------------------------------------------------------------------------
#
# File          : class_obstacle_map.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .util import ResolvedOptions, snap_to_grid, point_to_string


class ObstacleMap:
    def __init__(self, options: ResolvedOptions):
        self.options = options
        self.mapGridSize = 100
        self.map = dict()

    def build(self, model, edge):
        """
        Builds a map of all nodes for quicker obstacle queries i.e. is a point
        contained in any obstacle?
        """
        # source or target node could be excluded from set of obstacles
        _excluded_terminals = list()
        for x in self.options.excludeTerminals:
            pass
        return self

    def is_accessible(self, point):
        snap_to_grid(copy.copy(point), self.mapGridSize)
        _k = point_to_string(point)
        _rects = self.map.get(_k)
        return True if _rects is None else not any([x.contains(point) for x in _rects])
