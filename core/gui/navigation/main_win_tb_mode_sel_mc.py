# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : main_win_tb_mode_sel_mc.py
# ------------------------------------------------------------------------------
#
# File          : main_win_tb_mode_sel_mc.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os, yaml
from pubsub import pub
from anytree.importer import DictImporter
from core.application.core.class_hierarchy_action_model import HierarchyActionModel
from core.application.define import EnumAppMsg
from core.gui.qtimp import QtGui
from core.gui.core.class_base import ZViewContentContainer, ZViewManager,ZViewModifier
from .define import EnumAppModeMenuIDs


class AppModeSelectSideBarContentContainer(ZViewContentContainer):
    def __init__(self, **kwargs):
        ZViewContentContainer.__init__(self, **kwargs)
        self.cfgPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cfg_app_mode_action.yaml'))

    def transform_data(self):
        with open(self.cfgPath, 'r', encoding='utf-8') as f:
            _data = yaml.load(f, Loader=yaml.SafeLoader)
            _tree = DictImporter(HierarchyActionModel).import_(_data)
        return _tree


class AppModeSelectSideBarManager(ZViewManager):
    def __init__(self, **kwargs):
        ZViewManager.__init__(self, **kwargs)
        self.activeModeAction = None
        self._initActiveModeAction=None

    def _setup(self):
        _tree = self.content_container.transform_data()
        _sorted = sorted(_tree.children, key=lambda x: x.oid)
        self._initActiveModeAction = self.view.init_actions(_sorted)
        self.view.actionTriggered.connect(self.on_app_mode_changed)

    def on_app_mode_changed(self, event: QtGui.QAction):
        if self.activeModeAction==event:
            return
        _data = event.data()
        self.activeModeAction = event
        _modifiers=list()
        for x in _data.layoutModifiers:
            _modifiers.append(ZViewModifier(**x))
        self.sigChangeMainViewRequired.emit('viewModify', _modifiers)
        pub.sendMessage(EnumAppMsg.sigAppModeChanged, mode=event.data())

    def set_state(self, state):
        if state == 'noProject':
            for x in self.view.actions():
                if x.data():
                    if x.data().uid in [EnumAppModeMenuIDs.MODEL, EnumAppModeMenuIDs.TESTER]:
                        x.setVisible(False)
        elif state == 'projectLoaded':
            for x in self.view.actions():
                x.setVisible(True)

    def set_content(self, content):
        super().set_content(content)
        self._setup()

    def restore_content(self):
        pass

    def ensure_view(self):
        if self.view is None:
            return
        self.on_app_mode_changed(self._initActiveModeAction)
