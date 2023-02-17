# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_menu.py
# ------------------------------------------------------------------------------
#
# File          : class_menu.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import re
from distutils.version import LooseVersion
from gui import QtGui,QtCore,QtWidgets

from .exceptions import NodeMenuError
from ..views.class_menu_widget import BaseMenuWidget, GraphAction, NodeAction


class NodeGraphMenu(object):
    """
    The ``NodeGraphMenu`` is the main context menu triggered from the node graph.

    example for accessing the node graph context menu.

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph

        node_graph = NodeGraph()

        # get the context menu for the node graph.
        context_menu = node_graph.get_context_menu('graph')

    """

    def __init__(self, graph, menu_widget:BaseMenuWidget):
        self._graph = graph
        self._menuWidget = menu_widget
        self._name = menu_widget.title()
        self._menus = {}
        self._commands = {}
        self._items = []

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self._name, hex(id(self)))

    @property
    def menu_widget(self):
        """
        The underlying QMenu.

        Returns:
            BaseMenu: menu object.
        """
        return self._menuWidget
    @property
    def name(self):
        """
        Returns the name for the menu.

        Returns:
            str: label name.
        """
        return self._name
    @property
    def items(self):
        """
        Return the menu items in the order they were added.

        Returns:
            list: current menu items.
        """
        return self._items

    def get_menu(self, name):
        """
        Returns the child menu by name.

        Args:
            name (str): name of the menu.

        Returns:
            NodeGraphQt.NodeGraphMenu: menu item.
        """
        self._menus.get(name)

    def get_command(self, name):
        """
        Returns the child menu command by name.

        Args:
            name (str): name of the command.

        Returns:
            NodeGraphQt.MenuCommand: context menu command.
        """
        return self._commands.get(name)

    def add_menu(self, name):
        """
        Adds a child menu to the current menu.

        Args:
            name (str): menu name.

        Returns:
            NodeGraphQt.NodeGraphMenu: the appended menu item.
        """
        if name in self._menus:
            raise NodeMenuError('menu object "{}" already exists!'.format(name))
        _base_menu = BaseMenuWidget(name, self._menuWidget)
        self._menuWidget.addMenu(_base_menu)
        _menu = NodeGraphMenu(self._graph, _base_menu)
        self._menus[name] = _menu
        self._items.append(_menu)
        return _menu

    def add_command(self, name, func=None, shortcut=None):
        """
        Adds a command to the menu.

        Args:
            name (str): command name.
            func (function): command function eg. "func(``graph``)".
            shortcut (str): shortcut key.

        Returns:
            NodeGraphQt.NodeGraphCommand: the appended command.
        """
        _action = GraphAction(name, self._graph.get_view())
        _action.graph = self._graph
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            _action.setShortcutVisibleInContextMenu(True)

        if isinstance(shortcut, str):
            _search = re.search(r'(?:\.|)QKeySequence\.(\w+)', shortcut)
            if _search:
                shortcut = getattr(QtGui.QKeySequence, _search.group(1))
            elif all([i in ['Alt', 'Enter'] for i in shortcut.split('+')]):
                shortcut = QtGui.QKeySequence(
                    QtCore.Qt.Key.Key_Alt + QtCore.Qt.Key.Key_Return
                )
            elif all([i in ['Return', 'Enter'] for i in shortcut.split('+')]):
                shortcut = QtCore.Qt.Key.Key_Return

        if shortcut:
            _action.setShortcut(shortcut)
        if func:
            _action.sigExecuted.connect(func)
        self._menuWidget.addAction(_action)
        _command = NodeGraphCommand(self._graph, _action, func)
        self._commands[name] = _command
        self._items.append(_command)
        return _command

    def add_separator(self):
        """
        Adds a separator to the menu.
        """
        self._menuWidget.addSeparator()
        self._items.append(None)


class NodesMenu(NodeGraphMenu):
    """
    The ``NodesMenu`` is the context menu triggered from a node.

    **Inherited from:** :class:`NodeGraphQt.NodeGraphMenu`

    example for accessing the nodes context menu.

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph

        node_graph = NodeGraph()

        # get the nodes context menu.
        nodes_menu = node_graph.get_context_menu('nodes')
    """

    def add_command(self, name, func=None, node_type=None, node_class=None):
        """
        Re-implemented to add a command to the specified node type menu.

        Args:
            name (str): command name.
            func (function): command function eg. "func(``graph``, ``node``)".
            node_type (str): specified node type for the command.
            node_class (class): specified node class for the command.

        Returns:
            NodeGraphQt.NodeGraphCommand: the appended command.
        """
        if not node_type and not node_class:
            raise NodeMenuError('Node type or Node class not specified!')

        if node_class:
            _node_type = node_class.__name__

        _node_menu = self._menuWidget.get_menu(node_type)
        if not _node_menu:
            _node_menu = BaseMenuWidget(node_type, self._menuWidget)

            if node_class:
                _node_menu.node_class = node_class
                _node_menu.graph = self._graph

            self._menuWidget.addMenu(_node_menu)

        if not self._menuWidget.isEnabled():
            self._menuWidget.setDisabled(False)

        _action = NodeAction(name, self._graph.viewer())
        _action.graph = self._graph
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            _action.setShortcutVisibleInContextMenu(True)
        if func:
            _action.sigExecuted.connect(func)

        if node_class:
            _node_menus = self._menuWidget.get_menus(node_class)
            if _node_menu in _node_menus:
                _node_menus.remove(_node_menu)
            for menu in _node_menus:
                menu.addAction(_action)

        _q_action = _node_menu.addAction(_action)
        _command = NodeGraphCommand(self._graph, _q_action, func)
        self._commands[name] = _command
        self._items.append(_command)
        return _command


class NodeGraphCommand(object):
    """
    Node graph menu command.
    """

    def __init__(self, graph, q_action, func=None):
        self._graph = graph
        self._qAction = q_action
        self._name = q_action.text()
        self._func = func

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self.name, hex(id(self)))

    @property
    def q_action(self):
        """
        The underlying qaction.

        Returns:
            GraphAction: qaction object.
        """
        return self._qAction

    @property
    def slot_function(self):
        """
        The function executed by this command.

        Returns:
            function: command function.
        """
        return self._func
    @property
    def name(self):
        """
        Returns the name for the menu command.

        Returns:
            str: label name.
        """
        return self._name

    def set_shortcut(self, shortcut=None):
        """
        Sets the shortcut key combination for the menu command.

        Args:
            shortcut (str): shortcut key.
        """
        shortcut = shortcut or QtGui.QKeySequence()
        self._qAction.setShortcut(shortcut)

    def run_command(self):
        """
        execute the menu command.
        """
        self._qAction.trigger()
