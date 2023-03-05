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
from core.application.core.base import singleton
from core.gui.core.class_qt_tree_model import ZQtTreeModel
from core.gui.core.class_base import ZView, Toggling
from core.gui.qtimp import QtWidgets, QtCore
import core.gui.qtads as QtAds


class _TesterProjectNodeTreeView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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


@singleton
class TesterProjectNodeTreeViewDockPane(QtAds.CDockWidget, ZView):
    def __init__(self, parent=None):
        super().__init__('', parent)
        self.zViewTitle = 'Tester'
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE, False)
        _widget = _TesterProjectNodeTreeView(self)
        self.setWidget(_widget)

    @ZView.title.setter
    def title(self, title):
        self.zViewTitle = title
        self.setWindowTitle(title)
