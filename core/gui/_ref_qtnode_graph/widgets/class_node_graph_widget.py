# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_node_graph_widget.py
# ------------------------------------------------------------------------------
#
# File          : class_node_graph_widget.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtWidgets, QtGui

from ..core.define import (
    EnumNodeStyleProperty, EnumViewFeature, EnumViewNavStyle
)
from .class_node_nav_widget import NodeNavigationWidget


class NodeGraphWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        super(NodeGraphWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.setTabBarAutoHide(True)

    def add_view(self, view: 'NodeGraphWidget', name: str, node_id: str):
        self.addTab(view, name)
        _index = self.indexOf(view)
        self.setTabToolTip(_index, node_id)
        self.setCurrentIndex(_index)

    def remove_view(self, view: QtWidgets.QGraphicsView):
        _index = self.indexOf(view)
        self.removeTab(_index)


class SubGraphWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, graph=None):
        super(SubGraphWidget, self).__init__(parent)
        self._graph = graph
        self._navigator = NodeNavigationWidget()
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(1)
        self._layout.addWidget(self._navigator)

        self._viewWidgets = {}
        self._viewCurrent = None

    @property
    def navigator(self):
        return self._navigator

    def add_view(self, view, name, node_id):
        if view in self._viewWidgets:
            return

        if self._viewCurrent:
            self.hide_view(self._viewCurrent)

        self._navigator.add_label_item(name, node_id)
        self._layout.addWidget(view)
        self._viewWidgets[view] = node_id
        self._viewCurrent = view
        self._viewCurrent.show()

    def remove_view(self, view=None):
        if view is None and self._viewCurrent:
            view = self._viewCurrent
        _node_id = self._viewWidgets.pop(view)
        self._navigator.remove_label_item(_node_id)
        self._layout.removeWidget(view)
        view.deleteLater()

    def hide_view(self, view):
        self._layout.removeWidget(view)
        view.hide()

    def show_view(self, view):
        if view == self._viewCurrent:
            self._viewCurrent.show()
            return
        if view in self._viewWidgets:
            if self._viewCurrent:
                self.hide_view(self._viewCurrent)
            self._layout.addWidget(view)
            self._viewCurrent = view
            self._viewCurrent.show()
