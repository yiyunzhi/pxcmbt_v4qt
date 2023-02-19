# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_node_object.py
# ------------------------------------------------------------------------------
#
# File          : class_node_object.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import Serializable,ClassFactory
from .core.define import EnumLayoutDirection


class _ClassProperty:

    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        return self.f(owner)


class NodeObject(Serializable):
    """
    The ``NodeObject`` class is the main base class that all
    nodes inherit from.

    **Inherited by:**
        :class:`BaseNode`,
        :class:`BackdropNode`

    Args:
        view_cls_name (str): the name of class which inherit from QGraphicsItem item used for drawing.
                             and registered in ClassMapper

            .. code-block:: python

                # snippet taken from the NodeGraphQt.BaseNode class.

                class BaseNode(NodeObject):

                    def __init__(self, view_cls_name=None, model=None):
                        graphics_item = graphics_item or NodeItem
                        super(BaseNode, self).__init__(view_cls_name)

    """
    serializeTag = '!NodeObject'
    nodeNamespace = 'builtIn'

    def __init__(self, **kwargs):
        """
        Args:
            view_cls_name (str): registered name of QGraphicsItem in ClassMapper, this class used for drawing.
        """
        assert self.nodeNamespace is not None, 'class attribute nodeName must be not None.'
        self._graph = None
        self._viewFactory = kwargs.get('view_factory', ClassFactory())
        self._label = kwargs.get('label', 'Node')
        self._layoutDirection = kwargs.get('layout_direction', EnumLayoutDirection.HORIZONTAL.value)

        # GroupNode attrs.
        self.subgraphSession = {}
        # view item
        self._viewType = kwargs.get('view_type')
        if self._viewType is None:
            raise RuntimeError(
                'No graphics item name specified for the node object!'
            )
        _view = self._viewFactory.create_class_instance(self._viewType, node=self)
        if _view is None:
            raise RuntimeError(
                'No graphics item class specified for the node object!'
            )
        self._view = _view

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self.type_, hex(id(self)))

    @property
    def serializer(self):
        return {'view_type': self._viewType}

    @_ClassProperty
    def type_(cls):
        """
        Node type identifier followed by the class name.
        `eg.` ``"com.foo.bar"``

        Returns:
            str: node type.
        """
        return cls.nodeNamespace + '.' + cls.__name__

    @property
    def id(self):
        """
        The node unique id.

        Returns:
            str: unique id string.
        """
        return hex(id(self))

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label=''):
        self._label = label

    @property
    def graph(self):
        """
        The parent node graph.

        Returns:
            NodeGraphQt.NodeGraph: node graph.
        """
        return self._graph

    @graph.setter
    def graph(self, graph):
        """
        The parent node graph.

        Returns:
            NodeGraphQt.NodeGraph: node graph.
        """
        self._graph = graph

    @property
    def view(self):
        """
        Returns the :class:`QtWidgets.QGraphicsItem` used in the scene.

        Returns:
            NodeGraphQt.qgraphics.node_abstract.AbstractNodeItem: node item.
        """
        return self._view

    @view.setter
    def view(self, view):
        """
        Set a new ``QGraphicsItem`` item to be used as the view.
        (the provided qgraphics item must be subclassed from the
        ``AbstractNodeItem`` object.)

        Args:
            view (NodeGraphQt.qgraphics.node_abstract.AbstractNodeItem): node item.
        """
        assert self._viewFactory.has_resgitered(view.p_type)
        if self._view:
            _old_view = self._view
            _scene = self._view.scene()
            _scene.removeItem(_old_view)
            self._view = view
            _scene.addItem(self._view)
        else:
            self._view = view
        self._viewType = view.p_type
        self._view.node = self

        # update the view.
        self.update_view()

    def update_view(self):
        """
        Update the node view from model.
        """
        if self._view is None:
            return
        self._view.update_from_node()

    @property
    def disabled(self):
        """
        Returns whether the node is enabled or disabled.

        Returns:
            bool: True if the node is disabled.
        """
        return self._view.disabled

    @disabled.setter
    def disabled(self, mode=False):
        """
        Set the node state to either disabled or enabled.

        Args:
            mode(bool): True to disable node.
        """
        self._view.disabled = mode

    @property
    def visible(self):
        """
        Returns the selected state of the node.

        Returns:
            bool: True if the node is selected.
        """
        return self._view.isVisible()

    @visible.setter
    def visible(self, visible=True):
        """
        Set the node to be selected or not selected.

        Args:
            visible (bool): True to visible the node.
        """
        self._view.setVisible(visible)

    @property
    def layout_direction(self):
        """
        Returns layout direction for this node.

        See Also:
            :meth:`NodeObject.set_layout_direction`

        Returns:
            int: node layout direction.
        """
        return self._layoutDirection

    @layout_direction.setter
    def layout_direction(self, value=0):
        """
        Sets the node layout direction to either horizontal or vertical on
        the current node only.

        `Implemented in` ``v0.3.0``

        See Also:
            :meth:`NodeGraph.set_layout_direction`
            :meth:`NodeObject.layout_direction`

        Warnings:
            This function does not register to the undo stack.

        Args:
            value (int): layout direction mode.
        """
        # fixme: check first if valid
        self._layoutDirection = value

    def on_delete(self):
        pass

    def on_remove(self):
        pass

    def on_clear_session(self):
        pass
