# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_node_graph.py
# ------------------------------------------------------------------------------
#
# File          : class_node_graph.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os, re, copy, json
from application.core.base import Serializable
from gui import QtGui, QtWidgets, QtCore, SerializableQObject
from .views.class_node_graph_view import NodeGraphView
from .class_node_object import NodeObject
from .core.define import (EnumLayoutDirection, URN_SCHEME, URI_SCHEME, EnumGraphViewFlag, EnumGraphFlag, EnumPipeShapeStyle)
from . import ClassFactory
from .core.class_menu import NodeGraphMenu, NodesMenu
from gui.node_graph.views.class_node_graph_widget import NodeGraphWidget
from .core.class_node_graph_view_setting import NodeGraphViewSetting
from .core.exceptions import *
from .core.commands import (NodeViewAddedCmd,
                            NodeViewRemovedCmd,
                            NodeViewMovedCmd,
                            PortViewConnectedCmd)


class NodeGraph(QtCore.QObject, Serializable, metaclass=SerializableQObject):
    """
        The ``NodeGraph`` class is the main controller for managing all nodes
        and the node graph.

        Inherited from: :class:`PySide2.QtCore.QObject`

        .. image:: _images/graph.png
            :width: 60%
        """

    serializeTag = '!NodeGraph'
    sigNodesRegistered = QtCore.Signal(list)
    """
    Signal triggered when a node is registered into the node graph.

    :parameters: list[:class:`NodeGraphQt.NodeObject`]
    :emits: registered nodes
    """

    sigNodeCreated = QtCore.Signal(NodeObject)
    """
    Signal triggered when a node is created in the node graph.

    :parameters: :class:`NodeGraphQt.NodeObject`
    :emits: created node
    """
    sigNodesDeleted = QtCore.Signal(list)
    """
    Signal triggered when nodes have been deleted from the node graph.

    :parameters: list[str]
    :emits: list of deleted node ids.
    """
    sigNodeSelected = QtCore.Signal(NodeObject)
    """
    Signal triggered when a node is clicked with the LMB.

    :parameters: :class:`NodeGraphQt.NodeObject`
    :emits: selected node
    """
    sigNodeSelectionChanged = QtCore.Signal(list, list)
    """
    Signal triggered when the node selection has changed.

    :parameters: list[:class:`NodeGraphQt.NodeObject`],
                 list[:class:`NodeGraphQt.NodeObject`]
    :emits: selected node, deselected nodes.
    """
    sigNodeDoubleClicked = QtCore.Signal(NodeObject)
    """
    Signal triggered when a node is double clicked and emits the node.

    :parameters: :class:`NodeGraphQt.NodeObject`
    :emits: selected node
    """
    sigPortConnected = QtCore.Signal(object, object)
    """
    Signal triggered when a node port has been connected.

    :parameters: :class:`NodeGraphQt.Port`, :class:`NodeGraphQt.Port`
    :emits: input port, output port
    """
    sigPortDisconnected = QtCore.Signal(object, object)
    """
    Signal triggered when a node port has been disconnected.

    :parameters: :class:`NodeGraphQt.Port`, :class:`NodeGraphQt.Port`
    :emits: input port, output port
    """
    sigPropertyChanged = QtCore.Signal(NodeObject, str, object)
    """
    Signal is triggered when a property has changed on a node.

    :parameters: :class:`NodeGraphQt.BaseNode`, str, object
    :emits: triggered node, property name, property value
    """
    sigDataDropped = QtCore.Signal(QtCore.QMimeData, QtCore.QPoint)
    """
    Signal is triggered when data has been dropped to the graph.

    :parameters: :class:`PySide2.QtCore.QMimeData`, :class:`PySide2.QtCore.QPoint`
    :emits: mime data, node graph position
    """
    sigSessionChanged = QtCore.Signal(str)
    """
    Signal is triggered when session has been changed.

    :parameters: :str
    :emits: new session path
    """
    sigOpenSubGraphRequired = QtCore.Signal(str, str)
    sigCloseSubGraphRequired = QtCore.Signal(str)
    sigShowSubGraphRequired = QtCore.Signal(str)

    def __init__(self, parent: QtCore.QObject = None, **kwargs):
        """
        Args:
            parent (object): object parent.
            **kwargs : Used for overriding internal objects while initial.
        """
        super(NodeGraph, self).__init__(parent)
        self.setObjectName('NodeGraph')
        self.__common_node_props = {}

        self.nodes = kwargs.get('nodes', {})
        self.session = ''
        self._layoutDirection = kwargs.get('layout_direction', EnumLayoutDirection.HORIZONTAL.value)
        self._viewFlags = kwargs.get('view_flags', EnumGraphViewFlag.DEFAULT)
        self._flags = kwargs.get('flags', EnumGraphFlag.DEFAULT)
        self._viewSetting = kwargs.get('view_setting', NodeGraphViewSetting())
        self._viewFactory = kwargs.get('view_factory') or ClassFactory()
        self._nodeFactory = kwargs.get('node_factory') or ClassFactory()
        self._undoView = None
        self._undoStack = kwargs.get('undo_stack') or QtGui.QUndoStack(self)
        self._widget = None
        self._subGraphs = kwargs.get('sub_graphs', dict())
        self._contextMenu = {}
        # initial view instance
        self._viewType = kwargs.get('view_type')
        if self._viewType is None:
            _view = NodeGraphView(undo_stack=self._undoStack, graph=self)
        else:
            _view = self._viewFactory.create_class_instance(self._viewType, graph=self, undo_stack=self._undoStack)
        self._view = _view
        self._view.set_layout_direction(self._layoutDirection)

        self.register_view_context_menu(kwargs.get('context_menus'))
        self._register_builtin_nodes()
        self._wire_signals()

    def __repr__(self):
        return '<{}("root") object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    @property
    def serializer(self):
        return {'layout_direction': self._layoutDirection,
                'view_type': self._viewType,
                'view_flags': self._viewFlags,
                'view_setting': self._viewSetting,
                'flags': self._flags,
                'nodes': self.nodes,
                'sub_graphs': self._subGraphs}

    @property
    def p_view(self):
        return self._view

    def register_view_context_menu(self, menus=None):
        """
        Register the default context menus.
        """
        if not self._view:
            return
        if menus is None:
            menus = self._view.get_context_menus()
        if menus.get('graph'):
            self._contextMenu['graph'] = NodeGraphMenu(self, menus['graph'])
        if menus.get('nodes'):
            self._contextMenu['nodes'] = NodesMenu(self, menus['nodes'])

    def _register_builtin_nodes(self):
        """
        Register the default builtin nodes to the :meth:`NodeGraph.node_factory`
        """
        pass

    def _wire_signals(self):
        """
        Connect up all the signals and slots here.
        """

        # internal signals.
        self._view.sigSearchTriggered.connect(self.on_search_triggered)
        self._view.sigConnectionSliced.connect(self.on_connection_sliced)
        self._view.sigConnectionChanged.connect(self.on_connection_changed)
        self._view.sigMovedNodes.connect(self.on_nodes_moved)
        self._view.sigNodeDoubleClicked.connect(self.on_node_double_clicked)
        self._view.sigNodeLabelChanged.connect(self.on_node_label_changed)
        self._view.sigNodeInserted.connect(self.on_insert_node)

        # pass through translated signals.
        self._view.sigNodeSelected.connect(self.on_node_selected)
        self._view.sigNodeSelectionChanged.connect(self.on_node_selection_changed)
        self._view.sigDataDropped.connect(self.on_node_data_dropped)
        # self._view.sigBackdropNodeUpdated.connect(self.on_node_backdrop_updated)

    @staticmethod
    def set_flag(flags, flag, on):
        if flag not in flags.ALL:
            return
        if on:
            flags |= flag
        else:
            flags &= ~flag

    @staticmethod
    def has_flag(flags, flag):
        return (flags & flag) != 0

    @property
    def flags(self):
        return self._flags

    @property
    def view_flags(self):
        return self._viewFlags

    @property
    def view_setting(self):
        return self._viewSetting

    @property
    def common_properties(self):
        """
        Return all common node properties.

        Returns:
            dict: common node properties.
                eg.
                    {'nodeGraphQt.nodes.FooNode': {
                        'my_property': {
                            'widget_type': 0,
                            'tab': 'Properties',
                            'items': ['foo', 'bar', 'test'],
                            'range': (0, 100)
                            }
                        }
                    }
        """
        return self.__common_node_props

    @common_properties.setter
    def common_properties(self, attrs: dict):
        """
        Store common node properties.

        Args:
            attrs (dict): common node properties.
                eg.
                    {'nodeGraphQt.nodes.FooNode': {
                        'my_property': {
                            'widget_type': 0,
                            'tab': 'Properties',
                            'items': ['foo', 'bar', 'test'],
                            'range': (0, 100)
                            }
                        }
                    }
        """
        for node_type in attrs.keys():
            _node_props = attrs[node_type]

            if node_type not in self.__common_node_props.keys():
                self.__common_node_props[node_type] = _node_props
                continue

            for prop_name, prop_attrs in _node_props.items():
                _common_props = self.__common_node_props[node_type]
                if prop_name not in _common_props.keys():
                    _common_props[prop_name] = prop_attrs
                    continue
                _common_props[prop_name].update(prop_attrs)

    def get_node_common_properties(self, node_type):
        """
        Return all the common properties for a registered node.

        Args:
            node_type (str): node type.

        Returns:
            dict: node common properties.
        """
        return self.__common_node_props.get(node_type)

    def on_insert_node(self, pipe, node_id, prev_node_pos):
        """
        Slot function triggered when a selected node has collided with a pipe.

        Args:
            pipe (Pipe): collided pipe item.
            node_id (str): selected node id to insert.
            prev_node_pos (dict): previous node position. {NodeItem: [prev_x, prev_y]}
        """
        # todo: check back
        _node = self.get_node_by_id(node_id)

        # exclude if not a BaseNode
        if not isinstance(_node, NodeObject):
            return
        _connected, _disconnected = pipe.on_node_insert(_node)
        self._undoStack.beginMacro('inserted node')
        self.on_connection_changed(_disconnected, _connected)
        self.on_nodes_moved(prev_node_pos)
        self._undoStack.endMacro()

    def on_property_bin_changed(self, node_id, prop_name, prop_value):
        """
        called when a property widget has changed in a properties bin.
        (emits the node object, property name, property value)

        Args:
            node_id (str): node id.
            prop_name (str): node property name.
            prop_value (object): python built in types.
        """
        _node = self.get_node_by_id(node_id)

        # prevent signals from causing an infinite loop.
        if _node.get_property(prop_name) != prop_value:
            _node.set_property(prop_name, prop_value)

    def on_node_label_changed(self, node_id, label):
        """
        called when a node text qgraphics item in the viewer is edited.
        (sets the name through the node object so undo commands are registered.)

        Args:
            node_id (str): node id emitted by the viewer.
            label (str): new node name.
        """
        _node = self.get_node_by_id(node_id)
        _node.view.set_property('label', label)

    def on_node_double_clicked(self, node_id):
        """
        called when a node in the viewer is double click.
        (emits the node object when the node is clicked)

        Args:
            node_id (str): node id emitted by the viewer.
        """
        _node = self.get_node_by_id(node_id)
        self.sigNodeDoubleClicked.emit(_node)

    def on_node_selected(self, node_id):
        """
        called when a node in the viewer is selected on left click.
        (emits the node object when the node is clicked)

        Args:
            node_id (str): node id emitted by the viewer.
        """
        _node = self.get_node_by_id(node_id)
        self.sigNodeSelected.emit(_node)

    def on_node_selection_changed(self, sel_ids, desel_ids):
        """
        called when the node selection changes in the viewer.
        (emits node objects <selected nodes>, <deselected nodes>)

        Args:
            sel_ids (list[str]): new selected node ids.
            desel_ids (list[str]): deselected node ids.
        """
        _sel_nodes = [self.get_node_by_id(nid) for nid in sel_ids]
        _unsel_nodes = [self.get_node_by_id(nid) for nid in desel_ids]
        self.sigNodeSelectionChanged.emit(_sel_nodes, _unsel_nodes)

    def on_node_data_dropped(self, data, pos):
        """
        called when data has been dropped on the viewer.

        Example Identifiers:
            URI = ngqt://path/to/node/session.graph
            URN = ngqt::node:com.nodes.MyNode1;node:com.nodes.MyNode2

        Args:
            data (QtCore.QMimeData): mime data.
            pos (QtCore.QPoint): scene position relative to the drop.
        """
        _uri_regex = re.compile(r'{}(?:/*)([\w/]+)(\.\w+)'.format(URI_SCHEME))
        _urn_regex = re.compile(r'{}([\w\.:;]+)'.format(URN_SCHEME))
        if data.hasFormat('text/uri-list'):
            for url in data.urls():
                _local_file = url.toLocalFile()
                if _local_file:
                    try:
                        self.import_session(_local_file)
                        continue
                    except Exception as e:
                        pass

                _url_str = url.toString()
                _uri_search = _uri_regex.search(_url_str)
                _urn_search = _urn_regex.search(_url_str)
                if _uri_search:
                    _path = _uri_search.group(1)
                    _ext = _uri_search.group(2)
                    self.import_session('{}{}'.format(_path, _ext))
                elif _urn_search:
                    _search_str = _urn_search.group(1)
                    _node_ids = sorted(re.findall('node:([\w\\.]+)', _search_str))
                    _x, _y = pos.x(), pos.y()
                    for node_id in _node_ids:
                        self.create_node(node_id, pos=[_x, _y])
                        _x += 80
                        _y += 80

    def on_nodes_moved(self, node_data):
        """
        called when selected nodes in the viewer has changed position.

        Args:
            node_data (dict): {<node_view>: <previous_pos>}
        """
        self._undoStack.beginMacro('move nodes')
        for node_view, prev_pos in node_data.items():
            _node = self.nodes[node_view.id]
            self._undoStack.push(NodeViewMovedCmd(_node, _node.view.xy_pos, prev_pos))
        self._undoStack.endMacro()

    # def on_node_backdrop_updated(self, node_id, update_property, value):
    #     """
    #     called when a BackdropNode is updated.
    #
    #     Args:
    #         node_id (str): backdrop node id.
    #         update_property (str): update type.
    #         value (str): update type.
    #     """
    #     _backdrop = self.get_node_by_id(node_id)
    #     if _backdrop and isinstance(_backdrop, BackdropNode):
    #         _backdrop.on_backdrop_updated(update_property, value)

    def on_search_triggered(self, node_type, pos):
        """
        called when the tab search widget is triggered in the viewer.

        Args:
            node_type (str): node identifier.
            pos (tuple or list): x, y position for the node.
        """
        self.create_node(node_type, pos=pos)

    def on_connection_changed(self, disconnected, connected):
        """
        called when a pipe connection has been changed in the viewer.

        Args:
            disconnected (list[list[widgets.port.PortItem]):
                pair list of port view items.
            connected (list[list[widgets.port.PortItem]]):
                pair list of port view items.
        """
        if not (disconnected or connected):
            return

        _label = 'connect node(s)' if connected else 'disconnect node(s)'
        # _ptypes = {EnumPortType.IN.value: 'get_inputs',
        #            EnumPortType.OUT.value: 'get_outputs'}

        self._undoStack.beginMacro(_label)
        # for p1_view, p2_view in disconnected:
        #     _node1 = self._model.nodes[p1_view.node.id]
        #     _node2 = self._model.nodes[p2_view.node.id]
        #     _port1 = getattr(_node1, _ptypes[p1_view.port_type])()[p1_view.name]
        #     _port2 = getattr(_node2, _ptypes[p2_view.port_type])()[p2_view.name]
        #     _port1.disconnect_from(_port2)
        # for p1_view, p2_view in connected:
        #     _node1 = self._model.nodes[p1_view.node.id]
        #     _node2 = self._model.nodes[p2_view.node.id]
        #     _port1 = getattr(_node1, _ptypes[p1_view.port_type])()[p1_view.name]
        #     _port2 = getattr(_node2, _ptypes[p2_view.port_type])()[p2_view.name]
        #     _port1.connect_to(_port2)
        self._undoStack.endMacro()

    def on_connection_sliced(self, ports):
        """
        slot when connection pipes have been sliced.

        Args:
            ports (list[list[widgets.port.PortItem]]):
                pair list of port connections (in port, out port)
        """
        if not ports:
            return
        # _ptypes = {EnumPortType.IN.value: 'get_inputs',
        #            EnumPortType.OUT.value: 'get_outputs'}
        self._undoStack.beginMacro('slice connections')
        # for p1_view, p2_view in ports:
        #     _node1 = self._model.nodes[p1_view.node.id]
        #     _node2 = self._model.nodes[p2_view.node.id]
        #     _port1 = getattr(_node1, _ptypes[p1_view.port_type])()[p1_view.name]
        #     _port2 = getattr(_node2, _ptypes[p2_view.port_type])()[p2_view.name]
        #     _port1.disconnect_from(_port2)
        self._undoStack.endMacro()

    @property
    def node_factory(self):
        """
        Return the node factory object used by the node graph.

        Returns:
            NodeFactory: node factory.
        """
        return self._nodeFactory

    @property
    def view_factory(self):
        return self._viewFactory

    @property
    def widget(self):
        """
        The node graph widget for adding into a layout.

        Returns:
            NodeGraphWidget: node graph widget.
        """
        if self._widget is None:
            self._widget = NodeGraphWidget()
            # todo: name in tab from graphName
            self._widget.addTab(self._view, 'Node Graph')
            # hide the close button on the first tab.
            _tab_bar = self._widget.tabBar()
            for btn_flag in [_tab_bar.ButtonPosition.RightSide, _tab_bar.ButtonPosition.LeftSide]:
                _tab_btn = _tab_bar.tabButton(0, btn_flag)
                if _tab_btn:
                    _tab_btn.deleteLater()
                    _tab_bar.setTabButton(0, btn_flag, None)
            self._widget.tabCloseRequested.connect(self._on_close_sub_graph_request)
        return self._widget

    @property
    def undo_view(self):
        """
        Returns node graph undo history list widget.

        Returns:
            PySide2.QtWidgets.QUndoView: node graph undo view.
        """
        if self._undoView is None:
            self._undoView = QtWidgets.QUndoView(self._undoStack)
            self._undoView.setWindowTitle('Undo History')
        return self._undoView

    def toggle_node_search(self):
        """
        toggle the node search widget visibility.
        """
        _cursor_pos = self._view.mapFromGlobal(QtGui.QCursor.pos())
        if self._view.underMouse() or self._view.contentsRect().contains(_cursor_pos):
            self._view.tab_search_set_nodes(self._nodeFactory.grouped)
            self._view.tab_search_toggle()

    def show(self):
        """
        Show node graph widget this is just a convenience
        function to :meth:`NodeGraph.widget.show()`.
        """
        self._view.show()

    def close(self):
        """
        Close node graph NodeViewer widget this is just a convenience
        function to :meth:`NodeGraph.widget.close()`.
        """
        self._view.close()

    def get_view(self):
        """
        Returns the internal view interface used by the node graph.

        Warnings:
            Methods in the ``NodeViewer`` are used internally
            by ``NodeGraphQt`` components to get the widget use
            :attr:`NodeGraph.widget`.

        See Also:
            :attr:`NodeGraph.widget` to add the node graph widget into a
            :class:`PySide2.QtWidgets.QLayout`.

        Returns:
            NodeGraphQt.widgets.viewer.NodeViewer: viewer interface.
        """
        return self._view

    def get_scene(self):
        """
        Returns the ``QGraphicsScene`` object used in the node graph.

        Returns:
            NodeGraphQt.widgets.scene.NodeScene: node scene.
        """
        return self._view.scene()

    def get_background_color(self):
        """
        Return the node graph background color.

        Returns:
            tuple: r, g ,b
        """
        return self.get_scene().background_color

    def set_background_color(self, r, g, b):
        """
        Set node graph background color.

        Args:
            r (int): red value.
            g (int): green value.
            b (int): blue value.
        """
        self.get_scene().background_color = (r, g, b)
        self._view.force_update()

    def get_grid_color(self):
        """
        Return the node graph grid color.

        Returns:
            tuple: r, g ,b
        """
        return self.get_scene().grid_color

    def set_grid_color(self, r, g, b):
        """
        Set node graph grid color.

        Args:
            r (int): red value.
            g (int): green value.
            b (int): blue value.
        """
        self.get_scene().grid_color = (r, g, b)
        self._view.force_update()

    def set_grid_mode(self, flag):
        """
        Set node graph grid mode.

        Note:
            By default grid mode is set to "VIEWER_GRID_LINES".

            Node graph background types:

            * :attr:`NodeGraphQt.constants.ViewerEnum.GRID_DISPLAY_NONE.value`
            * :attr:`NodeGraphQt.constants.ViewerEnum.GRID_DISPLAY_DOTS.value`
            * :attr:`NodeGraphQt.constants.ViewerEnum.GRID_DISPLAY_LINES.value`

        Args:
            flag (int): background style.
        """
        if flag not in [EnumGraphViewFlag.SHOW_GRID_NONE, EnumGraphViewFlag.SHOW_DOT_GRID, EnumGraphViewFlag.SHOW_LINE_GRID]:
            return
        if flag == self.has_flag(self._viewFlags, flag):
            return
        self.set_flag(self._viewFlags, flag, True)
        self._view.force_update()

    def add_properties_bin(self, prop_bin):
        """
        Wire up a properties bin widget to the node graph.

        Args:
            prop_bin (NodeGraphQt.PropertiesBinWidget): properties widget.
        """
        prop_bin.property_changed.connect(self.on_property_bin_changed)

    def get_undo_stack(self):
        """
        Returns the undo stack used in the node graph.

        See Also:
            :meth:`NodeGraph.begin_undo()`,
            :meth:`NodeGraph.end_undo()`

        Returns:
            QtWidgets.QUndoStack: undo stack.
        """
        return self._undoStack

    def clear_undo_stack(self):
        """
        Clears the undo stack.

        Note:
            Convenience function to
            :meth:`NodeGraph.undo_stack().clear()`

        See Also:
            :meth:`NodeGraph.begin_undo()`,
            :meth:`NodeGraph.end_undo()`,
            :meth:`NodeGraph.undo_stack()`
        """
        self._undoStack.clear()

    def begin_undo(self, name):
        """
        Start of an undo block followed by a
        :meth:`NodeGraph.end_undo()`.

        Args:
            name (str): name for the undo block.
        """
        self._undoStack.beginMacro(name)

    def end_undo(self):
        """
        End of an undo block started by
        :meth:`NodeGraph.begin_undo()`.
        """
        self._undoStack.endMacro()

    def get_graph_context_menu(self):
        """
        Returns the context menu for the node graph.

        Note:
            This is a convenience function to
            :meth:`NodeGraph.get_context_menu`
            with the arg ``menu="graph"``

        Returns:
            NodeGraphQt.NodeGraphMenu: context menu object.
        """
        return self.get_context_menu('graph')

    def get_context_nodes_menu(self):
        """
        Returns the context menu for the nodes.

        Note:
            This is a convenience function to
            :meth:`NodeGraph.get_context_menu`
            with the arg ``menu="nodes"``

        Returns:
            NodeGraphQt.NodesMenu: context menu object.
        """
        return self.get_context_menu('nodes')

    def get_context_menu(self, menu):
        """
        Returns the context menu specified by the name.

        Menu Types:
            - ``"graph"`` context menu from the node graph.
            - ``"nodes"`` context menu for the nodes.

        Args:
            menu (str): menu name.

        Returns:
            NodeGraphQt.NodeGraphMenu or NodeGraphQt.NodesMenu: context menu object.
        """
        return self._contextMenu.get(menu)

    def _deserialize_context_menu(self, menu, menu_data):
        """
        Populate context menu from a dictionary.

        Args:
            menu (NodeGraphQt.NodeGraphMenu or NodeGraphQt.NodesMenu):
                parent context menu.
            menu_data (list[dict] or dict): serialized menu data.
        """
        if not menu:
            raise ValueError('No context menu named: "{}"'.format(menu))

        import sys
        import importlib.util

        _nodes_menu = self.get_context_menu('nodes')

        def build_menu_command(menu, data):
            """
            Create menu command from serialized data.

            Args:
                menu (NodeGraphQt.NodeGraphMenu or NodeGraphQt.NodesMenu):
                    menu object.
                data (dict): serialized menu command data.
            """
            _full_path = os.path.abspath(data['file'])
            _base_dir, _file_name = os.path.split(_full_path)
            _base_name = os.path.basename(_base_dir)
            _file_name, _ = _file_name.split('.')

            _mod_name = '{}.{}'.format(_base_name, _file_name)

            _spec = importlib.util.spec_from_file_location(_mod_name, _full_path)
            _mod = importlib.util.module_from_spec(_spec)
            sys.modules[_mod_name] = _mod
            _spec.loader.exec_module(_mod)

            _cmd_func = getattr(_mod, data['function_name'])
            _cmd_name = data.get('label') or '<command>'
            _cmd_shortcut = data.get('shortcut')
            _cmd_kwargs = {'func': _cmd_func, 'shortcut': _cmd_shortcut}

            if menu == _nodes_menu and data.get('node_type'):
                _cmd_kwargs['node_type'] = data['node_type']

            menu.add_command(name=_cmd_name, **_cmd_kwargs)

        if isinstance(menu_data, dict):
            _item_type = menu_data.get('type')
            if _item_type == 'separator':
                menu.add_separator()
            elif _item_type == 'command':
                build_menu_command(menu, menu_data)
            elif _item_type == 'menu':
                _sub_menu = menu.add_menu(menu_data['label'])
                _items = menu_data.get('items', [])
                self._deserialize_context_menu(_sub_menu, _items)
        elif isinstance(menu_data, list):
            for item_data in menu_data:
                self._deserialize_context_menu(menu, item_data)

    def set_context_menu(self, menu_name, data):
        """
        Populate a context menu from serialized data.

        example of serialized menu data:

        .. highlight:: python
        .. code-block:: python

            [
                {
                    'type': 'menu',
                    'label': 'test sub menu',
                    'items': [
                        {
                            'type': 'command',
                            'label': 'test command',
                            'file': '../path/to/my/test_module.py',
                            'function': 'run_test',
                            'shortcut': 'Ctrl+b',
                            'node_type': 'nodeGraphQt.nodes.MyNodeClass'
                        },

                    ]
                },
            ]

        the ``run_test`` example function:

        .. highlight:: python
        .. code-block:: python

            def run_test(graph):
                print(graph.selected_nodes())


        Args:
            menu_name (str): name of the parent context menu to populate under.
            data (dict): serialized menu data.
        """
        _context_menu = self.get_context_menu(menu_name)
        self._deserialize_context_menu(_context_menu, data)

    def set_context_menu_from_file(self, file_path, menu=None):
        """
        Populate a context menu from a serialized json file.

        menu types:

            - ``"graph"`` context menu from the node graph.
            - ``"nodes"`` context menu for the nodes.

        Args:
            menu (str): name of the parent context menu to populate under.
            file_path (str): serialized menu commands json file.
        """
        file_path = os.path.abspath(file_path)

        menu = menu or 'graph'
        if not os.path.isfile(file_path):
            raise IOError('file doesn\'t exists: "{}"'.format(file_path))

        with open(file_path) as f:
            _data = json.load(f)
        _context_menu = self.get_context_menu(menu)
        self._deserialize_context_menu(_context_menu, _data)

    def disable_context_menu(self, disabled=True, name='all'):
        """
        Disable/Enable context menus from the node graph.

        Menu Types:
            - ``"all"`` all context menus from the node graph.
            - ``"graph"`` context menu from the node graph.
            - ``"nodes"`` context menu for the nodes.

        Args:
            disabled (bool): true to enable context menu.
            name (str): menu name. (default: ``"all"``)
        """
        if name == 'all':
            for k, menu in self._view.get_context_menus().items():
                menu.setDisabled(disabled)
                menu.setVisible(not disabled)
            return
        _menus = self._view.get_context_menus()
        if _menus.get(name):
            _menus[name].setDisabled(disabled)
            _menus[name].setVisible(not disabled)

    @property
    def is_acyclic(self):
        """
        Returns true if the current node graph is acyclic.

        See Also:
            :meth:`NodeGraph.set_acyclic`

        Returns:
            bool: true if acyclic (default: ``True``).
        """
        return self.has_flag(self.flags, EnumGraphFlag.ACYCLIC)

    def set_acyclic(self, mode=False):
        """
        Enable the node graph to be a acyclic graph. (default: ``False``)

        See Also:
            :meth:`NodeGraph.acyclic`

        Args:
            mode (bool): true to enable acyclic.
        """
        self.set_flag(self.flags, EnumGraphFlag.ACYCLIC, mode)

    @property
    def is_pipe_collision_enabled(self):
        """
        Returns if pipe collision is enabled.

        See Also:
            To enable/disable pipe collision
            :meth:`NodeGraph.set_pipe_collision`

        Returns:
            bool: True if pipe collision is enabled.
        """
        return self.has_flag(self._viewFlags, EnumGraphViewFlag.PIPE_COLLISION)

    def set_pipe_collision(self, mode=True):
        """
        Enable/Disable pipe collision.

        When enabled dragging a node over a pipe will allow the node to be
        inserted as a new connection between the pipe.

        See Also:
            :meth:`NodeGraph.pipe_collision`

        Args:
            mode (bool): False to disable pipe collision.
        """
        self.set_flag(self._viewFlags, EnumGraphViewFlag.PIPE_COLLISION, mode)

    def set_pipe_style(self, style_flag=EnumPipeShapeStyle.CURVED):
        """
        Set node graph pipes to be drawn as straight, curved or angled.

        .. image:: _images/pipe_layout_types.gif
            :width: 80%

        Note:
            By default pipe layout is set to "PIPE_LAYOUT_CURVED".

        Args:
            style_flag (int): pipe layout style.
        """
        if style_flag not in EnumPipeShapeStyle:
            return

        self._view.set_pipe_shape_style(style_flag)

    @property
    def layout_direction(self):
        """
        Return the current node graph layout direction.

        `Implemented in` ``v0.3.0``

        See Also:
            :meth:`NodeGraph.set_layout_direction`

        Returns:
            int: layout direction.
        """
        return self._layoutDirection

    @layout_direction.setter
    def layout_direction(self, direction):
        """
        Sets the node graph layout direction to horizontal or vertical.
        This function will also override the layout direction on all
        nodes in the current node graph.

        `Implemented in` ``v0.3.0``

        See Also:
            :meth:`NodeGraph.layout_direction`,
            :meth:`NodeObject.set_layout_direction`

        Note:
            Node Graph Layout Types:

            * :attr:`NodeGraphQt.constants.LayoutDirectionEnum.HORIZONTAL`
            * :attr:`NodeGraphQt.constants.LayoutDirectionEnum.VERTICAL`

            .. image:: _images/layout_direction_switch.gif
                :width: 300px

        Warnings:
            This function does not register to the undo stack.

        Args:
            direction (int): layout direction.
        """
        _direction_types = [e.value for e in EnumLayoutDirection]
        if direction not in _direction_types:
            direction = EnumLayoutDirection.HORIZONTAL.value
        for node in self.get_all_nodes():
            node.set_layout_direction(direction)
        self._view.set_layout_direction(direction)

    def fit_to_selection(self):
        """
        Sets the zoom level to fit selected nodes.
        If no nodes are selected then all nodes in the graph will be framed.
        """
        _nodes = self.get_selected_nodes() or self.get_all_nodes()
        if not _nodes:
            return
        self._view.zoom_to_nodes([n.view for n in _nodes])

    def reset_zoom(self):
        """
        Reset the zoom level
        """
        self._view.reset_zoom()

    def set_zoom(self, zoom=0):
        """
        Set the zoom factor of the Node Graph the default is ``0.0``

        Args:
            zoom (float): zoom factor (max zoom out ``-0.9`` / max zoom in ``2.0``)
        """
        self._view.set_zoom(zoom)

    def get_zoom(self):
        """
        Get the current zoom level of the node graph.

        Returns:
            float: the current zoom level.
        """
        return self._view.get_zoom()

    def set_center_on(self, nodes=None):
        """
        Center the node graph on the given nodes or all nodes by default.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): a list of nodes.
        """
        _nodes = nodes or []
        self._view.center_selection([n.view for n in nodes])

    def get_center_selection(self):
        """
        Centers on the current selected nodes.
        """
        _nodes = self._view.get_selected_nodes()
        self._view.center_selection(_nodes)

    def get_registered_nodes(self):
        """
        Return a list of all node types that have been registered.

        See Also:
            To register a node :meth:`NodeGraph.register_node`

        Returns:
            list[str]: list of node type identifiers.
        """
        return sorted(self._nodeFactory.nodes.keys())

    def register_node(self, node, alias=None):
        """
        Register the node to the :meth:`NodeGraph.node_factory`

        Args:
            node (NodeGraphQt.NodeObject): node object.
            alias (str): custom alias name for the node type.
        """
        self._nodeFactory.register_node(node, alias)
        self._view.rebuild_tab_search()
        self.sigNodesRegistered.emit([node])

    def register_nodes(self, nodes):
        """
        Register the nodes to the :meth:`NodeGraph.node_factory`

        Args:
            nodes (list): list of nodes.
        """
        [self._nodeFactory.register_node(n) for n in nodes]
        self._view.rebuild_tab_search()
        self.sigNodesRegistered.emit(nodes)

    def create_node(self, node_type, push_undo=True, **kwargs):
        """
        Create a new node in the node graph.

        See Also:
            To list all node types :meth:`NodeGraph.registered_nodes`

        Args:
            node_type (str): node instance type.
            kwargs:
                name (str): set name of the node.
                selected (bool): set created node to be selected.
                color (tuple or str): node color ``(255, 255, 255)`` or ``"#FFFFFF"``.
                text_color (tuple or str): text color ``(255, 255, 255)`` or ``"#FFFFFF"``.
                pos (list[int, int]): initial x, y position for the node (default: ``(0, 0)``).
            push_undo (bool): register the command to the undo stack. (default: True)

        Returns:
            BaseNode: the created instance of the node.
        """
        _node: NodeObject = self._nodeFactory.create_class_instance(node_type)
        if _node:
            _node.graph = self
            _node_props = _node.view.properties
            # _wid_types = _node.model.__dict__.pop('_TEMP_property_widget_types')
            # _prop_attrs = _node.model.__dict__.pop('_TEMP_property_attrs')

            # if self.get_node_common_properties(_node.type_) is None:
            #     _node_attrs = {_node.type_: {
            #         attr: {'widget_type': pp.widgetType} for attr, pp in _node_props.items()
            #     }}
            #     # for pname, pattrs in _prop_attrs.items():
            #     #     _node_attrs[_node.type_][pname].update(pattrs)
            #     self.set_node_common_properties(_node_attrs)

            # _node.NODE_NAME = self.get_unique_name(name or _node.NODE_NAME)
            # _node.model.name = _node.NODE_NAME
            kwargs.update({'layout_direction': self.layout_direction})
            _node.view.update_properties_with(**kwargs)
            # _node_model.selected=selected
            #
            # def format_color(clr):
            #     if isinstance(clr, str):
            #         clr = clr.strip('#')
            #         return tuple(int(clr[i:i + 2], 16) for i in (0, 2, 4))
            #     return clr
            #
            # if color:
            #     _node_model.color = format_color(color)
            # if text_color:
            #     _node_model.textColor = format_color(text_color)
            # if pos:
            #     _node_model.pos = [float(pos[0]), float(pos[1])]

            # initial node direction layout.
            # _node_model.layoutDirection = self.p_layout_direction

            # _node.update()

            _undo_cmd = NodeViewAddedCmd(self, _node, _node.view.pos())
            if push_undo:
                _undo_label = 'create node: "{}"'.format(_node.type_)
                self._undoStack.beginMacro(_undo_label)
                for n in self.get_selected_nodes():
                    n.set_property('selected', False, push_undo=True)
                self._undoStack.push(_undo_cmd)
                self._undoStack.endMacro()
            else:
                for n in self.get_selected_nodes():
                    n.set_property('selected', False, push_undo=False)
                NodeViewAddedCmd(self, _node, _node.view.pos()).redo()

            self.sigNodeCreated.emit(_node)
            return _node
        raise NodeCreationError('Can\'t find node: "{}"'.format(node_type))

    def add_node(self, node: NodeObject, pos=None, selected=True, push_undo=True):
        """
        Add a node into the node graph.
        unlike the :meth:`NodeGraph.create_node` function this will not
        trigger the :attr:`NodeGraph.node_created` signal.

        Args:
            node (NodeGraphQt.BaseNode): node object.
            pos (list[float]): node x,y position. (optional)
            selected (bool): node selected state. (optional)
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        assert isinstance(node, NodeObject), 'node must be a Node instance.'
        _node_props = node.properties

        if self.get_node_common_properties(node.type_) is None:
            _node_attrs = {node.type_: {
                attr: {'widget_type': pp.widgetType} for attr, pp in _node_props.items()
            }}
            # for pname, pattrs in _prop_attrs.items():
            #     _node_attrs[_node.type_][pname].update(pattrs)
            self.set_node_common_properties(_node_attrs)

        # node._graph = self
        # node.NODE_NAME = self.get_unique_name(node.NODE_NAME)
        # node.p_model._graph_model = self._model
        # node.p_model.name = node.NODE_NAME
        node.graph = self

        _kwargs = dict()
        _kwargs.update({'layout_direction': self.layout_direction})
        node.update_properties_with(**_kwargs)

        if push_undo:
            self._undoStack.beginMacro('add node: "{}"'.format(node.type_))
            self._undoStack.push(NodeViewAddedCmd(self, node, pos))
            if selected:
                node.selected = True
            self._undoStack.endMacro()
        else:
            NodeViewAddedCmd(self, node, pos).redo()

    def delete_node(self, node, push_undo=True):
        """
        Remove the node from the node graph.
        Args:
            node (NodeGraphQt.BaseNode): node object.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        assert isinstance(node, NodeObject), \
            'node must be a instance of a NodeObject.'
        _node_id = node.id
        if push_undo:
            self._undoStack.beginMacro('delete node: "{}"'.format(node.type_))
        if isinstance(node, NodeObject):
            node.on_delete()
            # for p in node.get_input_ports():
            #     if p.is_locked():
            #         p.set_locked(False,
            #                      connected_ports=False,
            #                      push_undo=push_undo)
            #     p.clear_connections(push_undo=push_undo)
            # for p in node.get_output_ports():
            #     if p.is_locked():
            #         p.set_locked(False,
            #                      connected_ports=False,
            #                      push_undo=push_undo)
            #     p.clear_connections(push_undo=push_undo)
        # collapse group node before removing.
        # if isinstance(node, GroupNode) and node.is_expanded:
        #     node.collapse()
        if push_undo:
            self._undoStack.push(NodeViewRemovedCmd(self, node))
            self._undoStack.endMacro()
        else:
            NodeViewRemovedCmd(self, node).redo()
        self.sigNodesDeleted.emit([_node_id])

    def remove_node(self, node, push_undo=True):
        """
        Remove the node from the node graph.

        unlike the :meth:`NodeGraph.delete_node` function this will not
        trigger the :attr:`NodeGraph.nodes_deleted` signal.

        Args:
            node (NodeGraphQt.BaseNode): node object.
            push_undo (bool): register the command to the undo stack. (default: True)

        """
        assert isinstance(node, NodeObject), 'node must be a Node instance.'

        if push_undo:
            self._undoStack.beginMacro('delete node: "{}"'.format(node.type_))

        # collapse group node before removing.
        node.on_remove()
        # if isinstance(node, GroupNode) and node.is_expanded:
        #     node.collapse()
        #
        # if isinstance(node, BaseNode):
        #     for p in node.get_input_ports():
        #         if p.locked():
        #             p.set_locked(False,
        #                          connected_ports=False,
        #                          push_undo=push_undo)
        #         p.clear_connections(push_undo=push_undo)
        #     for p in node.get_output_ports():
        #         if p.locked():
        #             p.set_locked(False,
        #                          connected_ports=False,
        #                          push_undo=push_undo)
        #         p.clear_connections(push_undo=push_undo)

        if push_undo:
            self._undoStack.push(NodeViewRemovedCmd(self, node))
            self._undoStack.endMacro()
        else:
            NodeViewRemovedCmd(self, node).redo()

    def delete_nodes(self, nodes, push_undo=True):
        """
        Remove a list of specified nodes from the node graph.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of node instances.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if not nodes:
            return
        if len(nodes) == 1:
            self.delete_node(nodes[0], push_undo=push_undo)
            return
        _node_ids = [n.id for n in nodes]
        if push_undo:
            self._undoStack.beginMacro('deleted "{}" nodes'.format(len(nodes)))
        for node in nodes:
            node.on_delete()
            # # collapse group node before removing.
            # if isinstance(node, GroupNode) and node.is_expanded:
            #     node.collapse()
            #
            # if isinstance(node, BaseNode):
            #     for p in node.get_input_ports():
            #         if p.locked():
            #             p.set_locked(False,
            #                          connected_ports=False,
            #                          push_undo=push_undo)
            #         p.clear_connections(push_undo=push_undo)
            #     for p in node.get_output_ports():
            #         if p.locked():
            #             p.set_locked(False,
            #                          connected_ports=False,
            #                          push_undo=push_undo)
            #         p.clear_connections(push_undo=push_undo)
            if push_undo:
                self._undoStack.push(NodeViewRemovedCmd(self, node))
            else:
                NodeViewRemovedCmd(self, node).redo()
        if push_undo:
            self._undoStack.endMacro()
        self.sigNodesDeleted.emit(_node_ids)

    def get_all_nodes(self):
        """
        Return all nodes in the node graph.

        Returns:
            list[NodeGraphQt.BaseNode]: list of nodes.
        """
        return list(self.nodes.values())

    def get_selected_nodes(self):
        """
        Return all selected nodes that are in the node graph.

        Returns:
            list[NodeGraphQt.BaseNode]: list of nodes.
        """
        _nodes = []
        for item in self._view.get_selected_items():
            _node = self.nodes[item.id]
            _nodes.append(_node)
        return _nodes

    def select_all(self):
        """
        Select all nodes in the node graph.
        """
        self._undoStack.beginMacro('select all')
        [node.set_selected(True) for node in self.get_all_nodes()]
        self._undoStack.endMacro()

    def clear_selection(self):
        """
        Clears the selection in the node graph.
        """
        self._undoStack.beginMacro('clear selection')
        [node.set_selected(False) for node in self.get_all_nodes()]
        self._undoStack.endMacro()

    def get_node_by_id(self, node_id=None):
        """
        Returns the node from the node id string.

        Args:
            node_id (str): node id (:attr:`NodeObject.id`)

        Returns:
            NodeGraphQt.NodeObject: node object.
        """
        return self.nodes.get(node_id, None)

    def get_node_by_name(self, name):
        """
        Returns node that matches the name.

        Args:
            name (str): name of the node.
        Returns:
            NodeGraphQt.NodeObject: node object.
        """
        for node_id, node in self.nodes.items():
            if node.get_name() == name:
                return node

    def get_nodes_by_type(self, node_type):
        """
        Return all nodes by their node type identifier.
        (see: :attr:`NodeGraphQt.NodeObject.type_`)

        Args:
            node_type (str): node type identifier.

        Returns:
            list[NodeGraphQt.NodeObject]: list of nodes.
        """
        return [n for n in self.nodes.values() if n.type_ == node_type]

    def get_unique_name(self, name):
        """
        Creates a unique node name to avoid having nodes with the same name.

        Args:
            name (str): node name.

        Returns:
            str: unique node name.
        """
        name = ' '.join(name.split())
        _node_names = [n.get_name() for n in self.get_all_nodes()]
        if name not in _node_names:
            return name

        _regex = re.compile(r'\w+ (\d+)$')
        _search = _regex.search(name)
        if not _search:
            for x in range(1, len(_node_names) + 2):
                _new_name = '{} {}'.format(name, x)
                if _new_name not in _node_names:
                    return _new_name

        _version = _search.group(1)
        name = name[:len(_version) * -1].strip()
        for x in range(1, len(_node_names) + 2):
            _new_name = '{} {}'.format(name, x)
            if _new_name not in _node_names:
                return _new_name

    def get_current_session(self):
        """
        Returns the file path to the currently loaded session.

        Returns:
            str: path to the currently loaded session
        """
        return self.session

    def clear_session(self):
        """
        Clears the current node graph session.
        """
        for n in self.get_all_nodes():
            if isinstance(n, NodeObject):
                n.on_clear_session()
                # for p in n.get_input_ports():
                #     if p.is_locked():
                #         p.set_locked(False, connected_ports=False)
                #     p.clear_connections()
                # for p in n.get_output_ports():
                #     if p.is_locked():
                #         p.set_locked(False, connected_ports=False)
                #     p.clear_connections()
            self._undoStack.push(NodeViewRemovedCmd(self, n))
        self._undoStack.clear()

    # def _serialize(self, nodes):
    #     """
    #     serialize nodes to a dict.
    #     (used internally by the node graph)
    #
    #     Args:
    #         nodes (list[NodeGraphQt.Nodes]): list of node instances.
    #
    #     Returns:
    #         dict: serialized data.
    #     """
    #     _serial_data = {'graph': {}, 'nodes': {}, 'connections': []}
    #     _nodes_data = {}
    #
    #     # serialize graph session.
    #     _serial_data['graph']['acyclic'] = self.is_acyclic()
    #     _serial_data['graph']['pipe_collision'] = self.is_pipe_collision_enabled()
    #
    #     # serialize nodes.
    #     for n in nodes:
    #         # update the node model.
    #         n.update_model()
    #
    #         _node_dict = n.model.to_dict
    #         _nodes_data.update(_node_dict)
    #
    #     for n_id, n_data in _nodes_data.items():
    #         _serial_data['nodes'][n_id] = n_data
    #
    #         # serialize connections
    #         _inputs = n_data.pop('inputs') if n_data.get('inputs') else {}
    #         _outputs = n_data.pop('outputs') if n_data.get('outputs') else {}
    #
    #         for pname, conn_data in _inputs.items():
    #             for conn_id, prt_names in conn_data.items():
    #                 for conn_prt in prt_names:
    #                     _pipe = {
    #                         EnumPortType.IN.value: [n_id, pname],
    #                         EnumPortType.OUT.value: [conn_id, conn_prt]
    #                     }
    #                     if _pipe not in _serial_data['connections']:
    #                         _serial_data['connections'].append(_pipe)
    #
    #         for pname, conn_data in _outputs.items():
    #             for conn_id, prt_names in conn_data.items():
    #                 for conn_prt in prt_names:
    #                     _pipe = {
    #                         EnumPortType.OUT.value: [n_id, pname],
    #                         EnumPortType.IN.value: [conn_id, conn_prt]
    #                     }
    #                     if _pipe not in _serial_data['connections']:
    #                         _serial_data['connections'].append(_pipe)
    #
    #     if not _serial_data['connections']:
    #         _serial_data.pop('connections')
    #
    #     return _serial_data
    #
    # def _deserialize(self, data, relative_pos=False, pos=None):
    #     """
    #     deserialize node data.
    #     (used internally by the node graph)
    #
    #     Args:
    #         data (dict): node data.
    #         relative_pos (bool): position node relative to the cursor.
    #         pos (tuple or list): custom x, y position.
    #
    #     Returns:
    #         list[NodeGraphQt.Nodes]: list of node instances.
    #     """
    #     # update node graph properties.
    #     for attr_name, attr_value in data.get('graph', {}).items():
    #         if attr_name == 'acyclic':
    #             self.set_acyclic(attr_value)
    #         elif attr_name == 'pipe_collision':
    #             self.set_pipe_collision(attr_value)
    #
    #     # build the nodes.
    #     _nodes = {}
    #     for n_id, n_data in data.get('nodes', {}).items():
    #         _identifier = n_data['type_']
    #         _node = self._nodeFactory.create_node_instance(_identifier)
    #         if _node:
    #             _node.NODE_NAME = n_data.get('name', _node.NODE_NAME)
    #             # set properties.
    #             for prop in _node.model.properties.keys():
    #                 if prop in n_data.keys():
    #                     _node.model.set_property(prop, n_data[prop])
    #             # set custom properties.
    #             for prop, val in n_data.get('custom', {}).items():
    #                 _node.model.set_property(prop, val)
    #                 if isinstance(_node, BaseNode):
    #                     if prop in _node.view.widgets:
    #                         _node.view.widgets[prop].set_value(val)
    #
    #             _nodes[n_id] = _node
    #             self.add_node(_node, n_data.get('pos'))
    #
    #             if n_data.get('port_deletion_allowed', None):
    #                 _node.set_ports({
    #                     'input_ports': n_data['input_ports'],
    #                     'output_ports': n_data['output_ports']
    #                 })
    #
    #     # build the connections.
    #     for connection in data.get('connections', []):
    #         _nid, _pname = connection.get('in', ('', ''))
    #         _in_node = _nodes.get(_nid) or self.get_node_by_id(_nid)
    #         if not _in_node:
    #             continue
    #         _in_port = _in_node.get_inputs().get(_pname) if _in_node else None
    #
    #         _nid, _pname = connection.get('out', ('', ''))
    #         _out_node = _nodes.get(_nid) or self.get_node_by_id(_nid)
    #         if not _out_node:
    #             continue
    #         _out_port = _out_node.get_outputs().get(_pname) if _out_node else None
    #
    #         if _in_port and _out_port:
    #             # only connect if input port is not connected yet or input port
    #             # can have multiple connections.
    #             # important when duplicating nodes.
    #             _allow_connection = any([not _in_port.model.connectedPorts,
    #                                      _in_port.model.multiConnection])
    #             if _allow_connection:
    #                 self._undoStack.push(PortConnectedCmd(_in_port, _out_port))
    #
    #     _node_objs = _nodes.values()
    #     if relative_pos:
    #         self._view.move_nodes([n.view for n in _node_objs])
    #         [setattr(n.model, 'pos', n.view.xy_pos) for n in _node_objs]
    #     elif pos:
    #         self._view.move_nodes([n.view for n in _node_objs], pos=pos)
    #         [setattr(n.model, 'pos', n.view.xy_pos) for n in _node_objs]
    #
    #     return _node_objs

    # def serialize_session(self):
    #     """
    #     Serializes the current node graph layout to a dictionary.
    #
    #     See Also:
    #         :meth:`NodeGraph.deserialize_session`,
    #         :meth:`NodeGraph.save_session`,
    #         :meth:`NodeGraph.load_session`
    #
    #     Returns:
    #         dict: serialized session of the current node layout.
    #     """
    #     return self._serialize(self.get_all_nodes())
    #
    # def deserialize_session(self, layout_data):
    #     """
    #     Load node graph session from a dictionary object.
    #
    #     See Also:
    #         :meth:`NodeGraph.serialize_session`,
    #         :meth:`NodeGraph.load_session`,
    #         :meth:`NodeGraph.save_session`
    #
    #     Args:
    #         layout_data (dict): dictionary object containing a node session.
    #     """
    #     self.clear_session()
    #     self._deserialize(layout_data)
    #     self.clear_selection()
    #     self._undoStack.clear()

    def save_session(self, file_path):
        """
        Saves the current node graph session layout to a `JSON` formatted file.

        See Also:
            :meth:`NodeGraph.serialize_session`,
            :meth:`NodeGraph.deserialize_session`,
            :meth:`NodeGraph.load_session`,

        Args:
            file_path (str): path to the saved node layout.
        """
        import yaml

        # _serialized_data = self._serialize(self.get_all_nodes())
        _file_path = file_path.strip()
        with open(file_path, 'w') as file_out:
            # json.dump(
            #     _serialized_data,
            #     file_out,
            #     indent=2,
            #     separators=(',', ':')
            # )
            yaml.dump(self.serializer, file_out, yaml.CDumper)

    def load_session(self, file_path):
        """
        Load node graph session layout file.

        See Also:
            :meth:`NodeGraph.deserialize_session`,
            :meth:`NodeGraph.serialize_session`,
            :meth:`NodeGraph.save_session`

        Args:
            file_path (str): path to the serialized layout file.
        """
        file_path = file_path.strip()
        if not os.path.isfile(file_path):
            raise IOError('file does not exist: {}'.format(file_path))

        self.clear_session()
        self.import_session(file_path)

    def import_session(self, file_path):
        """
        Import node graph session layout file.

        Args:
            file_path (str): path to the serialized layout file.
        """
        import yaml
        file_path = file_path.strip()
        if not os.path.isfile(file_path):
            raise IOError('file does not exist: {}'.format(file_path))
        with open(file_path) as data_file:
            _layout_data =yaml.load(data_file,Loader=yaml.CFullLoader)
            print(_layout_data)
        # try:
        #     from gui.node_graph.core.class_node_graph_view_setting import NodeGraphViewSetting
        #     with open(file_path) as data_file:
        #         _layout_data =yaml.load(data_file,Loader=yaml.CFullLoader)
        #         print(_layout_data)
        #         #_layout_data = json.load(data_file)
        # except Exception as e:
        #     _layout_data = None
        #     print('Cannot read data from file.\n{}'.format(e))

        if not _layout_data:
            return

        self._deserialize(_layout_data)
        self._undoStack.clear()
        self.session = file_path

        self.sigSessionChanged.emit(file_path)

    def _deserialize(self, data):
        pass

    # def copy_nodes(self, nodes=None):
    #     """
    #     Copy nodes to the clipboard.
    #
    #     See Also:
    #         :meth:`NodeGraph.cut_nodes`
    #
    #     Args:
    #         nodes (list[NodeGraphQt.BaseNode]):
    #             list of nodes (default: selected nodes).
    #     """
    #     nodes = nodes or self.get_selected_nodes()
    #     if not nodes:
    #         return False
    #     _clipboard = QtWidgets.QApplication.clipboard()
    #     _serial_data = self._serialize(nodes)
    #     _serial_str = json.dumps(_serial_data)
    #     if _serial_str:
    #         _clipboard.setText(_serial_str)
    #         return True
    #     return False
    #
    # def cut_nodes(self, nodes=None):
    #     """
    #     Cut nodes to the clipboard.
    #
    #     Note:
    #         This function doesn't not trigger the
    #         :attr:`NodeGraph.nodes_deleted` signal.
    #
    #     See Also:
    #         :meth:`NodeGraph.copy_nodes`
    #
    #     Args:
    #         nodes (list[NodeGraphQt.BaseNode]):
    #             list of nodes (default: selected nodes).
    #     """
    #     nodes = nodes or self.get_selected_nodes()
    #     self.copy_nodes(nodes)
    #     self._undoStack.beginMacro('cut nodes')
    #
    #     for node in nodes:
    #         if isinstance(node, BaseNode):
    #             for p in node.get_input_ports():
    #                 if p.is_locked():
    #                     p.set_locked(False,
    #                                  connected_ports=False,
    #                                  push_undo=True)
    #                 p.clear_connections()
    #             for p in node.get_output_ports():
    #                 if p.is_locked():
    #                     p.set_locked(False,
    #                                  connected_ports=False,
    #                                  push_undo=True)
    #                 p.clear_connections()
    #
    #         # collapse group node before removing.
    #         if isinstance(node, GroupNode) and node.is_expanded:
    #             node.collapse()
    #
    #         self._undoStack.push(NodeRemovedCmd(self, node))
    #
    #     self._undoStack.endMacro()
    #
    # def paste_nodes(self):
    #     """
    #     Pastes nodes copied from the clipboard.
    #     """
    #     _clipboard = QtWidgets.QApplication.clipboard()
    #     _cb_text = _clipboard.text()
    #     if not _cb_text:
    #         return
    #
    #     try:
    #         _serial_data = json.loads(_cb_text)
    #     except json.decoder.JSONDecodeError as e:
    #         print('ERROR: Can\'t Decode Clipboard Data:\n'
    #               '"{}"'.format(_cb_text))
    #         return
    #
    #     self._undoStack.beginMacro('pasted nodes')
    #     self.clear_selection()
    #     nodes = self._deserialize(_serial_data, relative_pos=True)
    #     [n.set_selected(True) for n in nodes]
    #     self._undoStack.endMacro()
    #
    # def duplicate_nodes(self, nodes):
    #     """
    #     Create duplicate copy from the list of nodes.
    #
    #     Args:
    #         nodes (list[NodeGraphQt.BaseNode]): list of nodes.
    #     Returns:
    #         list[NodeGraphQt.BaseNode]: list of duplicated node instances.
    #     """
    #     if not nodes:
    #         return
    #     self._undoStack.beginMacro('duplicate nodes')
    #     self.clear_selection()
    #     _serial = self._serialize(nodes)
    #     _new_nodes = self._deserialize(_serial)
    #     _offset = 50
    #     for n in _new_nodes:
    #         _x, _y = n.get_pos()
    #         n.set_pos(_x + _offset, _y + _offset)
    #         n.set_property('selected', True)
    #     self._undoStack.endMacro()
    #     return _new_nodes

    def disable_nodes(self, nodes, mode=None):
        """
        Set weather to Disable or Enable specified nodes.

        See Also:
            :meth:`NodeObject.set_disabled`

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of node instances.
            mode (bool): (optional) disable state of the nodes.
        """
        if not nodes:
            return
        if mode is None:
            mode = not nodes[0].disabled
        if len(nodes) > 1:
            _text = {False: 'enable', True: 'disable'}[mode]
            _text = '{} ({}) nodes'.format(_text, len(nodes))
            self._undoStack.beginMacro(_text)
            for n in nodes:
                n.disabled = mode
            self._undoStack.endMacro()
            return
        nodes[0].disabled = mode

    def use_OpenGL(self):
        """
        Set the viewport to use QOpenGLWidget widget to draw the graph.
        """
        self._view.use_OpenGL()

    # auto layout node functions.
    # --------------------------------------------------------------------------

    @staticmethod
    def _update_node_rank(node, nodes_rank, down_stream=True):
        """
        Recursive function for updating the node ranking.

        Args:
            node (NodeGraphQt.BaseNode): node to start from.
            nodes_rank (dict): node ranking object to be updated.
            down_stream (bool): true to rank down stram.
        """
        if down_stream:
            _node_values = node.get_connected_output_nodes().values()
        else:
            _node_values = node.get_connected_input_nodes().values()

        _connected_nodes = set()
        for nodes in _node_values:
            _connected_nodes.update(nodes)

        _rank = nodes_rank[node] + 1
        for n in _connected_nodes:
            if n in nodes_rank:
                nodes_rank[n] = max(nodes_rank[n], _rank)
            else:
                nodes_rank[n] = _rank
            NodeGraph._update_node_rank(n, nodes_rank, down_stream)

    @staticmethod
    def _compute_node_rank(nodes, down_stream=True):
        """
        Compute the ranking of nodes.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): nodes to start ranking from.
            down_stream (bool): true to compute down stream.

        Returns:
            dict: {NodeGraphQt.BaseNode: node_rank, ...}
        """
        _nodes_rank = {}
        for node in nodes:
            _nodes_rank[node] = 0
            NodeGraph._update_node_rank(node, _nodes_rank, down_stream)
        return _nodes_rank

    def auto_layout_nodes(self, nodes=None, down_stream=True, start_nodes=None):
        """
        Auto layout the nodes in the node graph.

        Note:
            If the node graph is acyclic then the ``start_nodes`` will need
            to be specified.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of nodes to auto layout
                if nodes is None then all nodes is layed out.
            down_stream (bool): false to layout up stream.
            start_nodes (list[NodeGraphQt.BaseNode]):
                list of nodes to start the auto layout from (Optional).
        """
        self.begin_undo('Auto Layout Nodes')

        _nodes = nodes or self.get_all_nodes()

        # filter out the backdrops.
        _backdrops = {
            n: n.get_nodes() for n in nodes if isinstance(n, BackdropNode)
        }
        _filtered_nodes = [n for n in nodes if not isinstance(n, BackdropNode)]

        start_nodes = start_nodes or []
        if down_stream:
            start_nodes += [
                n for n in _filtered_nodes
                if not any(n.get_connected_input_nodes().values())
            ]
        else:
            start_nodes += [
                n for n in _filtered_nodes
                if not any(n.get_connected_output_nodes().values())
            ]

        if not start_nodes:
            return

        _node_views = [n.view for n in nodes]
        _nodes_center_0 = self.get_view().get_nodes_rect_center(_node_views)

        _nodes_rank = NodeGraph._compute_node_rank(start_nodes, down_stream)

        _rank_map = {}
        for node, rank in _nodes_rank.items():
            if rank in _rank_map:
                _rank_map[rank].append(node)
            else:
                _rank_map[rank] = [node]

        _node_layout_direction = self._view.get_layout_direction()

        if _node_layout_direction is EnumLayoutDirection.HORIZONTAL.value:
            _current_x = 0
            _node_height = 120
            for rank in sorted(range(len(_rank_map)), reverse=not down_stream):
                _ranked_nodes = _rank_map[rank]
                _max_width = max([node.view.width for node in _ranked_nodes])
                _current_x += _max_width
                _current_y = 0
                for idx, node in enumerate(_ranked_nodes):
                    _dy = max(_node_height, node.view.height)
                    _current_y += 0 if idx == 0 else _dy
                    node.set_pos(_current_x, _current_y)
                    _current_y += _dy * 0.5 + 10

                _current_x += _max_width * 0.5 + 100
        elif _node_layout_direction is EnumLayoutDirection.VERTICAL.value:
            _current_y = 0
            _node_width = 250
            for rank in sorted(range(len(_rank_map)), reverse=not down_stream):
                _ranked_nodes = _rank_map[rank]
                _max_height = max([node.view.height for node in _ranked_nodes])
                _current_y += _max_height
                _current_x = 0
                for idx, node in enumerate(_ranked_nodes):
                    _dx = max(_node_width, node.view.width)
                    _current_x += 0 if idx == 0 else _dx
                    node.set_pos(_current_x, _current_y)
                    _current_x += _dx * 0.5 + 10

                _current_y += _max_height * 0.5 + 100

        _nodes_center_1 = self.get_view().get_nodes_rect_center(_node_views)
        _dx = _nodes_center_0[0] - _nodes_center_1[0]
        _dy = _nodes_center_0[1] - _nodes_center_1[1]
        [n.set_pos(n.get_x_pos() + _dx, n.get_y_pos() + _dy) for n in nodes]

        # wrap the backdrop nodes.
        for backdrop, contained_nodes in _backdrops.items():
            backdrop.wrap_nodes(contained_nodes)

        self.end_undo()

    # convenience dialog functions.
    # --------------------------------------------------------------------------

    def question_dialog(self, text, title='Node Graph'):
        """
        Prompts a question open dialog with ``"Yes"`` and ``"No"`` buttons in
        the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().question_dialog`

        Args:
            text (str): question text.
            title (str): dialog window title.

        Returns:
            bool: true if user clicked yes.
        """
        return self._view.question_dialog(text, title)

    def message_dialog(self, text, title='Node Graph'):
        """
        Prompts a file open dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().message_dialog`

        Args:
            text (str): message text.
            title (str): dialog window title.
        """
        self._view.message_dialog(text, title)

    def load_dialog(self, current_dir=None, ext=None):
        """
        Prompts a file open dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().load_dialog`

        Args:
            current_dir (str): path to a directory.
            ext (str): custom file type extension (default: ``"json"``)

        Returns:
            str: selected file path.
        """
        return self._view.load_dialog(current_dir, ext)

    def save_dialog(self, current_dir=None, ext=None):
        """
        Prompts a file save dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().save_dialog`

        Args:
            current_dir (str): path to a directory.
            ext (str): custom file type extension (default: ``"json"``)

        Returns:
            str: selected file path.
        """
        return self._view.save_dialog(current_dir, ext)

    # group node / sub graph.
    # --------------------------------------------------------------------------

    def _on_close_sub_graph_request(self, index: int):
        """
        Called when the close button is clicked on a expanded sub graph.

        Args:
            index (int): tab index.
        """
        _node_id = self._widget.tabToolTip(index)
        _group_node = self.get_node_by_id(_node_id)
        self.collapse_group_node(_group_node)

    @property
    def is_root(self):
        """
        Returns if the node graph controller is the root graph.

        Returns:
            bool: true is the node graph is root.
        """
        return True

    @property
    def sub_graphs(self):
        """
        Returns expanded group node sub graphs.

        Returns:
            dict: {<node_id>: <sub_graph>}
        """
        return self._subGraphs

    # def graph_rect(self):
    #     """
    #     Get the graph viewer range (scene size).
    #
    #     Returns:
    #         list[float]: [x, y, width, height].
    #     """
    #     return self._viewer.scene_rect()
    #
    # def set_graph_rect(self, rect):
    #     """
    #     Set the graph viewer range (scene size).
    #
    #     Args:
    #         rect (list[float]): [x, y, width, height].
    #     """
    #     self._viewer.set_scene_rect(rect)

    def expand_group_node(self, node):
        """
        Expands a group node session in a new tab.

        Args:
            node (NodeGraphQt.GroupNode): group node.

        Returns:
            SubGraph: sub node graph used to manage the group node session.
        """
        if not isinstance(node, GroupNode):
            return
        if self._widget is None:
            raise RuntimeError('NodeGraph.widget not initialized!')

        self.get_view().clear_key_state()
        self.get_view().clearFocus()

        if node.id in self._subGraphs:
            _sub_graph = self._subGraphs[node.id]
            _tab_index = self._widget.indexOf(_sub_graph.widget)
            self._widget.setCurrentIndex(_tab_index)
            return _sub_graph

        # build new sub graph.
        _node_factory = copy.deepcopy(self._nodeFactory)
        _layout_direction = self.get_layout_direction()
        _sub_graph = SubGraph(self,
                              node=node,
                              node_factory=_node_factory,
                              layout_direction=_layout_direction)

        # populate the sub graph.
        _session = node.get_sub_graph_session()
        _sub_graph.deserialize_session(_session)

        # store reference to expanded.
        self._subGraphs[node.id] = _sub_graph

        # open new tab at root level.
        # todo: check option if custom handling the subGraph
        self.sigOpenSubGraphRequired.emit(node.get_name(), node.id)
        self._widget.add_view(_sub_graph.widget, node.get_name(), node.id)

        return _sub_graph

    def collapse_group_node(self, node):
        """
        Collapse a group node session tab and it's expanded child sub graphs.

        Args:
            node (NodeGraphQt.GroupNode): group node.
        """
        assert isinstance(node, GroupNode), 'node must be a GroupNode instance.'
        if self._widget is None:
            return

        if node.id not in self._subGraphs:
            _err = '{} sub graph not initialized!'.format(node.get_name())
            raise RuntimeError(_err)

        _sub_graph = self._subGraphs.pop(node.id)
        _sub_graph.collapse_group_node(node)

        # remove the sub graph tab.
        # todo: check option if custom handling the subGraph
        self._widget.remove_view(_sub_graph.widget)
        self.sigCloseSubGraphRequired.emit(node.id)
        # TODO: delete sub graph hmm... not sure if I need this here.
        del _sub_graph


class SubGraph(NodeGraph):
    """
    The ``SubGraph`` class is just like the ``NodeGraph`` but is the main
    controller for managing the expanded node graph for a group node.

    Inherited from: :class:`NodeGraphQt.NodeGraph`

    .. image:: _images/sub_graph.png
        :width: 70%

    -
    """

    def __init__(self, **kwargs):
        """
        Args:
            parent (object): object parent.
            node (GroupNode): group node related to this sub graph.
            node_factory (NodeFactory): override node factory.
            **kwargs : additional kwargs.
        """
        _parent = kwargs.get('parent')
        NodeGraph.__init__(self, _parent, **kwargs)
        _associated_node = kwargs.get('associated_node')
        assert _associated_node is not None and isinstance(_associated_node, NodeObject)
        # sub graph attributes.
        self._associatedNode = _associated_node
        self._parentGraph = _parent
        self._subViewWidget = None
        if self._parentGraph.is_root:
            self._initializedGraphs = [self]
            self._subGraphs[self._associatedNode.id] = self
        else:
            # delete attributes if not top level sub graph.
            del self._widget
            del self._subGraphs

        # clone context menu from the parent node graph.
        self._clone_context_menu_from_parent()

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self._associatedNode.type_, hex(id(self)))

    def _register_builtin_nodes(self):
        """
        Register the default builtin nodes to the :meth:`NodeGraph.node_factory`
        """
        return

    def _clone_context_menu_from_parent(self):
        """
        Clone the context menus from the parent node graph.
        """
        _graph_menu = self.get_context_menu('graph')
        _parent_menu = self.parent_graph.get_context_menu('graph')
        _parent_viewer = self.parent_graph.get_view()
        _excl_actions = [_parent_viewer.qaction_for_undo(),
                         _parent_viewer.qaction_for_redo()]

        def clone_menu(menu, menu_to_clone):
            """
            Args:
                menu (NodeGraphQt.NodeGraphMenu):
                menu_to_clone (NodeGraphQt.NodeGraphMenu):
            """
            _sub_items = []
            for item in menu_to_clone.get_items():
                if item is None:
                    menu.add_separator()
                    continue
                _name = item.name()
                if isinstance(item, NodeGraphMenu):
                    _sub_menu = menu.add_menu(_name)
                    _sub_items.append([_sub_menu, item])
                    continue

                if item in _excl_actions:
                    continue

                menu.add_command(
                    _name,
                    func=item.slot_function,
                    shortcut=item.q_action.shortcut()
                )

            for sub_menu, to_clone in _sub_items:
                clone_menu(sub_menu, to_clone)

        # duplicate the menu items.
        clone_menu(_graph_menu, _parent_menu)

    def _build_port_nodes(self):
        """
        Build the corresponding input & output nodes from the parent node ports
        and remove any port nodes that are outdated..

        Returns:
             tuple(dict, dict): input nodes, output nodes.
        """
        _node_layout_direction = self._view.get_layout_direction()

        # build the parent input port nodes.
        _input_nodes = {n.get_name(): n for n in self.get_nodes_by_type(PortInputNode.type_)}
        for port in self.node.get_input_ports():
            _port_name = port.get_name()
            if _port_name not in _input_nodes:
                _input_node = PortInputNode(parent_port=port)
                _input_node.NODE_NAME = _port_name
                _input_node.model.set_property('name', _port_name)
                _input_node.add_output(_port_name)
                _input_nodes[_port_name] = _input_node
                self.add_node(_input_node, selected=False, push_undo=False)
                _x, _y = _input_node.get_pos()
                if _node_layout_direction is EnumLayoutDirection.HORIZONTAL.value:
                    _x -= 100
                elif _node_layout_direction is EnumLayoutDirection.VERTICAL.value:
                    _y -= 100
                _input_node.set_property('pos', [_x, _y], push_undo=False)

        # build the parent output port nodes.
        _output_nodes = {n.get_name(): n for n in self.get_nodes_by_type(PortOutputNode.type_)}
        for port in self.node.get_output_ports():
            _port_name = port.get_name()
            if _port_name not in _output_nodes:
                _output_node = PortOutputNode(parent_port=port)
                _output_node.NODE_NAME = _port_name
                _output_node.model.set_property('name', _port_name)
                _output_node.add_input(_port_name)
                _output_nodes[_port_name] = _output_node
                self.add_node(_output_node, selected=False, push_undo=False)
                _x, _y = _output_node.get_pos()
                if _node_layout_direction is EnumLayoutDirection.HORIZONTAL.value:
                    _x += 100
                elif _node_layout_direction is EnumLayoutDirection.VERTICAL.value:
                    _y += 100
                _output_node.set_property('pos', [_x, _y], push_undo=False)

        return _input_nodes, _output_nodes

    def _deserialize(self, data, relative_pos=False, pos=None):
        """
        deserialize node data.
        (used internally by the node graph)

        Args:
            data (dict): node data.
            relative_pos (bool): position node relative to the cursor.
            pos (tuple or list): custom x, y position.

        Returns:
            list[NodeGraphQt.Nodes]: list of node instances.
        """
        # update node graph properties.
        for attr_name, attr_value in data.get('graph', {}).items():
            if attr_name == 'acyclic':
                self.set_acyclic(attr_value)
            elif attr_name == 'pipe_collision':
                self.set_pipe_collision(attr_value)

        # build the port input & output nodes here.
        _input_nodes, _output_nodes = self._build_port_nodes()

        # build the nodes.
        _nodes = {}
        for n_id, n_data in data.get('nodes', {}).items():
            _identifier = n_data['type_']
            _name = n_data.get('name')
            if _identifier == PortInputNode.type_:
                _nodes[n_id] = _input_nodes[_name]
                _nodes[n_id].set_pos(*(n_data.get('pos') or [0, 0]))
                continue
            elif _identifier == PortOutputNode.type_:
                _nodes[n_id] = _output_nodes[_name]
                _nodes[n_id].set_pos(*(n_data.get('pos') or [0, 0]))
                continue

            _node = self._nodeFactory.create_node_instance(_identifier)
            if not _node:
                continue

            _node.NODE_NAME = _name or _node.NODE_NAME
            # set properties.
            for prop in _node.model.properties.keys():
                if prop in n_data.keys():
                    _node.model.set_property(prop, n_data[prop])
            # set custom properties.
            for prop, val in n_data.get('custom', {}).items():
                _node.model.set_property(prop, val)

            _nodes[n_id] = _node
            self.add_node(_node, n_data.get('pos'))

            if n_data.get('port_deletion_allowed', None):
                _node.set_ports({
                    'input_ports': n_data['input_ports'],
                    'output_ports': n_data['output_ports']
                })

        # build the connections.
        for connection in data.get('connections', []):
            _nid, _pname = connection.get('in', ('', ''))
            _in_node = _nodes.get(_nid)
            if not _in_node:
                continue
            _in_port = _in_node.get_inputs().get(_pname) if _in_node else None

            _nid, _pname = connection.get('out', ('', ''))
            _out_node = _nodes.get(_nid)
            if not _out_node:
                continue
            _out_port = _out_node.get_outputs().get(_pname) if _out_node else None

            if _in_port and _out_port:
                self._undoStack.push(PortViewConnectedCmd(_in_port, _out_port))

        _node_objs = list(_nodes.values())
        if relative_pos:
            self._view.move_nodes([n.view for n in _node_objs])
            [setattr(n.model, 'pos', n.view.xy_pos) for n in _node_objs]
        elif pos:
            self._view.move_nodes([n.view for n in _node_objs], pos=pos)
            [setattr(n.model, 'pos', n.view.xy_pos) for n in _node_objs]

        return _node_objs

    def _on_navigation_changed(self, node_id, rm_node_ids):
        """
        Slot when the node navigation widget has changed.

        Args:
            node_id (str): selected group node id.
            rm_node_ids (list[str]): list of group node id to remove.
        """
        # collapse child sub graphs.
        for rm_node_id in rm_node_ids:
            _child_node = self.sub_graphs[rm_node_id].node
            self.collapse_group_node(_child_node)

        # show the selected node id sub graph.
        _sub_graph = self.sub_graphs.get(node_id)
        if _sub_graph:
            self.widget.show_view(_sub_graph.sub_view_widget)
            self.sigShowSubGraphRequired.emit(node_id)
            _sub_graph.get_view().setFocus()

    @property
    def is_root(self):
        """
        Returns if the node graph controller is the main root graph.

        Returns:
            bool: true is the node graph is root.
        """
        return False

    @property
    def sub_graphs(self):
        """
        Returns expanded group node sub graphs.

        Returns:
            dict: {<node_id>: <sub_graph>}
        """
        if self.parent_graph.is_root:
            return self._subGraphs
        return self.parent_graph.sub_graphs

    @property
    def initialized_graphs(self):
        """
        Returns a list of the sub graphs in the order they were initialized.

        Returns:
            list[NodeGraphQt.SubGraph]: list of sub graph objects.
        """
        if self._parentGraph.is_root:
            return self._initializedGraphs
        # fixme: parent could not have initialized_graphs
        return self._parentGraph.initialized_graphs

    @property
    def sub_view_widget(self):
        """
        The widget to the sub graph.

        Returns:
            PySide2.QtWidgets.QWidget: node graph widget.
        """
        if self._subViewWidget is None:
            self._subViewWidget = QtWidgets.QWidget()
            _layout = QtWidgets.QVBoxLayout(self._subViewWidget)
            _layout.setContentsMargins(0, 0, 0, 0)
            _layout.setSpacing(1)
            _layout.addWidget(self._view)
        return self._subViewWidget

    @property
    def widget(self):
        """
        The sub graph widget from the top most sub graph.

        Returns:
            SubGraphWidget: node graph widget.
        """
        if self.parent_graph.is_root:
            if self._widget is None:
                self._widget = SubGraphWidget()
                self._widget.add_view(self.sub_view_widget,
                                      self.node.get_name(),
                                      self.node.id)
                # connect the navigator widget signals.
                _navigator = self._widget.navigator
                _navigator.sigNavigationChanged.connect(
                    self._on_navigation_changed
                )
            return self._widget
        return self.parent_graph.p_widget

    @property
    def parent_graph(self):
        """
        The parent node graph controller.

        Returns:
            NodeGraphQt.NodeGraph or NodeGraphQt.SubGraph: parent graph.
        """
        return self._parentGraph

    @property
    def node(self):
        """
        Returns the parent node to the sub graph.

        .. image:: _images/group_node.png
            :width: 250px

        Returns:
            NodeGraphQt.GroupNode: group node.
        """
        return self._node

    def delete_node(self, node, push_undo=True):
        """
        Remove the node from the node sub graph.

        Note:
            :class:`.PortInputNode` & :class:`.PortOutputNode` can't be deleted
            as they are connected to a :class:`.Port` to remove these port nodes
            see :meth:`BaseNode.delete_input`, :meth:`BaseNode.delete_output`.

        Args:
            node (NodeGraphQt.BaseNode): node object.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        _port_nodes = self.get_input_port_nodes() + self.get_output_port_nodes()
        if node in _port_nodes and node.parent_port is not None:
            # note: port nodes can only be deleted by deleting the parent
            #       port object.
            raise NodeDeletionError(
                '{} can\'t be deleted as it is attached to a port!'.format(node)
            )
        super(SubGraph, self).delete_node(node, push_undo=push_undo)

    def delete_nodes(self, nodes, push_undo=True):
        """
        Remove a list of specified nodes from the node graph.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of node instances.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if not nodes:
            return

        _port_nodes = self.get_input_port_nodes() + self.get_output_port_nodes()
        for node in nodes:
            if node in _port_nodes and node.parent_port is not None:
                # note: port nodes can only be deleted by deleting the parent
                #       port object.
                raise NodeDeletionError(
                    '{} can\'t be deleted as it is attached to a port!'
                    .format(node)
                )

        super(SubGraph, self).delete_nodes(nodes, push_undo=push_undo)

    def collapse_graph(self, clear_session=True):
        """
        Collapse the current sub graph and hide its widget.

        Args:
            clear_session (bool): clear the current session.
        """
        # update the group node.
        _serialized_session = self.serialize_session()
        self.node.set_sub_graph_session(_serialized_session)

        # close the visible widgets.
        if self._undoView:
            self._undoView.close()
        # todo: collapse
        if self._subViewWidget:
            self.widget.hide_view(self._subViewWidget)

        if clear_session:
            self.clear_session()

    def expand_group_node(self, node):
        """
        Expands a group node session in current sub view.

        Args:
            node (NodeGraphQt.GroupNode): group node.

        Returns:
            SubGraph: sub node graph used to manage the group node session.
        """
        # todo: expand handling depends on the option
        assert isinstance(node, GroupNode), 'node must be a GroupNode instance.'

        if self._subViewWidget is None:
            raise RuntimeError('SubGraph.widget not initialized!')

        self.get_view().clear_key_state()
        self.get_view().clearFocus()

        if node.id in self.sub_graphs:
            _sub_graph_view = self.sub_graphs[node.id].viewer()
            _sub_graph_view.setFocus()
            return self.sub_graphs[node.id]

        # collapse expanded child sub graphs.
        _group_ids = [n.id for n in self.get_all_nodes() if isinstance(n, GroupNode)]
        for grp_node_id, grp_sub_graph in self.sub_graphs.items():
            # collapse current group node.
            if grp_node_id in _group_ids:
                _grp_node = self.get_node_by_id(grp_node_id)
                self.collapse_group_node(_grp_node)

            # close the widgets
            grp_sub_graph.collapse_graph(clear_session=False)

        # build new sub graph.
        _node_factory = copy.deepcopy(self.node_factory)
        _sub_graph = SubGraph(self,
                              node=node,
                              node_factory=_node_factory,
                              layout_direction=self.get_layout_direction())

        # populate the sub graph.
        _serialized_session = node.get_sub_graph_session()
        _sub_graph.deserialize_session(_serialized_session)

        # open new sub graph view.
        self.widget.add_view(_sub_graph.sub_view_widget,
                             node.get_name(),
                             node.id)
        self.sigOpenSubGraphRequired.emit(node.get_name(), node.id)
        # store the references.
        self.sub_graphs[node.id] = _sub_graph
        self.initialized_graphs.append(_sub_graph)

        return _sub_graph

    def collapse_group_node(self, node):
        """
        Collapse a group node session and it's expanded child sub graphs.

        Args:
            node (NodeGraphQt.GroupNode): group node.
        """
        # update the references.
        _sub_graph = self.sub_graphs.pop(node.id, None)
        if not _sub_graph:
            return

        _init_idx = self.initialized_graphs.index(_sub_graph) + 1
        for sgraph in reversed(self.initialized_graphs[_init_idx:]):
            self.initialized_graphs.remove(sgraph)

        # collapse child sub graphs here.
        _child_ids = [
            n.id for n in _sub_graph.get_all_nodes() if isinstance(n, GroupNode)
        ]
        for child_id in _child_ids:
            if self.sub_graphs.get(child_id):
                _child_graph = self.sub_graphs.pop(child_id)
                _child_graph.collapse_graph(clear_session=True)
                # remove child viewer widget.
                self.widget.remove_view(_child_graph.sub_view_widget)

        _sub_graph.collapse_graph(clear_session=True)
        self.widget.remove_view(_sub_graph.sub_view_widget)
        self.sigCloseSubGraphRequired.emit(node.id)

    def get_input_port_nodes(self):
        """
        Return all the port nodes related to the group node input ports.

        .. image:: _images/port_in_node.png
            :width: 150px

        -

        See Also:
            :meth:`NodeGraph.get_nodes_by_type`,
            :meth:`SubGraph.get_output_port_nodes`

        Returns:
            list[NodeGraphQt.PortInputNode]: input nodes.
        """
        return self.get_nodes_by_type(PortInputNode.type_)

    def get_output_port_nodes(self):
        """
        Return all the port nodes related to the group node output ports.

        .. image:: _images/port_out_node.png
            :width: 150px

        -

        See Also:
            :meth:`NodeGraph.get_nodes_by_type`,
            :meth:`SubGraph.get_input_port_nodes`

        Returns:
            list[NodeGraphQt.PortOutputNode]: output nodes.
        """
        return self.get_nodes_by_type(PortOutputNode.type_)

    def get_node_by_port(self, port):
        """
        Returns the node related to the parent group node port object.

        Args:
            port (NodeGraphQt.Port): parent node port object.

        Returns:
            PortInputNode or PortOutputNode: port node object.
        """
        _func_type = {
            EnumPortType.IN.value: self.get_input_port_nodes,
            EnumPortType.OUT.value: self.get_output_port_nodes
        }
        for n in _func_type.get(port.type_(), []):
            if port == n.parent_port:
                return n
