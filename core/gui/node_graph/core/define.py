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
import pathlib, os
import enum
from core.gui.qtimp import QtWidgets

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


class EnumVersion(enum.Enum):
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


class EnumLayoutDirection(enum.Enum):
    """
    Node graph nodes layout direction:
    :py:mod:`NodeGraphQt.constants.ViewerLayoutEnum`
    """
    #: layout nodes left to right.
    HORIZONTAL = 0
    #: layout nodes top to bottom.
    VERTICAL = 1


class EnumPortType(enum.Enum):
    """
    Port connection types:
    :py:mod:`NodeGraphQt.constants.PortTypeEnum`
    """
    #: Connection type for input ports.
    IN = 'in'
    #: Connection type for output ports.
    OUT = 'out'


# ----------------------------------------------------
# view
# ----------------------------------------------------
class EnumViewGridFeature(enum.Enum):
    """
    Node graph viewer styling layout:
    :py:mod:`NodeGraphQt.constants.ViewerEnum`
    """
    #: style node graph background with no grid or dots.
    GRID_DISPLAY_NONE = 0
    #: style node graph background with dots.
    GRID_DISPLAY_DOTS = 1
    #: style node graph background with grid lines.
    GRID_DISPLAY_LINES = 2
    #: grid size when styled with grid lines.
    GRID_SIZE = 50


class EnumViewPalette:
    #: default background color for the node graph.
    BACKGROUND_COLOR = '#232323'
    #: grid line color.
    GRID_COLOR = '#2D2D2D'


# ----------------------------------------------------
# property widget
# ----------------------------------------------------
class EnumNodePropWidgetType(enum.Enum):
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


class EnumGraphViewFlag:
    # brief Allow multiselection box
    MULTI_SELECTION = 0x0001
    # Allow shapes size change done via the multiselection box
    MULTI_SIZE_CHANGE = 0x0002
    # Show grid
    SHOW_GRID_NONE = 0x0004
    SHOW_DOT_GRID = 0x0008
    SHOW_LINE_GRID = 0x0010
    # Use grid
    SNAP_GRID = 0x0020
    # Enable Drag & Drop operations
    DND = 0x0040
    # Enable Undo/Redo operations
    UNDOREDO = 0x0080
    #  Enable the clipboard
    CLIPBOARD = 0x0100
    # Enable mouse hovering
    HOVERING = 0x0200
    # Enable highligting of shapes able to accept dragged shape(s)
    HIGHLIGHTING = 0x0400
    # Use gradient color for the canvas background
    GRADIENT_BACKGROUND = 0x0800
    # Print also canvas background
    PRINT_BACKGROUND = 0x1000
    # Process mouse wheel by the canvas (canvas scale will be changed)
    PROCESS_MOUSEWHEEL = 0x2000
    PIPE_COLLISION = 0x4000
    DEFAULT = (MULTI_SELECTION
               | MULTI_SIZE_CHANGE
               | DND
               | SHOW_GRID_NONE
               | UNDOREDO
               | CLIPBOARD
               | HOVERING
               | HIGHLIGHTING)
    ALL = [MULTI_SELECTION, MULTI_SIZE_CHANGE, SHOW_LINE_GRID, SHOW_DOT_GRID, SHOW_GRID_NONE, SNAP_GRID, DND, UNDOREDO,
           CLIPBOARD, HOVERING, HIGHLIGHTING, GRADIENT_BACKGROUND, PRINT_BACKGROUND, PROCESS_MOUSEWHEEL, PIPE_COLLISION]


class EnumGraphFlag:
    ACYCLIC = 0x0001
    DEFAULT = 0
    ALL = [ACYCLIC]


class EnumNodeConnectionPolicy(enum.IntEnum):
    ANYWHERE = 1
    ONLY_ON_CONNECTION_POINT = 2
    ONLY_ON_PORT = 3
    NONE = -1


class EnumPipeShapeStyle(enum.IntEnum):
    CURVED = 1
    STRAIGHT = 2
    ANGLE = 3
    ORTHOGONAL = 4


class EnumNodeEditFlag(enum.IntEnum):
    COPYABLE = 0x0001
    DELETEABLE = 0x0002
    REUSEABLE = 0x0004
    STYLE_DEFAULT = COPYABLE | DELETEABLE | REUSEABLE


class EnumNodeFlag(enum.IntEnum):
    # Interactive parent change is allowed
    REPARENT = 0x000001
    # Interactive position change is allowed
    REPOSITION = 0x000002
    # Interactive size change is allowed
    RESIZE = 0x000004
    # Shape is highlighted at mouse hovering
    HOVERING = 0x000008
    # Shape is highlighted at mouse select
    SELECTION = 0x000010
    # Shape is highlighted at shape dragging
    HIGHLIGHTING = 0x000020
    # Shape is always inside its parent
    ALWAYS_INSIDE = 0x000040
    # User data is destroyed at the shape deletion
    DELETE_USER_DATA = 0x000080
    # The DEL key is processed by the shape (not by the shape canvas)
    PROCESS_K_DEL = 0x000100
    # Show handles if the shape is selected
    SHOW_HANDLES = 0x000200
    # Show shadow under the shape
    SHOW_SHADOW = 0x000400
    # Show connection point on the shape
    SHOW_CONNECTION_PTS = 0x000800
    # Lock children relative position if the parent is resized
    LOCK_CHILDREN = 0x001000
    # Emit events (catchable in shape canvas)
    EMIT_EVENTS = 0x002000
    # Propagate mouse dragging event to parent shape
    PROPAGATE_DRAGGING = 0x004000
    # Propagate selection to parent shape
    # (it means this shape cannot be selected because its focus is redirected to its parent shape)
    PROPAGATE_SELECTION = 0x008000
    # Propagate interactive connection request to parent shape
    # (it means this shape cannot be connected interactively because this feature is redirected to its parent shape)
    PROPAGATE_INTERACTIVE_CONNECTION = 0x010000
    # Do no resize the shape to fit its children automatically
    NO_FIT_TO_CHILDREN = 0x020000
    # Do no resize the shape to fit its children automatically
    PROPAGATE_HOVERING = 0x040000
    # Propagate hovering to parent
    PROPAGATE_HIGHLIGHTING = 0x080000
    # if ration keeping while resizing
    RESIZE_KEEP_RATIO = 0x100000
    # if fixed the center of the shape while resizing
    USE_CENTER_RESIZING = 0x200000
    # if disappeared while too small
    DISAPPEAR_WHEN_SMALL = 0x400000
    STYLE_DEFAULT = (REPARENT | REPOSITION | RESIZE | HOVERING | SELECTION
                     | HIGHLIGHTING | SHOW_HANDLES | ALWAYS_INSIDE | DELETE_USER_DATA)
