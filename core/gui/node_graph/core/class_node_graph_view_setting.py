# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_node_graph_view_setting.py
# ------------------------------------------------------------------------------
#
# File          : class_node_graph_view_setting.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import Serializable
from .define import EnumPipeShapeStyle


class NodeGraphViewSetting(Serializable):
    serializeTag = '!NodeGraphViewSetting'
    def __init__(self, **kwargs):
        self.zoomMax = kwargs.get('max_zoom', 2.0)
        self.zoomMin = kwargs.get('min_zoom', -0.95)
        self.pipeStyle = kwargs.get('pipe_style', EnumPipeShapeStyle.CURVED.value)
        self.pipeCollisionEnabled = kwargs.get('pipe_collision_enabled', False)
        self.acyclic = kwargs.get('acyclic', True)

    @property
    def serializer(self):
        return {
            'max_zoom': self.zoomMax,
            'min_zoom': self.zoomMin,
            'pipe_style': self.pipeStyle,
            'pipe_collision_enabled': self.pipeCollisionEnabled,
            'acyclic': self.acyclic,
        }
