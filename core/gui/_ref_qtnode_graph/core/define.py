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
import os,pathlib

from core.gui.qtimp import QtWidgets
from enum import Enum

# ----------------------------------------------------
# private
# ----------------------------------------------------

URI_SCHEME = 'qtnodegraph://'
URN_SCHEME = 'qtnodegraph::'

# PATHS
BASE_PATH = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = BASE_PATH.parent.joinpath('resources').joinpath('image')

ICON_DOWN_ARROW = ICON_PATH.joinpath('down_arrow.png').resolve()
ICON_NODE_BASE = ICON_PATH.joinpath('node_base.png').resolve()

# DRAW STACK ORDER
Z_VAL_PIPE = -1
Z_VAL_NODE = 1
Z_VAL_PORT = 2
Z_VAL_NODE_WIDGET = 3

# ITEM CACHE MODE
# QGraphicsItem.NoCache
# QGraphicsItem.DeviceCoordinateCache
# QGraphicsItem.ItemCoordinateCache
ITEM_CACHE_MODE = QtWidgets.QGraphicsItem.CacheMode.DeviceCoordinateCache

# ----------------------------------------------------
# global
# ----------------------------------------------------
VERSION = '1.0.3'


class EnumVersion(Enum):
    """
    Current framework version.
    :py:mod:`NodeGraphQt.constants.VersionEnum`
    """
    #:
    MAJOR = int(VERSION.split('.')[0])
    #:
    MINOR = int(VERSION.split('.')[1])
    #:
    PATCH = int(VERSION.split('.')[2])


class EnumLayoutDirection(Enum):
    """
    Node graph nodes layout direction:
    :py:mod:`NodeGraphQt.constants.ViewerLayoutEnum`
    """
    #: layout nodes left to right.
    HORIZONTAL = 0
    #: layout nodes top to bottom.
    VERTICAL = 1


# ----------------------------------------------------
# view
# ----------------------------------------------------
class EnumViewFeature(Enum):
    """
    Node graph viewer styling layout:
    :py:mod:`NodeGraphQt.constants.ViewerEnum`
    """
    #: default background color for the node graph.
    BACKGROUND_COLOR = (35, 35, 35)
    #: style node graph background with no grid or dots.
    GRID_DISPLAY_NONE = 0
    #: style node graph background with dots.
    GRID_DISPLAY_DOTS = 1
    #: style node graph background with grid lines.
    GRID_DISPLAY_LINES = 2
    #: grid size when styled with grid lines.
    GRID_SIZE = 50
    #: grid line color.
    GRID_COLOR = (45, 45, 45)


class EnumViewNavStyle(Enum):
    """
    Node graph viewer navigation styling layout:
    :py:mod:`NodeGraphQt.constants.ViewerNavEnum`
    """
    #: default background color.
    BACKGROUND_COLOR = (25, 25, 25)
    #: default item color.
    ITEM_COLOR = (35, 35, 35)


# ----------------------------------------------------
# node
# ----------------------------------------------------

class EnumNodeStyleProperty(Enum):
    """
    Node styling layout:
    :py:mod:`NodeGraphQt.constants.NodeEnum`
    """
    #: default node width.
    WIDTH = 160
    #: default node height.
    HEIGHT = 60
    #: default node icon size (WxH).
    ICON_SIZE = 18
    #: default node overlay color when selected.
    SELECTED_COLOR = (255, 255, 255, 30)
    #: default node border color when selected.
    SELECTED_BORDER_COLOR = (254, 207, 42, 255)


# ----------------------------------------------------
# port
# ----------------------------------------------------
class EnumPortStyleProperty(Enum):
    """
    Port styling layout:
    :py:mod:`NodeGraphQt.constants.PortEnum`
    """
    #: default port size.
    SIZE = 22.0
    #: default port color. (r, g, b, a)
    COLOR = (49, 115, 100, 255)
    #: default port border color.
    BORDER_COLOR = (29, 202, 151, 255)
    #: port color when selected.
    ACTIVE_COLOR = (14, 45, 59, 255)
    #: port border color when selected.
    ACTIVE_BORDER_COLOR = (107, 166, 193, 255)
    #: port color on mouse over.
    HOVER_COLOR = (17, 43, 82, 255)
    #: port border color on mouse over.
    HOVER_BORDER_COLOR = (136, 255, 35, 255)
    #: threshold for selecting a port.
    CLICK_FALLOFF = 15.0


class EnumPortType(Enum):
    """
    Port connection types:
    :py:mod:`NodeGraphQt.constants.PortTypeEnum`
    """
    #: Connection type for input ports.
    IN = 'in'
    #: Connection type for output ports.
    OUT = 'out'


# ----------------------------------------------------
# pipe
# ----------------------------------------------------
class EnumPipeStyleProperty(Enum):
    """
    Pipe styling layout:
    :py:mod:`NodeGraphQt.constants.PipeEnum`
    """
    #: default width.
    WIDTH = 1.2
    #: default color.
    COLOR = (175, 95, 30, 255)
    #: pipe color to a node when it's disabled.
    DISABLED_COLOR = (190, 20, 20, 255)
    #: pipe color when selected or mouse over.
    ACTIVE_COLOR = (70, 255, 220, 255)
    #: pipe color to a node when it's selected.
    HIGHLIGHT_COLOR = (232, 184, 13, 255)
    #: draw connection as a line.
    DRAW_TYPE_DEFAULT = 0
    #: draw connection as dashed lines.
    DRAW_TYPE_DASHED = 1
    #: draw connection as a dotted line.
    DRAW_TYPE_DOTTED = 2


class EnumPipeSlicerStyleProperty(Enum):
    """
    Slicer Pipe styling layout:
    :py:mod:`NodeGraphQt.constants.PipeSlicerEnum`
    """
    #: default width.
    WIDTH = 1.5
    #: default color.
    COLOR = (255, 50, 75)


class EnumPipeShape(Enum):
    """
    Pipe connection drawing layout:
    :py:mod:`NodeGraphQt.constants.PipeLayoutEnum`
    """
    #: draw straight lines for pipe connections.
    STRAIGHT = 0
    #: draw curved lines for pipe connections.
    CURVED = 1
    #: draw angled lines for pipe connections.
    ANGLE = 2


# ----------------------------------------------------
# property widget
# ----------------------------------------------------
class EnumNodePropWidgetType(Enum):
    """
    Mapping used for the :class:`NodeGraphQt.PropertiesBinWidget` to display a
    node property in the specified widget type.

    :py:mod:`NodeGraphQt.constants.NodePropWidgetEnum`
    """
    #: Node property will be hidden in the ``PropertiesBinWidget`` (default).
    HIDDEN = 0
    #: Node property represented with a ``QLabel`` widget.
    QLABEL = 2
    #: Node property represented with a ``QLineEdit`` widget.
    QLINE_EDIT = 3
    #: Node property represented with a ``QTextEdit`` widget.
    QTEXT_EDIT = 4
    #: Node property represented with a ``QComboBox`` widget.
    QCOMBO_BOX = 5
    #: Node property represented with a ``QCheckBox`` widget.
    QCHECK_BOX = 6
    #: Node property represented with a ``QSpinBox`` widget.
    QSPIN_BOX = 7
    #: Node property represented with a ``QDoubleSpinBox`` widget.
    QDOUBLESPIN_BOX = 8
    #: Node property represented with a ColorPicker widget.
    COLOR_PICKER = 9
    #: Node property represented with a Slider widget.
    SLIDER = 10
    #: Node property represented with a file selector widget.
    FILE_OPEN = 11
    #: Node property represented with a file save widget.
    FILE_SAVE = 12
    #: Node property represented with a vector2 widget.
    VECTOR2 = 13
    #: Node property represented with vector3 widget.
    VECTOR3 = 14
    #: Node property represented with vector4 widget.
    VECTOR4 = 15
    #: Node property represented with float line edit widget.
    FLOAT = 16
    #: Node property represented with int line edit widget.
    INT = 17
    #: Node property represented with button widget.
    BUTTON = 18
