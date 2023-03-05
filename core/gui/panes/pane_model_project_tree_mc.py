# -*- coding: utf-8 -*-
import addict
# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_model_project_tree_mc.py
# ------------------------------------------------------------------------------
#
# File          : pane_model_project_tree_mc.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import anytree
# todo: wrappe anytree
import typing
from core.application.class_application_context import ApplicationContext
from core.application.utils_helper import util_get_uuid_string
from core.application.mbt_solution_manager.solution import MBTSolution
from core.gui.qtimp import QtCore, QtGui
from core.gui.core.define import EnumLayoutModifierPolicy, EnumLayoutModifierTarget
from core.gui.core.class_base import ZViewManager, ZViewContentContainer, ZViewContent, ZViewModifier
from core.gui.core.class_qt_tree_model import ZQtTreeModel, ZQtTreeModelItem
from .pane_model_project_tree_view import _ModelProjectNodeTreeView

_appCtx: ApplicationContext = ApplicationContext()


class _ModelTreeModelItem(ZQtTreeModelItem):
    serializeTag = '!_ModelTreeModelItem'

    def __init__(self, **kwargs):
        ZQtTreeModelItem.__init__(self, **kwargs)

    def setData(self, column, value):
        if column == 0:
            if not value:
                return False
            _sibling_names = [x.label for x in self.siblings]
            if value in _sibling_names:
                return False
            else:
                self.label = value
        return True

    def setCheckedState(self, value):
        pass

    def addNewChild(self, **kwargs):
        _item = _ModelTreeModelItem(**kwargs)
        _item.setFlag(QtCore.Qt.ItemFlag.ItemIsEditable, True)
        return _item


class ModelProjectNodeTreeViewContent(ZViewContent):
    serializeTag = '!ModelProjectNodeTreeViewContent'

    def __init__(self, **kwargs):
        ZViewContent.__init__(self, container=kwargs.get('container'))
        self.treeModel = ZQtTreeModel(column_names=kwargs.get('column_names', ['items']))
        self._treeRoot = kwargs.get('tree_root')
        self._columns = ['label']
        if self._treeRoot is None:
            self._treeRoot = _ModelTreeModelItem()
            self.prototypesNode = _ModelTreeModelItem(parent=self._treeRoot, column_attrs=self._columns, label='prototypes', icon_path=['fa', 'ph.folders'],
                                                      readonly=True)
            self.abilitiesNode = _ModelTreeModelItem(parent=self._treeRoot, column_attrs=self._columns, label='abilities', icon_path=['fa', 'ph.folders'],
                                                     readonly=True)
        else:
            self.prototypesNode = anytree.find(self._treeRoot, lambda x: x.label == 'prototypes')
            self.abilitiesNode = anytree.find(self._treeRoot, lambda x: x.label == 'abilities')
        self.treeModel.assignTree(self._treeRoot)

    @property
    def serializer(self):
        return {'tree_root': self._treeRoot,
                'column_names': self.treeModel.column_names}

    def get_root_node(self):
        return self._treeRoot

    def remove_node_by_index(self, index: QtCore.QModelIndex):
        _item = index.internalPointer()
        _parent = self.treeModel.parent(index).internalPointer()
        self.treeModel.beginRemoveRows(index.parent(), index.row(), index.row())
        _res = self.treeModel.removeRow(index.row(), index.parent())
        self.treeModel.parent(index).internalPointer().removeChild(_item)
        self.treeModel.endRemoveRows()

    def add_prototype_node(self):
        self.treeModel.layoutAboutToBeChanged.emit()
        self.prototypesNode.addNewChild(parent=self.prototypesNode, column_attrs=self._columns, label='%s_newChild' % self.prototypesNode.label)
        self.treeModel.layoutChanged.emit()

    def add_ability_node(self, **options):
        self.treeModel.layoutAboutToBeChanged.emit()
        self.abilitiesNode.addNewChild(parent=self.abilitiesNode, column_attrs=self._columns, **options)
        self.treeModel.layoutChanged.emit()

    def get_ability_node_by_name(self, name):
        _res = None
        if self.abilitiesNode:
            _res = anytree.find(self.abilitiesNode, lambda x: x.label == name)
        return _res

    def get_prototype_node_by_name(self, name):
        _res = None
        if self.prototypesNode:
            _res = anytree.find(self.prototypesNode, lambda x: x.label == name)
        return _res


class ModelProjectNodeContentContainer(ZViewContentContainer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.defaultContent = ModelProjectNodeTreeViewContent(container=self)

    def get_root_node(self):
        if self._content is None:
            return None
        return self._content.get_root_node()

    def add_prototype_node(self, *args):
        self._content.add_prototype_node()

    def add_ability_node(self, **options):
        self._content.add_ability_node(**options)

    def remove_nodes(self, indexes: typing.List[QtCore.QModelIndex]):
        for x in indexes:
            self._content.remove_node_by_index(x)

    def is_ability_name_exist(self, name):
        return self._content.get_ability_node_by_name(name) is not None

    def is_prototype_name_exist(self, name):
        return self._content.get_prototype_node_by_name(name) is not None

    def transform_data(self):
        return self._content.treeModel


class NodeLabelChangedCmd(QtGui.QUndoCommand):
    """
    """

    def __init__(self, view_mgr, index: QtCore.QModelIndex, old_name):
        QtGui.QUndoCommand.__init__(self)
        self.setText('rename node')
        self.index = index
        self.viewMgr = view_mgr
        self.oldVal = old_name
        self.newVal = index.internalPointer().label

    def undo(self):
        if not self.index.isValid():
            return
        if self.oldVal != self.newVal:
            _model: QtCore.QAbstractItemModel = self.viewMgr.content_container.transform_data()
            _model.setData(self.index, self.oldVal)

    def redo(self):
        if not self.index.isValid():
            return
        _cur_v = self.index.internalPointer().label
        if _cur_v != self.newVal:
            self.index.internalPointer().label = self.newVal
        self.viewMgr.update_node_view_title(self.index.internalPointer())


class ModelProjectNodeTreeManager(ZViewManager):
    aliveWithProject = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._wire_signal()

    def _wire_signal(self):
        _e_view = self.get_effected_view()
        _e_view.sigAddNodeRequired.connect(self.on_item_add_required)
        _e_view.sigRemoveNodeRequired.connect(self.on_item_remove_required)
        _e_view.sigSortNodeRequired.connect(self.on_item_sort_required)
        _e_view.sigEditNodeRequired.connect(self.on_item_edit_required)
        _e_view.sigItemDoubleClicked.connect(self.on_item_double_clicked)
        _e_view.sigItemSelectionChanged.connect(self.on_item_selection_changed)

    def get_effected_view(self) -> _ModelProjectNodeTreeView:
        return self.view.widget()

    def get_toolbar_view(self):
        return self.view.widget().toolbar

    def get_root_nodes(self):
        _root_node_of_tree = self.content_container.get_root_node()
        if _root_node_of_tree is None:
            return None
        return _root_node_of_tree.children

    def _add_node(self, node, parent):
        pass

    def resolve_node_user_data(self, ud):
        _res = ud
        if isinstance(ud, str):
            if 'solution:' in ud:
                _, _slt_uid = ud.split(':')
                _res = _appCtx.mbt_solution_manager.get_solution_by_uuid(_slt_uid)
        else:
            raise ValueError('not supported user data type')
        return _res

    def is_valid_ability_name(self, name):
        return not self.content_container.is_ability_name_exist(name)

    def is_valid_prototype_name(self, name):
        return not self.content_container.is_prototype_name_exist(name)

    def on_item_add_required(self, item_type, item_info):
        if item_type == 'prototype':
            self.content_container.add_prototype_node()
        elif item_type == 'ability':
            self.content_container.add_ability_node(uuid=util_get_uuid_string(),
                                                    label=item_info.name,
                                                    icon_path=item_info.solution.icon_info,
                                                    user_data='solution:%s' % item_info.solution.uuid)

    def on_item_edit_required(self, index, old_value: object):
        self.on_item_renamed(index.internalPointer(), old_value)

    def on_item_remove_required(self, indexes: typing.List[QtCore.QModelIndex]):
        self.content_container.remove_nodes(indexes)
        self.sigChangeMainViewRequired.emit('removeViews', [x.internalPointer().uuid for x in indexes])

    def on_item_sort_required(self, sort_type: str):
        print('---->on_item_sort_required,', sort_type)

    def on_item_double_clicked(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return
        _node = index.internalPointer()
        _node_ud = _node.userData
        if _node_ud is None:
            return
        _node_ud = self.resolve_node_user_data(_node_ud)
        if isinstance(_node_ud, MBTSolution):
            _view_name = _node_ud.uuid
            if _view_name:
                _view_title = self.pathSep.join([x.view_title for x in self.path] + [x.label for x in _node.path if x.parent])
                _modify = ZViewModifier(view_name=_view_name,
                                        target=EnumLayoutModifierTarget.CENTER_WIDGET,
                                        policy=EnumLayoutModifierPolicy.APPEND,
                                        options={'view_id': _node.uuid,
                                                 'view_title': _view_title,
                                                 'manager_parent': self})
                self.sigChangeMainViewRequired.emit('viewModify', [_modify])

    def on_item_selection_changed(self, index):
        print('---->on_item_selection_changed,', index)

    def on_item_data_changed(self, tl_idx: QtCore.QModelIndex, br_idx: QtCore.QModelIndex, roles: [], old_value):
        if tl_idx.column() == 0:
            self.on_item_renamed(tl_idx, old_value)

    def on_item_renamed(self, index: QtCore.QModelIndex, old_name):
        self._undoStack.push(NodeLabelChangedCmd(self, index, old_name))

    def update_node_view_title(self, node):
        _view_id = node.uuid
        _view_title = self.pathSep.join([x.view_title for x in self.path] + [x.label for x in node.path if x.parent])
        self.sigChangeMainViewRequired.emit('setViewTitle', {_view_id: _view_title})

    def set_content(self, content: ZViewContent):
        super().set_content(content)
        _tree_model = self.content_container.transform_data()
        self.view.widget().treeView.setModel(_tree_model)
        _tree_model.sigDataChanged.connect(self.on_item_data_changed)

    def restore_content(self):
        pass

    def ensure_view(self):
        if self.view is None:
            return
