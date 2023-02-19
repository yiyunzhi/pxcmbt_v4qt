# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : mb_app.py
# ------------------------------------------------------------------------------
#
# File          : mb_app.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os, yaml, weakref
from pubsub import pub
from anytree.importer import DictImporter
from core.application.core.class_hierarchy_action_model import HierarchyActionModel
from core.gui.qtimp import QtGui, QtWidgets
from core.gui.core.class_base import ThemeStyledUiObject, I18nUiObject
from .main_win_mb_interactor import APPMenubarInteractor
from .define import EnumMainMenuIDs


class APPMenubarManager(ThemeStyledUiObject, I18nUiObject):
    def __init__(self, menu_bar: QtWidgets.QMenuBar, container: QtWidgets.QWidget):
        ThemeStyledUiObject.__init__(self)
        I18nUiObject.__init__(self)
        self.mb = menu_bar
        self.container = container
        self.model = None
        self.interactor = APPMenubarInteractor(self)
        self.refMap = weakref.WeakValueDictionary()
        self.cfgPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cfg_app_mb.yaml'))

    @staticmethod
    def parse_shortcut_ks(cfg_text: str) -> [QtGui.QKeySequence, None]:
        """
        QKeySequence(QKeySequence::Print);
        QKeySequence(tr("Ctrl+P"));
        QKeySequence(tr("Ctrl+p"));
        QKeySequence(Qt::CTRL + Qt::Key_P);
        """
        if cfg_text is None or not cfg_text:
            return
        if cfg_text.startswith('!'):
            _ks = cfg_text.replace('!', '')
            if hasattr(QtGui.QKeySequence.StandardKey, _ks):
                return getattr(QtGui.QKeySequence.StandardKey, _ks)
        elif cfg_text.startswith('>'):
            _ks = cfg_text.replace('>', '')
            return QtGui.QKeySequence(_ks)
        return None

    def _build_menu_items(self, item: HierarchyActionModel, parent: QtWidgets.QMenu):
        _icon_info = item.get_icon_info()
        _color = self.mb.palette().text().color()
        if item.children or item.asContainer:
            _menu = QtWidgets.QMenu(self.container)
            self.i18nUsageRegistry.register(_menu, item.i18nNs, item.label, 'setTitle', do_update=True)
            self.add_map(item.uid, _menu)
            if _icon_info is not None:
                self.iconUsageRegistry.register(_menu, *_icon_info)
                _icon = self.iconUsageRegistry.get_icon(_menu, color=_color)
                if _icon is not None:
                    _menu.setIcon(_icon)
            parent.addMenu(_menu)
            if item.children:
                _sorted_item = sorted(item.children, key=lambda n: n.oid)
                for x in _sorted_item:
                    self._build_menu_items(x, _menu)
        else:
            if item.label == '-':
                parent.addSeparator()
            else:
                _action = QtGui.QAction(self.container)
                _action.setData(item)
                self.i18nUsageRegistry.register(_action, item.i18nNs, item.label, 'setText', do_update=True)
                self.add_map(item.uid, _action)
                if _icon_info is not None:
                    self.iconUsageRegistry.register(_action, *_icon_info)
                    _icon = self.iconUsageRegistry.get_icon(_action, color=_color)
                    if _icon is not None:
                        _action.setIcon(_icon)
                _action.setStatusTip(item.tooltip)
                _scs = self.parse_shortcut_ks(item.shortcut)
                if _scs is not None:
                    _action.setShortcut(_scs)
                    _action.setShortcutContext(QtGui.Qt.ShortcutContext.ApplicationShortcut)
                parent.addAction(_action)

    def add_map(self, k, val):
        self.refMap[k] = val

    def get_ref(self, k):
        return self.refMap.get(k)

    def setup(self):
        with open(self.cfgPath, 'r', encoding='utf-8') as f:
            _data = yaml.load(f, Loader=yaml.SafeLoader)
            _tree = DictImporter(HierarchyActionModel).import_(_data)
        self.model = _tree
        _parent = self.container
        _sorted = sorted(_tree.children, key=lambda x: x.oid)
        for x in _sorted:
            _menu = self.mb.addMenu('')
            self.i18nUsageRegistry.register(_menu, x.i18nNs, x.label, 'setTitle', do_update=True)
            self.add_map(x.uid, _menu)
            _x_sorted = sorted(x.children, key=lambda n: n.oid)
            for y in _x_sorted:
                self._build_menu_items(y, _menu)

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        _palette = msg_data.get('palette')
        if _palette is None:
            _palette = self.mb.palette()
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

    def get_path(self, node: HierarchyActionModel):
        return node.path

    def enable(self, menu_action_id, enable=True):
        _action = self.get_ref(menu_action_id)
        if _action is not None:
            _action.setEnable(enable)
