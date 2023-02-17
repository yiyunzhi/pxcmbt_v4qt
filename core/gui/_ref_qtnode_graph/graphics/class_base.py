# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_base.py
# ------------------------------------------------------------------------------
#
# File          : class_base.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------

from gui import QtCore, QtWidgets

from ..core.define import (
    Z_VAL_NODE,
    ITEM_CACHE_MODE,
    EnumLayoutDirection,
    EnumNodeStyleProperty
)


class BaseNodeItem(QtWidgets.QGraphicsItem):
    """
    The base class of all node qgraphics item.
    """

    def __init__(self, name='node', parent=None):
        super(BaseNodeItem, self).__init__(parent)
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable | self.GraphicsItemFlag.ItemIsMovable)
        self.setCacheMode(ITEM_CACHE_MODE)
        self.setZValue(Z_VAL_NODE)
        self._properties = {
            'id': None,
            'name': name.strip(),
            'color': (13, 18, 23, 255),
            'borderColor': (46, 57, 66, 255),
            'textColor': (255, 255, 255, 180),
            'type_': 'BaseNodeItem',
            'selected': False,
            'disabled': False,
            'visible': False,
            'layoutDirection': EnumLayoutDirection.HORIZONTAL.value,
        }
        self._width = EnumNodeStyleProperty.WIDTH.value
        self._height = EnumNodeStyleProperty.HEIGHT.value

    def __repr__(self):
        return '{}.{}(\'{}\')'.format(
            self.__module__, self.__class__.__name__, self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._width, self._height)

    def mousePressEvent(self, event):
        """
        Re-implemented to update "self._properties['selected']" attribute.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        self._properties['selected'] = True
        super(BaseNodeItem, self).mousePressEvent(event)

    def setSelected(self, selected):
        self._properties['selected'] = selected
        super(BaseNodeItem, self).setSelected(selected)

    def pre_init(self, viewer, pos=None):
        """
        Called before node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer.
            pos (tuple): the cursor pos if node is called with tab search.
        """
        pass

    def post_init(self, viewer, pos=None):
        """
        Called after node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer
            pos (tuple): the cursor pos if node is called with tab search.
        """
        pass

    @property
    def id(self):
        return self._properties['id']

    @id.setter
    def id(self, unique_id=''):
        self._properties['id'] = unique_id

    @property
    def type_(self):
        return self._properties['type_']

    @type_.setter
    def type_(self, node_type='NODE'):
        self._properties['type_'] = node_type

    @property
    def layout_direction(self):
        return self._properties['layoutDirection']

    @layout_direction.setter
    def layout_direction(self, value=0):
        self._properties['layoutDirection'] = value

    @property
    def size(self):
        return self._width, self._height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width=0.0):
        self._width = width

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height=0.0):
        self._height = height

    @property
    def color(self):
        return self._properties['color']

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self._properties['color'] = color

    @property
    def text_color(self):
        return self._properties['textColor']

    @text_color.setter
    def text_color(self, color=(100, 100, 100, 255)):
        self._properties['textColor'] = color

    @property
    def border_color(self):
        return self._properties['borderColor']

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self._properties['borderColor'] = color

    @property
    def disabled(self):
        return self._properties['disabled']

    @disabled.setter
    def disabled(self, state=False):
        self._properties['disabled'] = state

    @property
    def selected(self):
        if self._properties['selected'] != self.isSelected():
            self._properties['selected'] = self.isSelected()
        return self._properties['selected']

    @selected.setter
    def selected(self, selected=False):
        self.setSelected(selected)

    @property
    def visible(self):
        return self._properties['visible']

    @visible.setter
    def visible(self, visible=False):
        self._properties['visible'] = visible
        self.setVisible(visible)

    @property
    def xy_pos(self):
        """
        return the item scene postion.
        ("node.pos" conflicted with "QGraphicsItem.pos()"
        so it was refactored to "xy_pos".)

        Returns:
            list[float]: x, y scene position.
        """
        return [float(self.scenePos().x()), float(self.scenePos().y())]

    @xy_pos.setter
    def xy_pos(self, pos=None):
        """
        set the item scene postion.
        ("node.pos" conflicted with "QGraphicsItem.pos()"
        so it was refactored to "xy_pos".)

        Args:
            pos (list[float]): x, y scene position.
        """
        pos = pos or [0.0, 0.0]
        self.setPos(pos[0], pos[1])

    @property
    def name(self):
        return self._properties['name']

    @name.setter
    def name(self, name=''):
        self._properties['name'] = name
        self.setToolTip('node: {}'.format(name))

    @property
    def properties(self):
        """
        return the node view attributes.

        Returns:
            dict: {property_name: property_value}
        """
        _props = {'width': self.width,
                 'height': self.height,
                 'pos': self.xy_pos}
        _props.update(self._properties)
        return _props

    def get_view(self):
        """
        return the main viewer.

        Returns:
            NodeGraphQt.widgets.viewer.NodeViewer: viewer object.
        """
        if self.scene():
            return self.scene().get_view()

    def delete(self):
        """
        remove node view from the scene.
        """
        if self.scene():
            self.scene().removeItem(self)

    def from_dict(self, node_dict):
        """
        set the node view attributes from the dictionary.

        Args:
            node_dict (dict): serialized node dict.
        """
        _node_attrs = list(self._properties.keys()) + ['width', 'height', 'pos']
        for name, value in node_dict.items():
            if name in _node_attrs:
                # "node.pos" conflicted with "QGraphicsItem.pos()"
                # so it's refactored to "xy_pos".
                if name == 'pos':
                    name = 'xy_pos'
                setattr(self, name, value)
