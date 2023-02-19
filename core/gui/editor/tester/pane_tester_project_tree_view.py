# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_tester_project_tree_view.py
# ------------------------------------------------------------------------------
#
# File          : pane_tester_project_tree_view.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.application.core.base import singleton
from core.gui.qtimp import QtGui, QtWidgets
import core.gui.qtads as QtAds


class _TesterProjectTreeViewContentPane(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel('Tester', self)
        self.counter = QtWidgets.QSpinBox(self)
        self.treeView = QtWidgets.QTreeView(self)
        # bind event
        # layout
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.counter)
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)


@singleton
class TesterProjectTreeViewContentDockPane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__('Tester', parent)
        self.setWidget(_TesterProjectTreeViewContentPane(self))
