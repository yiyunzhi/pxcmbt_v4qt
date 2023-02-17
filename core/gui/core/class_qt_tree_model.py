# -*- coding: utf-8 -*-
import types

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_qt_tree_model.py
# ------------------------------------------------------------------------------
#
# File          : class_qt_tree_model.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from typing import Union, Any
from core.application.class_tree import UUIDTreeNode
from gui import QtCore, QtGui
from gui.core.class_base import ThemeStyledUiObject


class ZQtTreeModelItem(UUIDTreeNode, ThemeStyledUiObject):
    def __init__(self, **kwargs):
        ThemeStyledUiObject.__init__(self)
        UUIDTreeNode.__init__(self, **kwargs)
        self.parent = kwargs.get('parent')
        self.label = kwargs.get('label', 'newNode')
        self.iconPath = kwargs.get('icon_path', ('fa', 'ri.file-line'))
        self.iconColor = kwargs.get('icon_color', '#777')
        self.columnAttrs = kwargs.get('column_attrs', [])
        self.flags = kwargs.get('flags', QtCore.Qt.ItemFlag.ItemIsEnabled
                                | QtCore.Qt.ItemFlag.ItemIsSelectable
                                )
        self.iconUsageRegistry.register(self, *self.iconPath)

    def __repr__(self):
        return 'label={}'.format(self.label)

    def __str__(self):
        return self.__repr__()

    def addChild(self, child):
        child.parent = self

    def addNewChild(self, **kwargs):
        return ZQtTreeModelItem(**kwargs)

    def removeChild(self, child):
        if child in self.children:
            child.parent = None
            del child

    def pathInStr(self):
        return self.separator.join([str(x) for x in self.path])

    def _column2attr(self, column_idx: int):
        if column_idx > len(self.columnAttrs) - 1:
            return None
        _attr = self.columnAttrs[column_idx]
        if hasattr(self, _attr):
            _attr = getattr(self, _attr)
            return str(_attr) if type(_attr) != types.MethodType else _attr()
        else:
            return None

    def setCheckedState(self, value):
        raise NotImplementedError

    def getCheckedState(self):
        return QtCore.Qt.CheckState.Unchecked

    def child(self, row):
        try:
            return self.children[row]
        except IndexError:
            return None

    def hasFlag(self, flag):
        return flag & self.flags == flag

    def setFlag(self, flag: QtCore.Qt.ItemFlag, on: bool):
        if on:
            self.flags |= flag
        else:
            self.flags &= ~flag

    def childCount(self):
        return len(self.children)

    def columnCount(self):
        return len(self.columnAttrs)

    def data(self, column: int):
        try:
            return self._column2attr(column)
        except IndexError:
            return None

    def setData(self, column, value):
        raise NotImplementedError

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def getColumnDataByRole(self, column: int, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.data(column)
        elif role == QtCore.Qt.ItemDataRole.CheckStateRole and self.hasFlag(QtCore.Qt.ItemFlag.ItemIsUserCheckable):
            return self.getCheckedState()
        elif role == QtCore.Qt.ItemDataRole.DecorationRole:
            _icon = self.iconUsageRegistry.get_icon(self, color=self.iconColor)
            return _icon

    def on_theme_changed(self, **msg_data):
        _palette: QtGui.QPalette = msg_data.get('palette')
        if _palette is not None:
            self.iconUsageRegistry.get_icon(self, force=True, color=_palette.text().color())


class ZQtTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, tree_item: ZQtTreeModelItem = None, column_names: list = [], parent=None):
        super().__init__(parent)
        self._columnNames = column_names
        if tree_item is not None:
            self.rootItem = tree_item.root
        else:
            self.rootItem = ZQtTreeModelItem()
        self.iconProvider = None

    def assignTree(self, tree_node: ZQtTreeModelItem):
        self.rootItem = tree_node.root

    def columnCount(self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex]) -> int:
        if index.isValid():
            _node=index.internalPointer()
            if _node is not None:
                return index.internalPointer().columnCount()
            else:
                print('columnCount:',_node)
                return len(self._columnNames)
        else:
            return len(self._columnNames)

    def data(self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex], role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        _item = index.internalPointer()
        if _item is None:
            print('data:', index,role)
            return
        # if role == QtCore.Qt.ItemDataRole.DecorationRole:
        #     return QtGui.QIcon(self.iconProvider.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon))
        # else:
        return _item.getColumnDataByRole(index.column(), role)

    def setData(self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex], value: Any, role: int = QtCore.Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False
        _item = index.internalPointer()
        if _item is None:
            return False
        return _item.setData(index.column(), value)

    def flags(self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex]) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        _item = index.internalPointer()
        if _item is None:
            return QtCore.Qt.ItemFlag.NoItemFlags
        return _item.flags

    def setFlag(self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex], flag: QtCore.Qt.ItemFlag, on: bool):
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        _item = index.internalPointer()
        if _item is None:
            return
        _item.setFlag(flag, on)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = 0) -> Any:
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self._columnNames[section]
        return None

    def index(self, row: int, column: int, parent_index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = None) -> QtCore.QModelIndex:
        if row < 0 or column < 0: return QtCore.QModelIndex()
        if parent_index is None:
            _parent_item = self.rootItem
        else:
            if parent_index.isValid():
                if not self.hasIndex(row, column, parent_index):
                    return QtCore.QModelIndex()
                _parent_item = parent_index.internalPointer()
            else:
                _parent_item = self.rootItem
        if _parent_item is None:
            print('data:', row,column,parent_index)
            return QtCore.QModelIndex()
        _child_item = _parent_item.child(row)
        if _child_item:
            return self.createIndex(row, column, _child_item)
        return QtCore.QModelIndex()

    def parent(self, child_index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex]) -> QtCore.QModelIndex:
        if child_index is None or not child_index.isValid():
            return QtCore.QModelIndex()
        _child_item = child_index.internalPointer()
        _parent_item = _child_item.parent
        if _parent_item == self.rootItem:
            return QtCore.QModelIndex()
        elif _parent_item is None:
            print('parent:', child_index)
            return QtCore.QModelIndex()
        else:
            return self.createIndex(_parent_item.row(), 0, _parent_item)

    def rowCount(self, parent_index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex]) -> int:
        if parent_index.column() > 0:
            return 0
        if not parent_index.isValid():
            _parent_item = self.rootItem
        else:
            _parent_item = parent_index.internalPointer()
        if _parent_item is None:
            print('parent:', parent_index)
            return 0
        return _parent_item.childCount()
