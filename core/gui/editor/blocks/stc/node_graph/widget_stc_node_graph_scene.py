# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_stc_node_graph_scene.py
# ------------------------------------------------------------------------------
#
# File          : widget_stc_node_graph_scene.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtGui,QtCore
from gui.utils.helper import get_qApp
from gui.core.class_base import ThemeStyledUiObject
from gui.node_graph.views.class_node_graph_scene import NodeGraphScene
from gui.node_graph.core.define import EnumViewGridFeature
from .define import EnumSceneDefaultPalette


class STCNodeGraphScene(NodeGraphScene, ThemeStyledUiObject):
    def __init__(self, parent=None):
        NodeGraphScene.__init__(self, parent,
                                grid_mode=EnumViewGridFeature.GRID_DISPLAY_NONE.value,
                                grid_color=EnumSceneDefaultPalette.GRID_COLOR,
                                grid_size=EnumSceneDefaultPalette.GRID_SIZE)
        ThemeStyledUiObject.__init__(self)

    def on_theme_changed(self, topic=None, **msg_data):
        self.setBackgroundBrush(self.backgroundBrush())
