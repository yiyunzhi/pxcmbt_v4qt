# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : main_win_menu_bar_mc.py
# ------------------------------------------------------------------------------
#
# File          : main_win_menu_bar_mc.py
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
from core.application.class_application_context import ApplicationContext
from core.gui.qtimp import QtGui, QtWidgets
from core.gui.core.class_base import ZViewManager, ZViewContentContainer, Content
from core.gui.utils.class_call_ext_unified_evt_handle import CallExternalUnifiedEventHandle


class AppMenubarContentContainer(ZViewContentContainer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cfgPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cfg_app_mb.yaml'))

    def transform_data(self):
        with open(self.cfgPath, 'r', encoding='utf-8') as f:
            _data = yaml.load(f, Loader=yaml.SafeLoader)
            _tree = DictImporter(HierarchyActionModel).import_(_data)
        return _tree


class APPMenubarManager(ZViewManager):
    def __init__(self, **kwargs):
        ZViewManager.__init__(self, **kwargs)
        self._appCtx = ApplicationContext()
        self.refMap = weakref.WeakValueDictionary()
        self.ceUnifiedEventHandle = CallExternalUnifiedEventHandle()
        self.mbInteractor = APPMenubarInteractor(self)

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
        _color = self.view.palette().text().color()
        if item.children or item.asContainer:
            _menu = QtWidgets.QMenu(self.view.parent())
            _i18n_t = self._appCtx.i18nResp.get_i18n(_menu, i18n_ns=item.i18nNs, i18n_key=item.label, setter='setTitle')
            _menu.setTitle(_i18n_t)
            self.add_map(item.uid, _menu)
            if _icon_info is not None:
                _icon = self._appCtx.iconResp.get_icon(_menu, icon_ns=_icon_info[0],icon_name=_icon_info[1], setter='setIcon')
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
                _action = QtGui.QAction(self.view.parent())
                _action.setData(item)
                _i18n_t = self._appCtx.i18nResp.get_i18n(_action, i18n_ns=item.i18nNs, i18n_key=item.label, setter='setText')
                _action.setText(_i18n_t)
                self.add_map(item.uid, _action)
                if _icon_info is not None:
                    _icon = self._appCtx.iconResp.get_icon(_action, icon_ns=_icon_info[0],icon_name=_icon_info[1], setter='setIcon')
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

    def _setup(self):
        _tree = self.content_container.transform_data()
        _parent = self.view.parent()
        _sorted = sorted(_tree.children, key=lambda x: x.oid)
        for x in _sorted:
            _menu = self.view.addMenu('')
            _i18n_t = self._appCtx.i18nResp.get_i18n(_menu, i18n_ns=x.i18nNs, i18n_key=x.label, setter='setTitle')
            _menu.setTitle(_i18n_t)
            self.add_map(x.uid, _menu)
            _x_sorted = sorted(x.children, key=lambda n: n.oid)
            for y in _x_sorted:
                self._build_menu_items(y, _menu)
        self.view.triggered.connect(self.on_menubar_action_triggered)

    def on_menubar_action_triggered(self, event: QtGui.QAction):
        _e_data = event.data()
        if _e_data is None:
            return
        _handle = _e_data.handle
        if _handle is None:
            self.view.parent().on_menubar_action_triggered(event)
            return
        if self.ceUnifiedEventHandle.is_handleable(_handle['method']):
            self.ceUnifiedEventHandle.exec(self.view.parent(), _handle['method'], **_handle['kwargs'])
        else:
            _method = _handle.get('method')
            getattr(self.mbInteractor, _method)(event, self.view.parent(), **_handle['kwargs'])

    def get_path(self, node: HierarchyActionModel):
        return node.path

    def enable(self, menu_action_id, enable=True):
        _action = self.get_ref(menu_action_id)
        if _action is not None:
            _action.setEnable(enable)

    def set_content(self, content: Content):
        super().set_content(content)
        self.refMap.clear()
        self._setup()

    def restore_content(self):
        pass

    def ensure_view(self):
        pass


class APPMenubarInteractor:
    def __init__(self, view_manager):
        self.viewManager = view_manager
        self.appCtx = ApplicationContext()

    # ---------------------------------------------------
    # file menu
    # ---------------------------------------------------
    def on_open_project(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_new_project(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_save_project(self, event: QtGui.QAction, view, **kwargs):
        if self.appCtx.project is None:
            return
        self.appCtx.project.save_project()
        self.appCtx.project.save_all()

    def on_save_as_project(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_exit(self, event: QtGui.QAction, view, **kwargs):
        pass

    # ---------------------------------------------------
    # edit menu
    # ---------------------------------------------------
    def on_undo(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_redo(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_cut(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_copy(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_paste(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_remove(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_delete(self, event: QtGui.QAction, view, **kwargs):
        pass

    # ---------------------------------------------------
    # tool menu
    # ---------------------------------------------------
    def on_option(self, event: QtGui.QAction, view, **kwargs):
        pass

    # ---------------------------------------------------
    # windows menu
    # ---------------------------------------------------
    def on_save_perspective(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_load_perspective(self, event: QtGui.QAction, view, **kwargs):
        pass

    # ---------------------------------------------------
    # help menu
    # ---------------------------------------------------
    def on_help(self, event: QtGui.QAction, view, **kwargs):
        pass

    def on_about(self, event: QtGui.QAction, view, **kwargs):
        pass
