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
from pubsub import pub
from core.gui.core.class_qt_tree_model import ZQtTreeModel, ZQtTreeModelItem
from core.gui.qtimp import QtWidgets, QtCore, QtGui
from core.gui.utils.helper import get_qApp
import core.gui.qtads as QtAds
from core.gui.core.class_base import ThemeStyledUiObject, I18nUiObject


class _ModelProjectNodeTreeView(QtWidgets.QWidget, ThemeStyledUiObject, I18nUiObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        ThemeStyledUiObject.__init__(self)
        I18nUiObject.__init__(self)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar(self)
        self.treeView = QtWidgets.QTreeView(self)
        self._init_toolbar()
        # layout
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.toolbar)
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)

    def _init_toolbar(self):
        self.toolbar.setIconSize(QtCore.QSize(18, 18))
        _icon_color = self.palette().light().color()
        _add_prototype_action = QtGui.QAction('add prototype', self)
        self.iconUsageRegistry.register(_add_prototype_action, 'fa', 'ri.pencil-ruler-2-line')
        _add_prototype_action.setIcon(self.iconUsageRegistry.get_icon(_add_prototype_action, color=_icon_color))

        _add_ability_action = QtGui.QAction('add ability', self)
        self.iconUsageRegistry.register(_add_ability_action, 'fa', 'ri.cpu-line')
        _add_ability_action.setIcon(self.iconUsageRegistry.get_icon(_add_ability_action, color=_icon_color))

        _remove_action = QtGui.QAction('remove', self)
        self.iconUsageRegistry.register(_remove_action, 'fa', 'ri.delete-bin-line')
        _remove_action.setIcon(self.iconUsageRegistry.get_icon(_remove_action, color=_icon_color))

        _order_action = QtGui.QAction('sort', self)
        self.iconUsageRegistry.register(_order_action, 'fa', 'ri.list-unordered')
        _order_action.setIcon(self.iconUsageRegistry.get_icon(_order_action, color=_icon_color))

        _order_menu = QtWidgets.QMenu(self)
        _order_by_name_action = QtGui.QAction('sort by name', self)
        self.iconUsageRegistry.register(_order_by_name_action, 'fa', 'ri.price-tag-3-line')
        _order_by_name_action.setIcon(self.iconUsageRegistry.get_icon(_order_by_name_action, color=_icon_color))
        _order_by_date_action = QtGui.QAction('sort by date', self)
        self.iconUsageRegistry.register(_order_by_date_action, 'fa', 'ri.calendar-line')
        _order_by_date_action.setIcon(self.iconUsageRegistry.get_icon(_order_by_date_action, color=_icon_color))
        _order_menu.addAction(_order_by_name_action)
        _order_menu.addAction(_order_by_date_action)

        _order_action.setMenu(_order_menu)

        self.toolbar.addAction(_add_prototype_action)
        self.toolbar.addAction(_add_ability_action)
        self.toolbar.addAction(_remove_action)
        self.toolbar.addAction(_order_action)

    def on_locale_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        pass

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        pass

    def set_content(self, model: ZQtTreeModel):
        self.treeView.setModel(model)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.PaletteChange:
            event.accept()


class ModelProjectNodeTreeViewDockPane(QtAds.CDockWidget):
    def __init__(self, parent=None):
        super().__init__('Model', parent)
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE, False)
        _widget = _ModelProjectNodeTreeView(self)
        self.setWidget(_widget)
