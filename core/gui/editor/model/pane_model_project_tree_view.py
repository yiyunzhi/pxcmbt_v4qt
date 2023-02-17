# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_model_project_tree_view.py
# ------------------------------------------------------------------------------
#
# File          : pane_model_project_tree_view.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from application.core.base import singleton
from gui import QtGui, QtWidgets
import gui.qtads as QtAds


class _ModelProjectTreeViewContentPane(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel('Model', self)
        self.counter = QtWidgets.QSpinBox(self)
        self.treeView = QtWidgets.QTreeView(self)
        # bind event
        # layout
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.counter)
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)


@singleton
class ModelProjectTreeViewContentDockPane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__('Model', parent)
        self.setWidget(_ModelProjectTreeViewContentPane(self))
