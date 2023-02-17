# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : tb_app_mode_sel.py
# ------------------------------------------------------------------------------
#
# File          : tb_app_mode_sel.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import typing
from pubsub import pub
from application.core.class_hierarchy_action_model import HierarchyActionModel
from gui import QtGui, QtWidgets, QtCore
from gui.core.define import evtAppThemeChanged
from gui.core.class_base import ThemeStyledUiObject, I18nUiObject


class AppModeSelectSideBar(QtWidgets.QToolBar, ThemeStyledUiObject, I18nUiObject):

    def __init__(self, parent):
        QtWidgets.QToolBar.__init__(self, 'AppModeToolBar', parent)
        ThemeStyledUiObject.__init__(self)
        I18nUiObject.__init__(self)
        self.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.setObjectName('modeSelToolBar')

    def _createModeActionSubmenu(self, mode_node: HierarchyActionModel, parent_menu: QtWidgets.QMenu = None):
        if parent_menu is None:
            _menu = QtWidgets.QMenu(self)
        else:
            _menu = parent_menu
        _icon_info = mode_node.getIconInfo()

        _color = self.palette().text().color()
        if mode_node.children:
            _p_menu = _menu.addMenu(mode_node.getLabel())
            self.i18nUsageRegistry.register(_p_menu, mode_node.i18nNs, mode_node.label)
            _p_menu.setText(self.i18nUsageRegistry.get_i18n_text(_p_menu))
            _p_menu.setData(mode_node)
            if _icon_info is not None:
                self.iconUsageRegistry.register(_p_menu, *_icon_info)
                _icon = self.iconUsageRegistry.get_icon(_p_menu, color=_color)
                if _icon is not None:
                    _p_menu.setIcon(_icon)
            for x in mode_node.children:
                self._createModeActionSubmenu(x, _p_menu)
        else:
            _icon_info = mode_node.getIconInfo()
            _action = _menu.addAction(mode_node.getLabel())
            self.i18nUsageRegistry.register(_action, mode_node.i18nNs, mode_node.label)
            _action.setText(self.i18nUsageRegistry.get_i18n_text(_action))
            _action.setData(mode_node)
            if _icon_info is not None:
                self.iconUsageRegistry.register(_action, *_icon_info)
                _icon = self.iconUsageRegistry.get_icon(_action, color=_color)
                if _icon is not None:
                    _action.setIcon(_icon)

    def addModeAction(self, mode_node: HierarchyActionModel, parent_tool_btn: [QtWidgets.QToolButton, QtGui.QActionGroup] = None):
        if parent_tool_btn is not None:
            _m = parent_tool_btn
        else:
            _m = self
        _icon_info = mode_node.getIconInfo()
        _action = _m.addAction(mode_node.getLabel())
        self.i18nUsageRegistry.register(_action, mode_node.i18nNs, mode_node.label)
        _action.setText(self.i18nUsageRegistry.get_i18n_text(_action))
        _action.setData(mode_node)
        _color = self.palette().text().color()
        if _icon_info is not None:
            self.iconUsageRegistry.register(_action, *_icon_info)
            _icon = self.iconUsageRegistry.get_icon(_action, color=_color)
            if _icon is not None:
                _action.setIcon(_icon)
        if mode_node.checkable:
            _action.setCheckable(mode_node.checkable)
            _action.setChecked(mode_node.state)
        if mode_node.children:
            _tb = self.widgetForAction(_action)
            _tb.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
            _menu = QtWidgets.QMenu(_tb)
            for x in mode_node.children:
                self._createModeActionSubmenu(x, _menu)
            _tb.setMenu(_menu)
        return _action

    def addSpacer(self):
        _spacer = QtWidgets.QWidget()
        _spacer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        self.addWidget(_spacer)

    def doRadioCheck(self, action: QtGui.QAction):
        for x in self.actions():
            if x is action:
                continue
            if x.isCheckable():
                if x.isChecked():
                    x.setChecked(False)

    def on_theme_changed(self,topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        _color = self.palette().text().color()
        for k in self.iconUsageRegistry.keyrefs():
            _obj = k()
            if _obj is not None:
                _obj.setIcon(self.iconUsageRegistry.get_icon(_obj, color=_color))

    def on_locale_changed(self,topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        for k in self.i18nUsageRegistry.keyrefs():
            _obj = k()
            if _obj is not None:
                _obj.setText(self.i18nUsageRegistry.get_i18n_text(_obj))
