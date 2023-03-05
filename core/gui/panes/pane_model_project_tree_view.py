# -*- coding: utf-8 -*-
import addict

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
from core.application.class_application_context import ApplicationContext
from core.application.core.base import singleton
from core.application.zI18n import zI18n
from core.gui.qtimp import QtWidgets, QtCore, QtGui
import core.gui.qtads as QtAds
from core.gui.core.class_base import ZView, Toggling
from core.gui.components.widget_header import HeaderWidget
from core.gui.components.widget_alert import AlertWidget


class _ModelProjectNodeTreeView(QtWidgets.QWidget, ZView):
    sigAddNodeRequired = QtCore.Signal(str, object)
    sigRemoveNodeRequired = QtCore.Signal(list)
    sigEditNodeRequired = QtCore.Signal(QtCore.QModelIndex, object)
    sigSortNodeRequired = QtCore.Signal(str)
    sigItemDoubleClicked = QtCore.Signal(QtCore.QModelIndex)
    sigItemSelectionChanged = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        ZView.__init__(self)
        self._appCtx: ApplicationContext = ApplicationContext()
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar(self)
        self.treeView = QtWidgets.QTreeView(self)
        self.treeView.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.setIconSize(QtCore.QSize(18, 18))
        self.treeView.setContentsMargins(0, 0, 0, 0)
        self.treeView.setEditTriggers(QtWidgets.QTreeView.EditTrigger.EditKeyPressed)
        self._init_toolbar()
        # bind event
        self.treeView.customContextMenuRequested.connect(self.on_context_menu_activated)
        self.treeView.doubleClicked.connect(self.on_node_double_clicked)
        self.treeView.clicked.connect(self.on_node_clicked)

        # layout
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.toolbar)
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)

    def _init_toolbar(self):
        _toggling_dis_states = ['readonly']
        self.toolbar.setIconSize(QtCore.QSize(18, 18))
        _icon_color = self.palette().light().color()
        _add_menu = QtWidgets.QMenu(self)
        _add_action = QtGui.QAction('sort', self)
        _icon = self._appCtx.iconResp.get_icon(_add_action, icon_ns='fa', icon_name='ri.add-box-line', setter='setIcon')
        _add_action.setIcon(_icon)
        _add_action.setMenu(_add_menu)

        _add_prototype_action = QtGui.QAction('add prototype', self)
        _icon = self._appCtx.iconResp.get_icon(_add_prototype_action, icon_ns='fa', icon_name='ri.pencil-ruler-2-line', setter='setIcon')
        _add_prototype_action.setIcon(_icon)
        _add_menu.addAction(_add_prototype_action)

        _add_ability_action = QtGui.QAction('add ability', self)
        _icon = self._appCtx.iconResp.get_icon(_add_ability_action, icon_ns='fa', icon_name='ri.cpu-line', setter='setIcon')
        _add_ability_action.setIcon(_icon)
        _add_menu.addAction(_add_ability_action)

        _remove_action = QtGui.QAction('remove', self)
        _remove_action.setData(Toggling(_toggling_dis_states, _remove_action.setEnabled))
        _icon = self._appCtx.iconResp.get_icon(_remove_action, icon_ns='fa', icon_name='ri.delete-bin-line', setter='setIcon')
        _remove_action.setIcon(_icon)

        _order_action = QtGui.QAction('sort', self)
        _icon = self._appCtx.iconResp.get_icon(_order_action, icon_ns='fa', icon_name='ri.list-unordered', setter='setIcon')
        _order_action.setIcon(_icon)

        _order_menu = QtWidgets.QMenu(self)
        _order_by_name_action = QtGui.QAction('sort by name', self)
        _icon = self._appCtx.iconResp.get_icon(_order_by_name_action, icon_ns='fa', icon_name='ri.price-tag-3-line', setter='setIcon')
        _order_by_name_action.setIcon(_icon)
        _order_by_date_action = QtGui.QAction('sort by date', self)
        _icon = self._appCtx.iconResp.get_icon(_order_by_date_action, icon_ns='fa', icon_name='ri.calendar-line', setter='setIcon')
        _order_by_date_action.setIcon(_icon)
        _order_menu.addAction(_order_by_name_action)
        _order_menu.addAction(_order_by_date_action)

        _order_action.setMenu(_order_menu)

        _add_prototype_action.triggered.connect(self._on_action_add_prototype)
        _add_ability_action.triggered.connect(self._on_action_add_ability)
        _remove_action.triggered.connect(self._on_action_remove)
        _order_by_name_action.triggered.connect(self._on_action_sort_by_name)
        _order_by_date_action.triggered.connect(self._on_action_sort_by_date)

        self.toolbar.addAction(_add_action)
        self.toolbar.addAction(_remove_action)
        self.toolbar.addAction(_order_action)

    def on_context_menu_activated(self, pos: QtCore.QPoint):
        _idx_at = self.treeView.indexAt(pos)
        if not _idx_at.isValid():
            return
        _node = _idx_at.internalPointer()
        if _node is None or _node.readonly:
            return

        _menu = QtWidgets.QMenu()
        _action_rename = QtGui.QAction('rename', self)
        _action_copy = QtGui.QAction('copy', self)
        _action_paste = QtGui.QAction('paste', self)
        _action_delete = QtGui.QAction('delete', self)
        _menu.addAction(_action_rename)
        _menu.addSeparator()
        _menu.addAction(_action_copy)
        _menu.addAction(_action_paste)
        _menu.addAction(_action_delete)
        _action_rename.triggered.connect(lambda x: self.on_node_rename_required(x, _idx_at))
        _action_copy.triggered.connect(lambda x: self.on_node_copy_required(x, _idx_at))
        _action_paste.triggered.connect(lambda x: self.on_node_paste_required(x, _idx_at))
        _action_delete.triggered.connect(lambda x: self.on_node_delete_required(x, _idx_at))
        _menu.exec(QtGui.QCursor.pos())

    def on_node_rename_required(self, evt, index: QtCore.QModelIndex):
        _node = index.internalPointer()
        _old_name = _node.label
        _sibling_names = [x.label for x in _node.siblings]
        self.treeView.edit(index)

        def _on_edit_done(editor: QtWidgets.QLineEdit):
            _edit_value = editor.text()
            if _edit_value in _sibling_names:
                _msg_b = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning,
                                               zI18n.t('app.waining'),
                                               zI18n.t('err.exist_f').format(_edit_value),
                                               parent=self)
                _msg_b.exec()
            else:
                self.sigEditNodeRequired.emit(index, _old_name)
            self.treeView.itemDelegate(index).closeEditor.disconnect()

        self.treeView.itemDelegate(index).closeEditor.connect(_on_edit_done)

    def on_node_copy_required(self, evt, index: QtCore.QModelIndex):
        self.copy_item(index)

    def on_node_paste_required(self, evt, index: QtCore.QModelIndex):
        pass

    def on_node_delete_required(self, evt, index: QtCore.QModelIndex):
        self.delete_item(index)

    def on_node_double_clicked(self, index: QtCore.QModelIndex):
        _item = index.internalPointer()
        if _item.children and _item.userData is None:
            return
        self.sigItemDoubleClicked.emit(index)

    def on_node_clicked(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return
        _item = index.internalPointer()
        if _item.readonly:
            self.set_toolbar_state('readonly')
        else:
            self.set_toolbar_state('normal')
        self.sigItemSelectionChanged.emit(index)

    def set_toolbar_state(self, state='normal'):
        for x in self.toolbar.actions():
            if x.data() and isinstance(x.data(), Toggling):
                x.data().toggle(state)

    def copy_item(self, index):
        pass

    def paste_item(self):
        pass

    def delete_item(self, index):
        _msg_b = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, 'delete',
                                       'are you sure? this action is not reversible',
                                       QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, self)
        if _msg_b.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            self.sigRemoveNodeRequired.emit([index] if not isinstance(index, list) else index)

    def _show_create_prototype_prompt_dialog(self) -> (bool, addict.Dict):
        _dlg = QtWidgets.QDialog(self)
        _dlg.setWindowTitle(zI18n.t('app.create_new_prototype'))
        _dlg_layout = QtWidgets.QVBoxLayout(_dlg)
        _msg_layout = QtWidgets.QVBoxLayout(_dlg)
        _form = QtWidgets.QFormLayout(_dlg)
        _form.setVerticalSpacing(5)
        _hdr_w = HeaderWidget(_dlg)
        _hdr_w.set_content(zI18n.t('app.prompt_detail'), zI18n.t('app.prompt_new_prototype_detail'))
        _form.addRow(_hdr_w)
        _form.addRow(_msg_layout)
        _form.addRow(' ', None)
        _name_edit = QtWidgets.QLineEdit(zI18n.t('app.new_f') % 'prototype', _dlg)
        _form.addRow(zI18n.t('app.name') + ':', _name_edit)
        _form.addRow(' ', None)
        _btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel, _dlg)
        _dlg_layout.addLayout(_form)
        _dlg_layout.addWidget(_btn_box)
        _dlg.setLayout(_dlg_layout)
        _res = addict.Dict()

        def _on_accepted():
            if not _name_edit.text():
                _msg_layout.addWidget(AlertWidget(_dlg, description=zI18n.t('err.empty_f').format('name')))
            else:
                _name = _name_edit.text()
                if not self.zViewManager.is_valid_prototype_name(_name):
                    _msg_layout.addWidget(AlertWidget(_dlg, description=zI18n.t('err.exist_f').format('name')))
                    return
                _res.name = _name
                _dlg.accept()

        _btn_box.accepted.connect(_on_accepted)
        _btn_box.rejected.connect(_dlg.reject)

        if _dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            return True, _res
        else:
            return False, _res

    def _show_create_ability_prompt_dialog(self, ab_options) -> (bool, addict.Dict):
        _dlg = QtWidgets.QDialog(self)
        _dlg.setWindowTitle(zI18n.t('app.create_new_ability'))
        _dlg_layout = QtWidgets.QVBoxLayout(_dlg)
        _msg_layout = QtWidgets.QVBoxLayout(_dlg)
        _form = QtWidgets.QFormLayout(_dlg)
        _form.setVerticalSpacing(5)
        _hdr_w = HeaderWidget(_dlg)
        _hdr_w.set_content(zI18n.t('app.prompt_detail'), zI18n.t('app.prompt_new_ability_detail'))
        _form.addRow(_hdr_w)
        _form.addRow(_msg_layout)
        _form.addRow(' ', None)
        _name_edit = QtWidgets.QLineEdit(zI18n.t('app.new_f') % 'ability', _dlg)
        _form.addRow(zI18n.t('app.name') + ':', _name_edit)
        _selection = QtWidgets.QComboBox(_dlg)
        _selection.addItems(ab_options)
        _form.addRow(zI18n.t('app.type') + ':', _selection)
        _form.addRow(' ', None)
        _btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel, _dlg)
        _dlg_layout.addLayout(_form)
        _dlg_layout.addWidget(_btn_box)
        _dlg.setLayout(_dlg_layout)
        _res = addict.Dict()

        def _on_accepted():
            _name = _name_edit.text()
            if not _name_edit.text():
                _msg_layout.addWidget(AlertWidget(_dlg, description=zI18n.t('err.empty_f').format('name')))
            else:
                if not self.zViewManager.is_valid_ability_name(_name):
                    _msg_layout.addWidget(AlertWidget(_dlg, description=zI18n.t('err.exist_f').format(_name)))
                    return
                _res.name = _name
                _res.option = _selection.currentText()
                _dlg.accept()

        _btn_box.accepted.connect(_on_accepted)
        _btn_box.rejected.connect(_dlg.reject)

        if _dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            return True, _res
        else:
            return False, _res

    def _on_action_add_prototype(self, action: QtGui.QAction):
        _ret, _form_data = self._show_create_prototype_prompt_dialog()
        if _ret:
            self.sigAddNodeRequired.emit('prototype', _form_data)

    def _on_action_add_ability(self, action: QtGui.QAction):
        _slt_names = dict()
        for k, v in self._appCtx.mbt_solution_manager.solutions.items():
            if v.is_valid:
                _slt_names.update({v.name: v})
        _ret, _form_data = self._show_create_ability_prompt_dialog(list(_slt_names.keys()))
        if _ret:
            _slt = _slt_names.get(_form_data.option)
            _options = addict.Dict()
            _options.solution = _slt
            _options.name = _form_data.name
            self.sigAddNodeRequired.emit('ability', _options)

    def _on_action_remove(self, action: QtGui.QAction):
        _indexes = self.treeView.selectedIndexes()
        self.delete_item(_indexes)

    def _on_action_sort_by_name(self, action: QtGui.QAction):
        self.sigSortNodeRequired.emit('name')

    def _on_action_sort_by_date(self, action: QtGui.QAction):
        self.sigSortNodeRequired.emit('date')


@singleton
class ModelProjectNodeTreeViewDockPane(QtAds.CDockWidget, ZView):
    def __init__(self, parent=None):
        QtAds.CDockWidget.__init__(self, '', parent)
        ZView.__init__(self)
        self.zViewTitle = 'Model'
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_ON_CLOSE, False)
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE, False)
        _widget = _ModelProjectNodeTreeView(self)
        self.setWidget(_widget)

    @ZView.title.setter
    def title(self, title):
        self.zViewTitle = title
        self.setWindowTitle(title)

    def set_view_manager(self, view_mgr):
        super().set_view_manager(view_mgr)
        if self.widget() and isinstance(self.widget(), ZView):
            self.widget().set_view_manager(view_mgr)
