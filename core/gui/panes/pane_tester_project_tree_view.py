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
from pubsub import pub
from core.gui.core.class_qt_tree_model import ZQtTreeModel, ZQtTreeModelItem
from core.gui.qtimp import QtWidgets, QtCore
import core.gui.qtads as QtAds
from core.gui.core.class_base import ThemeStyledUiObject, I18nUiObject


class _TesterProjectNodeTreeView(QtWidgets.QWidget, ThemeStyledUiObject, I18nUiObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        ThemeStyledUiObject.__init__(self)
        I18nUiObject.__init__(self)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar(self)
        self.treeView = QtWidgets.QTreeView(self)
        self._init_toolbar()
        # layout
        self.mainLayout.addWidget(self.toolbar)
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)

    def _init_toolbar(self):
        self.toolbar.addAction('Add->')
        self.toolbar.addAction('remove')
        self.toolbar.addAction('reorder->')

    def on_locale_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        pass

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        pass

    def set_content(self, model: ZQtTreeModel):
        self.treeView.setModel(model)


class TesterProjectNodeTreeViewDockPane(QtAds.CDockWidget):
    def __init__(self, parent=None):
        super().__init__('Tester', parent)
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE, False)
        _widget = _TesterProjectNodeTreeView(self)
        self.setWidget(_widget)
