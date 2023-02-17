# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_backdrop_node.py
# ------------------------------------------------------------------------------
#
# File          : class_backdrop_node.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .class_node_object import NodeObject


class BackdropNode(NodeObject):
    """
    The ``NodeGraphQt.BackdropNode`` class allows other node object to be
    nested inside, it's mainly good for grouping nodes together.

    **Inherited from:** :class:`NodeGraphQt.NodeObject`

    .. image:: ../_images/backdrop.png
        :width: 250px

    -
    """

    def __init__(self, **kwargs):
        super(BackdropNode, self).__init__(**kwargs)

    def on_backdrop_updated(self, update_prop, value=None):
        """
        Slot triggered by the "on_backdrop_updated" signal from
        the node graph.

        Args:
            update_prop (str): update property type.
            value (object): update value (optional)
        """
        if value is None:
            return
        if update_prop == 'sizer_mouse_release':
            self.graph.begin_undo('resized "{}"'.format(self.label))
            self.view.set_property('width', value['width'])
            self.view.set_property('height', value['height'])
            self.view.set_pos(*value['pos'])
            self.graph.end_undo()
        elif update_prop == 'sizer_double_clicked':
            self.graph.begin_undo('"{}" auto resize'.format(self.label))
            self.view.set_property('width', value['width'])
            self.view.set_property('height', value['height'])
            self.view.set_pos(*value['pos'])
            self.graph.end_undo()

    def auto_size(self):
        """
        Auto resize the backdrop node to fit around the intersecting nodes.
        """
        self.graph.begin_undo('"{}" auto resize'.format(self.label))
        _size = self.view.calc_backdrop_size()
        self.view.set_property('width', _size['width'])
        self.view.set_property('height', _size['height'])
        self.view.set_pos(*_size['pos'])
        self.graph.end_undo()

    def wrap_nodes(self, nodes):
        """
        Set the backdrop size to fit around specified nodes.

        Args:
            nodes (list[NodeGraphQt.NodeObject]): list of nodes.
        """
        if not nodes:
            return
        self.graph.begin_undo('"{}" wrap nodes'.format(self.label))
        _size = self.view.calc_backdrop_size([n.view for n in nodes])
        self.view.set_property('width', _size['width'])
        self.view.set_property('height', _size['height'])
        self.view.set_pos(*_size['pos'])
        self.graph.end_undo()

    def get_nodes(self):
        """
        Returns nodes wrapped within the backdrop node.

        Returns:
            list[NodeGraphQt.BaseNode]: list of node under the backdrop.
        """
        _node_ids = [n.id for n in self.view.get_nodes()]
        return [self.graph.get_node_by_id(nid) for nid in _node_ids]


