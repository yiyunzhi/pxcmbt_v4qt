# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_blocks_project_tree_view.py
# ------------------------------------------------------------------------------
#
# File          : pane_blocks_project_tree_view.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from pubsub import pub
from application.core.base import singleton
from gui import QtGui, QtWidgets, QtCore
from gui.core.class_base import ThemeStyledUiObject, I18nUiObject
import gui.qtads as QtAds


class _BlocksProjectTreeViewContentPane(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel('Blocks', self)
        self.counter = QtWidgets.QSpinBox(self)
        self.treeView = QtWidgets.QTreeView(self)
        # bind event
        # layout
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.counter)
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)


@singleton
class BlocksProjectTreeViewContentDockPane(QtAds.CDockWidget, I18nUiObject, ThemeStyledUiObject):
    def __init__(self, parent):
        super().__init__('Blocks', parent)
        I18nUiObject.__init__(self)
        ThemeStyledUiObject.__init__(self)
        self.setWidget(_BlocksProjectTreeViewContentPane(self))

    def on_locale_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        self.setWindowTitle(self.i18nUsageRegistry.get_i18n('app', 'blocks').capitalize())

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        pass
