# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_base_node_view_item.py
# ------------------------------------------------------------------------------
#
# File          : class_base_node_view_item.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import typing
from gui import QtCore, QtWidgets
from ..core.commands import NodeViewPropertyChangedCmd
from ..core.class_base import PropertyDef
from ..core.exceptions import NodePropertyError
from ..core.define import (
    Z_VAL_NODE,
    ITEM_CACHE_MODE
)

if typing.TYPE_CHECKING:
    from gui.node_graph.class_node_object import NodeObject


class BaseNodeViewItem(QtWidgets.QGraphicsItem):
    """
    The base class of all node qgraphics item.
    """
    nodeNamespace = None

    def __init__(self, node: 'NodeObject', parent=None, **kwargs):
        super(BaseNodeViewItem, self).__init__(parent)
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable | self.GraphicsItemFlag.ItemIsMovable)
        self.setCacheMode(ITEM_CACHE_MODE)
        self.setZValue(Z_VAL_NODE)
        self.node = node

        self._color = kwargs.get('color', '#0d1217')
        self._borderColor = kwargs.get('border_color', '#4a5455')
        self._selectedBorderColor = kwargs.get('selected_border_color', '#fecf2a')
        self._textColor = kwargs.get('text_color', '#ffffff')
        self._disabled = kwargs.get('disabled', False)
        self._selected = kwargs.get('selected', False)
        self._visible = kwargs.get('visible', True)
        self._width = kwargs.get('width', 100.0)
        self._height = kwargs.get('height', 60.0)
        self._minWidth = kwargs.get('min_width', 100.0)
        self._minHeight = kwargs.get('min_height', 60.0)
        self._pos = kwargs.get('pos', [0.0, 0.0])

        # store the property attributes.
        # category in [appearance, Behaviour, data, layout]
        # for the readonly property, the assigned view could read and write, but not from gui.
        self._properties = [
            PropertyDef(name='id', object=self, getter='id', value_type='hex', readonly=True, category='data'),
            PropertyDef(name='type', object=self, getter='type_', readonly=True, category_name='data'),
            PropertyDef(name='icon', object=self, readonly=True),
            PropertyDef(value_type='str', name='label', category='appearance', getter='label', setter='label', object=self),
            PropertyDef(value_type='color:hex', name='color', getter='color', category='appearance', readonly=True, object=self),
            PropertyDef(value_type='color:hex', name='borderColor', getter='border_color', category='appearance', readonly=True,
                        object=self),
            PropertyDef(value_type='color:hex', name='selectedBorderColor', getter='selected_border_color', category='appearance', readonly=True,
                        object=self),
            PropertyDef(value_type='color:hex', name='textColor', getter='text_color', category='appearance', readonly=True,
                        object=self),
            PropertyDef(value_type='bool', name='disabled', getter='disabled', setter='disabled', category='behaviour', readonly=True,
                        object=self),
            PropertyDef(value_type='bool', name='selected', getter='selected', setter='selected', category='behaviour', readonly=True, object=self,
                        undoable=False),
            PropertyDef(value_type='bool', name='visible', getter='visible', setter='visible', category='behaviour', readonly=True, object=self),
            PropertyDef(value_type='int', name='width', getter='width', setter='width', category='appearance', readonly=True, object=self),
            PropertyDef(value_type='int', name='height', getter='height', setter='height', category='appearance', readonly=True, object=self),
            PropertyDef(value_type='xy', name='pos', getter=self.pos, setter=self.setPos, category='appearance', readonly=True, object=self),
            PropertyDef(value_type='enum', getter='layout_direction', name='layoutDirection', readonly=True, category='layout',
                        object=self)
        ]

    def __repr__(self):
        return '{}.{}(\'{}\')'.format(
            self.__module__, self.__class__.__name__, self.node.type_)

    @property
    def id(self):
        return self.node.id

    @property
    def type_(self):
        return self.node.type_

    @property
    def properties(self):
        """
        return all default node properties.

        Returns:
            dict: default node properties.
        """

        return self._properties

    @property
    def label(self):
        """
        Name of the node.

        Returns:
        str: name of the node.
        """
        return self.node.label

    @label.setter
    def label(self, label=''):
        """
        Set the name of the node.

        Args:
            label (str): name for the node.
        """
        self.node.label = label

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, state):
        self._disabled = state

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @property
    def border_color(self):
        return self._borderColor

    @border_color.setter
    def border_color(self, color):
        self._borderColor = color

    @property
    def selected_border_color(self):
        return self._selectedBorderColor

    @selected_border_color.setter
    def selected_border_color(self, color):
        self._selectedBorderColor = color

    @property
    def text_color(self):
        return self._textColor

    @text_color.setter
    def text_color(self, color):
        self._textColor = color

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def min_width(self):
        return self._minWidth

    @min_width.setter
    def min_width(self, value):
        self._minWidth = value

    @property
    def min_height(self):
        return self._minHeight

    @min_height.setter
    def min_height(self, value):
        self._minHeight = value

    @property
    def property_names(self):
        return [x.name for x in self._properties]

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self.width, self.height)

    def setSelected(self, selected):
        super(BaseNodeViewItem, self).setSelected(selected)

    def pre_init(self, viewer, pos=None):
        """
        Called before node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer.
            pos (tuple): the cursor pos if node is called with tab search.
        """
        assert self.node is not None, 'No node object assigned'

    def post_init(self, viewer, pos=None):
        """
        Called after node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer
            pos (tuple): the cursor pos if node is called with tab search.
        """
        self.draw()
        # set initial node position.
        if pos:
            if isinstance(pos, QtCore.QPointF):
                self.setPos(pos)
            else:
                self.setPos(*pos)

    def add_property(self, **kwargs):
        """
        add custom property.
        Args:
            kwargs (dict): arguments for property.
        """
        _name = kwargs.get('name')
        if not _name:
            raise NodePropertyError('property name is required')

        if _name in self.property_names:
            raise NodePropertyError(
                '"{}" reserved for default property.'.format(_name))
        kwargs['custom'] = True
        _prop = PropertyDef(**kwargs)
        self._properties.append(_prop)
        return _prop

    def get_prop_widget_type(self, prop_name):
        _prop = self.get_property(prop_name)
        return EnumNodePropWidgetType.HIDDEN.value

    def get_property_category_name(self, prop_name):
        _prop = self.get_property(prop_name)
        if _prop:
            return _prop.category
        return 'Properties'

    def update_properties_with(self, **kwargs):
        """
        convenient method to updating properties,
        Notice: those operations not in undoStack stored.
        """
        for k, v in kwargs.items():
            _prop = self.get_property(k)
            if _prop:
                self.do_set_property(_prop, v)

    def get_property(self, name) -> PropertyDef:
        """
        Return the node custom property.

        Args:
            name (str): name of the property.

        Returns:
            object: property data.
        """
        if name in self.property_names:
            return self._properties[self.property_names.index(name)]

    def set_property(self, name, value, push_undo=True):
        """
        Set the value on the node custom property.

        Args:
            name (str): name of the property.
            value (object): property data (python built in types).
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        _prop = self.get_property(name)
        if _prop is None:
            return
            # prevent signals from causing a infinite loop.
        if _prop.name == value:
            return

        # if self._graph and name == 'node_name':
        #     value = self._graph.get_unique_name(value)
        #     self.nodeName = value
        if value == _prop.get():
            return
        if not _prop.undoable:
            push_undo = False
        if self.node.graph:
            if push_undo:
                _undo_stack = self.node.graph.get_undo_stack()
                _cmd = NodeViewPropertyChangedCmd(self, name, value)
                _undo_stack.push(_cmd)
            else:
                NodeViewPropertyChangedCmd(self, name, value).redo()
        else:
            self.do_set_property(_prop, value)

    def do_set_property(self, prop: PropertyDef, value):
        _prev_v = prop.value
        try:
            prop.value = value
            prop.set()
        except Exception as e:
            prop.value = _prev_v
            raise NodePropertyError('property "{}" update error.'.format(prop.name))

    def has_property(self, name):
        """
        Check if node custom property exists.

        Args:
            name (str): name of the node.

        Returns:
            bool: true if property name exists in the Node.
        """
        return name in self.property_names

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

    # def from_dict(self, node_dict):
    #     """
    #     set the node view attributes from the dictionary.
    #
    #     Args:
    #         node_dict (dict): serialized node dict.
    #     """
    #     _node_attrs = list(self._properties.keys()) + ['width', 'height', 'pos']
    #     for name, value in node_dict.items():
    #         if name in _node_attrs:
    #             # "node.pos" conflicted with "QGraphicsItem.pos()"
    #             # so it's refactored to "xy_pos".
    #             if name == 'pos':
    #                 name = 'xy_pos'
    #             setattr(self, name, value)
    def update_from_node(self):
        pass

    # ---------------------------------------------------
    # override evnet handle
    # ---------------------------------------------------
    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: typing.Any) -> typing.Any:
        """
        Re-implemented to update pipes on selection changed.

        Args:
            change:
            value:
        """
        if change == self.GraphicsItemChange.ItemSelectedChange and self.scene():
            self.setZValue(Z_VAL_NODE)
            if not self.isSelected():
                self.setZValue(Z_VAL_NODE + 1)
        return super(BaseNodeViewItem, self).itemChange(change, value)

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Re-implemented to emit "node_double_clicked" signal.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            _view = self.get_view()
            if _view:
                _view.sigNodeDoubleClicked.emit(self.node.id)
        super(BaseNodeViewItem, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        """
        Re-implemented to update "self._properties['selected']" attribute.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        super(BaseNodeViewItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Re-implemented to ignore event if Alt modifier is pressed.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        if event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier:
            event.ignore()
            return
        super(BaseNodeViewItem, self).mouseReleaseEvent(event)

    def draw(self, *args, **kwargs):
        raise NotImplementedError
