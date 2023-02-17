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
from gui import QtCore, QtWidgets, QtGui

from ..core.define import EnumViewNavStyle


class BaseMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        super(BaseMenu, self).__init__(*args, **kwargs)
        self.nodeClass = None
        self.graph = None

    # disable for issue #142
    # def hideEvent(self, event):
    #     super(BaseMenu, self).hideEvent(event)
    #     for a in self.actions():
    #         if hasattr(a, 'node_id'):
    #             a.node_id = None

    def get_menu(self, name, node_id=None):
        for action in self.actions():
            _menu = action.menu()
            if not _menu:
                continue
            if _menu.title() == name:
                return _menu
            if node_id and _menu.node_class:
                _node = _menu.graph.get_node_by_id(node_id)
                if isinstance(_node, _menu.nodeClass):
                    return _menu

    def get_menus(self, node_class):
        _menus = []
        for action in self.actions():
            _menu = action.menu()
            if _menu.nodeClass:
                if issubclass(_menu.nodeClass, node_class):
                    _menus.append(_menu)
        return _menus


class GraphAction(QtGui.QAction):
    sigExecuted = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(GraphAction, self).__init__(*args, **kwargs)
        self.graph = None
        self.triggered.connect(self._on_triggered)

    def _on_triggered(self):
        self.sigExecuted.emit(self.graph)

    def get_action(self, name):
        for action in self.qmenu.actions():
            if not action.menu() and action.text() == name:
                return action


class NodeAction(GraphAction):
    sigExecuted = QtCore.Signal(object, object)

    def __init__(self, *args, **kwargs):
        super(NodeAction, self).__init__(*args, **kwargs)
        self.nodeId = None

    def _on_triggered(self):
        _node = self.graph.get_node_by_id(self.nodeId)
        self.sigExecuted.emit(self.graph, _node)
