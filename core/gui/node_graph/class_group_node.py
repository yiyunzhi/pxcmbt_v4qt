# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_group_node.py
# ------------------------------------------------------------------------------
#
# File          : class_group_node.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .class_base_node import BaseNode
from .class_port_node import PortInputNode, PortOutputNode
from ..graphics.class_group_node_item import GroupNodeItem


class GroupNode(BaseNode):
    """
    `Implemented in` ``v0.2.0``

    The ``NodeGraphQt.GroupNode`` class extends from the
    :class:``NodeGraphQt.BaseNode`` class with the ability to nest other nodes
    inside of it.

    **Inherited from:** :class:`NodeGraphQt.BaseNode`

    .. image:: ../_images/group_node.png
        :width: 250px

    -
    """

    NODE_NAME = 'Group'

    def __init__(self, graphics_item=None):
        super(GroupNode, self).__init__(graphics_item or GroupNodeItem)
        self._inputPortNodes = {}
        self._outputPortNodes = {}

    @property
    def is_expanded(self):
        """
        Returns if the group node is expanded or collapsed.

        Returns:
            bool: true if the node is expanded.
        """
        if not self.graph:
            return False
        return bool(self.id in self.graph.sub_graphs)

    def get_sub_graph(self):
        """
        Returns the sub graph controller to the group node if initialized
        or returns None.

        Returns:
            NodeGraphQt.SubGraph or None: sub graph controller.
        """
        return self.graph.sub_graphs.get(self.id)

    def get_sub_graph_session(self):
        """
        Returns the serialized sub graph session.

        Returns:
            dict: serialized sub graph session.
        """
        return self.model.subgraphSession

    def set_sub_graph_session(self, serialized_session):
        """
        Sets the sub graph session data to the group node.

        Args:
            serialized_session (dict): serialized session.
        """
        serialized_session = serialized_session or {}
        self.model.subgraphSession = serialized_session

    def expand(self):
        """
        Expand the group node session.

        See Also:
            :meth:`NodeGraph.expand_group_node`,
            :meth:`SubGraph.expand_group_node`.
        """
        self.graph.expand_group_node(self)

    def collapse(self):
        """
        Collapse the group node session it's expanded child sub graphs.

        See Also:
            :meth:`NodeGraph.collapse_group_node`,
            :meth:`SubGraph.collapse_group_node`.
        """
        self.graph.collapse_group_node(self)

    def add_input(self, name='input', multi_input=False, display_name=True,
                  color=None, locked=False, painter_func=None):
        _port = super(GroupNode, self).add_input(
            name=name,
            multi_input=multi_input,
            display_name=display_name,
            color=color,
            locked=locked,
            painter_func=painter_func
        )
        if self.is_expanded:
            _input_node = PortInputNode(parent_port=_port)
            _input_node.NODE_NAME = _port.name()
            _input_node.model.set_property('name', _port.name())
            _input_node.add_output(_port.name())
            _sub_graph = self.get_sub_graph()
            _sub_graph.add_node(_input_node, selected=False, push_undo=False)

        return _port

    def add_output(self, name='output', multi_output=True, display_name=True,
                   color=None, locked=False, painter_func=None):
        _port = super(GroupNode, self).add_output(
            name=name,
            multi_output=multi_output,
            display_name=display_name,
            color=color,
            locked=locked,
            painter_func=painter_func
        )
        if self.is_expanded:
            _output_port = PortOutputNode(parent_port=_port)
            _output_port.NODE_NAME = _port.name()
            _output_port.model.set_property('name', _port.name())
            _output_port.add_input(_port.name())
            _sub_graph = self.get_sub_graph()
            _sub_graph.add_node(_output_port, selected=False, push_undo=False)

        return _port

    def delete_input(self, port):
        if type(port) in [int, str]:
            port = self.get_output(port)
            if port is None:
                return

        if self.is_expanded:
            _sub_graph = self.get_sub_graph()
            _port_node = _sub_graph.get_node_by_port(port)
            if _port_node:
                _sub_graph.remove_node(_port_node, push_undo=False)

        super(GroupNode, self).delete_input(port)

    def delete_output(self, port):
        if type(port) in [int, str]:
            port = self.get_output(port)
            if port is None:
                return

        if self.is_expanded:
            _sub_graph = self.get_sub_graph()
            _port_node = _sub_graph.get_node_by_port(port)
            if _port_node:
                _sub_graph.remove_node(_port_node, push_undo=False)

        super(GroupNode, self).delete_output(port)
