# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : define.py
# ------------------------------------------------------------------------------
#
# File          : define.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
NODE_GRAPH_STATE_NS = 'State'
NODE_GRAPH_PSEUDO_NS = 'Pseudo'
NODE_GRAPH_TOOL_NS = 'Tools'
NODE_GRAPH_NS = 'GRAPH'
CLASS_FACTORY_NS_KEY = 'nodeNamespace'


class EnumSceneDefaultPalette:
    BG_COLOR = '#ADB8C6'
    GRID_COLOR = '#525A65'
    GRID_SIZE = 10


class EnumNodeDefaultPalette:
    BG_COLOR = '#ffeccc'
    BORDER_COLOR = '#B4AA99'
    SELECTED_BORDER_COLOR = '#FF8B5C'
    TEXT_COLOR = '#777777'
    WIDTH = 100
    HEIGHT = 60
    MIN_WIDTH = 100
    MIN_HEIGHT = 60
    BORDER_RADIUS = 16
    ICON_SIZE = 18


DEFAULT_STATE_STYLE = {
    'color': EnumNodeDefaultPalette.BG_COLOR,
    'text_color': EnumNodeDefaultPalette.TEXT_COLOR,
    'border_color': EnumNodeDefaultPalette.BORDER_COLOR,
    'selected_border_color': EnumNodeDefaultPalette.SELECTED_BORDER_COLOR,
    'width': EnumNodeDefaultPalette.WIDTH,
    'height': EnumNodeDefaultPalette.HEIGHT,
    'min_width': EnumNodeDefaultPalette.MIN_WIDTH,
    'min_height': EnumNodeDefaultPalette.MIN_HEIGHT,
    'border_radius': EnumNodeDefaultPalette.BORDER_RADIUS,
    'icon_size': EnumNodeDefaultPalette.ICON_SIZE
}

DEFAULT_INITIAL_STATE_STYLE = {
    'color': '#101010',
    'text_color': EnumNodeDefaultPalette.TEXT_COLOR,
    'border_color': EnumNodeDefaultPalette.BORDER_COLOR,
    'selected_border_color': EnumNodeDefaultPalette.SELECTED_BORDER_COLOR,
    'width': 18,
    'height': 18,
    'min_width': 18,
    'min_height': 18,
}
