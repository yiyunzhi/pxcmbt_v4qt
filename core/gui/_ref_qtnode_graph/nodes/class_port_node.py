# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_port_node.py
# ------------------------------------------------------------------------------
#
# File          : class_port_node.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------

from ..core.exceptions import PortRegistrationError
from .class_base_node import BaseNode
from ..graphics.class_port_in_item import PortInputNodeItem
from ..graphics.class_port_out_item import PortOutputNodeItem


class PortInputNode(BaseNode):
    """
    The ``PortInputNode`` class is the node object that represents a port from a
    :class:`NodeGraphQt.GroupNode` when expanded in a
    :class:`NodeGraphQt.SubGraph`.

    **Inherited from:** :class:`NodeGraphQt.BaseNode`

    .. image:: ../_images/port_in_node.png
        :width: 150px

    -
    """

    NODE_NAME = 'InputPort'

    def __init__(self, graphics_item=None, parent_port=None):
        super(PortInputNode, self).__init__(graphics_item or PortInputNodeItem)
        self._parentPort = parent_port

    @property
    def parent_port(self):
        """
        The parent group node port representing this node.

        Returns:
            NodeGraphQt.Port: port object.
        """
        return self._parentPort

    def add_input(self, name='input', multi_input=False, display_name=True,
                  color=None, locked=False, painter_func=None):
        """
        This is not available for the `PortInputNode` class.
        """
        raise PortRegistrationError(
            '"{}.add_input()" is not available for {}.'
            .format(self.__class__.__name__, self)
        )

    def add_output(self, name='output', multi_output=True, display_name=True,
                   color=None, locked=False, painter_func=None):
        if self._outputs:
            raise PortRegistrationError(
                '"{}.add_output()" only ONE output is allowed for this node.'
                .format(self.__class__.__name__, self)
            )
        super(PortInputNode, self).add_output(
            name=name,
            multi_output=multi_output,
            display_name=False,
            color=color,
            locked=locked,
            painter_func=None
        )


class PortOutputNode(BaseNode):
    """
    The ``PortOutputNode`` class is the node object that represents a port
    from a :class:`NodeGraphQt.GroupNode` when expanded in a
    :class:`NodeGraphQt.SubGraph`.

    **Inherited from:** :class:`NodeGraphQt.BaseNode`

    .. image:: ../_images/port_out_node.png
        :width: 150px

    -
    """

    NODE_NAME = 'OutputPort'

    def __init__(self, graphics_item=None, parent_port=None):
        super(PortOutputNode, self).__init__(graphics_item or PortOutputNodeItem)
        self._parentPort = parent_port

    @property
    def parent_port(self):
        """
        The parent group node port representing this node.

        Returns:
            NodeGraphQt.Port: port object.
        """
        return self._parentPort

    def add_input(self, name='input', multi_input=False, display_name=True,
                  color=None, locked=False, painter_func=None):
        if self._inputs:
            raise PortRegistrationError(
                '"{}.add_input()" only ONE input is allowed for this node.'
                .format(self.__class__.__name__, self)
            )
        super(PortOutputNode, self).add_input(
            name=name,
            multi_input=multi_input,
            display_name=False,
            color=color,
            locked=locked,
            painter_func=None
        )

    def add_output(self, name='output', multi_output=True, display_name=True,
                   color=None, locked=False, painter_func=None):
        """
        This is not available for the `PortOutputNode` class.
        """
        raise PortRegistrationError(
            '"{}.add_output()" is not available for {}.'
            .format(self.__class__.__name__, self)
        )
