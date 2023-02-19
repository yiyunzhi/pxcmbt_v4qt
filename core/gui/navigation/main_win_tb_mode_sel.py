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
import typing, os, yaml
from pubsub import pub
from anytree.importer import DictImporter
from core.application.core.class_hierarchy_action_model import HierarchyActionModel
from core.gui.qtimp import QtGui, QtWidgets, QtCore
from core.gui.core.class_base import ThemeStyledUiObject, I18nUiObject


class AppModeSelectSideBar(QtWidgets.QToolBar, ThemeStyledUiObject, I18nUiObject):

    def __init__(self, parent):
        QtWidgets.QToolBar.__init__(self, 'AppModeToolBar', parent)
        ThemeStyledUiObject.__init__(self)
        I18nUiObject.__init__(self)
        self.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.setObjectName('modeSelToolBar')
        self.cfgPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cfg_app_mode_action.yaml'))

    def _createModeActionSubmenu(self, mode_node: HierarchyActionModel, parent_menu: QtWidgets.QMenu = None):
        if parent_menu is None:
            _menu = QtWidgets.QMenu(self)
        else:
            _menu = parent_menu
        _icon_info = mode_node.get_icon_info()

        _color = self.palette().text().color()
        if mode_node.children:
            _p_menu = _menu.addMenu(mode_node.get_label())
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
            _icon_info = mode_node.get_icon_info()
            _action = _menu.addAction(mode_node.get_label())
            self.i18nUsageRegistry.register(_action, mode_node.i18nNs, mode_node.label)
            _action.setText(self.i18nUsageRegistry.get_i18n_text(_action))
            _action.setData(mode_node)
            if _icon_info is not None:
                self.iconUsageRegistry.register(_action, *_icon_info)
                _icon = self.iconUsageRegistry.get_icon(_action, color=_color)
                if _icon is not None:
                    _action.setIcon(_icon)

    def setup(self):
        with open(self.cfgPath, 'r', encoding='utf-8') as f:
            _data = yaml.load(f, Loader=yaml.SafeLoader)
            _tree = DictImporter(HierarchyActionModel).import_(_data)
        _active_mode_action = None
        _sorted = sorted(_tree.children, key=lambda x: x.oid)
        for x in _sorted:
            if x.label == '=':
                self.add_spacer()
            elif x.label == '-':
                self.addSeparator()
            elif x.label == '[]':
                _action_g = QtGui.QActionGroup(self)
                _actions = []
                for gi in x.children:
                    _action = self.add_mode_action(gi, _action_g)
                    if gi.checkable and gi.state:
                        _active_mode_action = _action
                    _actions.append(_action)
                self.addActions(_actions)
            else:
                _action = self.add_mode_action(x)
                if x.checkable and x.state:
                    _active_mode_action = _action
        return _active_mode_action

    def add_mode_action(self, mode_node: HierarchyActionModel, parent_tool_btn: [QtWidgets.QToolButton, QtGui.QActionGroup] = None):
        if parent_tool_btn is not None:
            _m = parent_tool_btn
        else:
            _m = self
        _icon_info = mode_node.get_icon_info()
        _action = _m.addAction(mode_node.get_label())
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

    def add_spacer(self):
        _spacer = QtWidgets.QWidget()
        _spacer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        self.addWidget(_spacer)

    def do_radio_check(self, action: QtGui.QAction):
        for x in self.actions():
            if x is action:
                continue
            if x.isCheckable():
                if x.isChecked():
                    x.setChecked(False)

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        _palette = msg_data.get('palette')
        if _palette is None:
            _palette = self.palette()
        _color = _palette.text().color()
        for k in self.iconUsageRegistry.keyrefs():
            _obj = k()
            if _obj is not None:
                _obj.setIcon(self.iconUsageRegistry.get_icon(_obj, color=_color, force=True))

    def on_locale_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        for k in self.i18nUsageRegistry.keyrefs():
            _obj = k()
            if _obj is not None:
                _obj.setText(self.i18nUsageRegistry.get_i18n_text(_obj))
