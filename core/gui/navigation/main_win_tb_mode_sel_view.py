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
from pubsub import pub
from core.application.core.class_hierarchy_action_model import HierarchyActionModel
from core.application.class_application_context import ApplicationContext
from core.gui.qtimp import QtGui, QtWidgets, QtCore
from core.gui.core.class_base import ZView


class AppModeSelectSideBar(QtWidgets.QToolBar, ZView):

    def __init__(self, parent):
        QtWidgets.QToolBar.__init__(self, 'AppModeToolBar', parent)
        ZView.__init__(self)
        self.zViewTitle = 'AppModeToolBar'
        self._appCtx = ApplicationContext()
        self.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.setObjectName('modeSelToolBar')

    def _createModeActionSubmenu(self, mode_node: HierarchyActionModel, parent_menu: QtWidgets.QMenu = None):
        if parent_menu is None:
            _menu = QtWidgets.QMenu(self)
        else:
            _menu = parent_menu
        _icon_info = mode_node.get_icon_info()

        _color = self.palette().text().color()
        if mode_node.children:
            _p_menu = _menu.addMenu(mode_node.get_label())
            _i18n_t = self._appCtx.i18nResp.get_i18n(_p_menu, i18n_ns=mode_node.i18nNs, i18n_key=mode_node.label, setter='setText')
            _p_menu.setText(_i18n_t)
            _p_menu.setData(mode_node)
            if _icon_info is not None:
                _icon = self._appCtx.iconResp.get_icon(_p_menu, icon_ns=_icon_info[0], icon_name=_icon_info[1], setter='setIcon')
                if _icon is not None:
                    _p_menu.setIcon(_icon)
            for x in mode_node.children:
                self._createModeActionSubmenu(x, _p_menu)
        else:
            _icon_info = mode_node.get_icon_info()
            _action = _menu.addAction(mode_node.get_label())
            _i18n_t = self._appCtx.i18nResp.get_i18n(_action, i18n_ns=mode_node.i18nNs, i18n_key=mode_node.label, setter='setText')
            _action.setText(_i18n_t)
            _action.setData(mode_node)
            if _icon_info is not None:
                _icon = self._appCtx.iconResp.get_icon(_action, icon_ns=_icon_info[0], icon_name=_icon_info[1], setter='setIcon')
                if _icon is not None:
                    _action.setIcon(_icon)

    def init_actions(self, actions: list):
        # with open(self.cfgPath, 'r', encoding='utf-8') as f:
        #     _data = yaml.load(f, Loader=yaml.SafeLoader)
        #     _tree = DictImporter(HierarchyActionModel).import_(_data)
        # _active_mode_action = None
        # _sorted = sorted(_tree.children, key=lambda x: x.oid)
        _active_mode_action = None
        for x in actions:
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
        _i18n_t = self._appCtx.i18nResp.get_i18n(_action, i18n_ns=mode_node.i18nNs, i18n_key=mode_node.label, setter='setText')
        _action.setText(_i18n_t)
        _action.setData(mode_node)
        _color = self.palette().text().color()
        if _icon_info is not None:
            _icon = self._appCtx.iconResp.get_icon(_action, icon_ns=_icon_info[0], icon_name=_icon_info[1], setter='setIcon')
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
