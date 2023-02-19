# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : test_ZQtTreeModel.py
# ------------------------------------------------------------------------------
#
# File          : test_ZQtTreeModel.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import sys, anytree
from core.gui.qtimp import QtGui, QtWidgets, QtCore
from core.gui.core.class_qt_tree_model import ZQtTreeModelItem, ZQtTreeModel


def on_clicked(evt):
    print('clicked:', evt)


def on_db_clicked(evt):
    print('db clicked:', evt)


def add_node_at(evt, idx):
    _item = idx.internalPointer()
    _model.layoutAboutToBeChanged.emit()
    _item.addNewChild(parent=_item, column_attrs=_columns, label='%s_newChild' % _item.label)
    _model.layoutChanged.emit()
    print('add_node_at', _item.children)
    print(anytree.RenderTree(_model.rootItem))


def remove_node_at(evt, idx):
    _item = idx.internalPointer()
    _parent = _model.parent(idx).internalPointer()
    _model.beginRemoveRows(idx.parent(), idx.row(), idx.row())
    _res = _model.removeRow(idx.row(), idx.parent())
    _model.parent(idx).internalPointer().removeChild(_item)
    _model.endRemoveRows()
    print('remove_node_at', _res, anytree.RenderTree(_parent))


def on_cm_req(evt):
    print('on_cm_req:', view.indexAt(evt))
    _idx = view.indexAt(evt)
    # view.selectionModel().select(_idx, QtCore.QItemSelectionModel.SelectionFlag.SelectCurrent)
    _menu = QtWidgets.QMenu()
    _act = _menu.addAction('add')
    _act.triggered.connect(lambda x: add_node_at(x, _idx))
    _act = _menu.addAction('remove')
    _act.triggered.connect(lambda x: remove_node_at(x, _idx))
    _menu.exec(QtGui.QCursor.pos())


# todo: add node, delete node
# todo: serialize,deserialize

app = QtWidgets.QApplication(sys.argv)

_columns = ['label']
_node_root = ZQtTreeModelItem()

_node_1 = ZQtTreeModelItem(parent=_node_root, column_attrs=_columns, label='node_1', icon_path=('fa', 'ri.government-line'))
_node_2 = ZQtTreeModelItem(parent=_node_root, column_attrs=_columns, label='node_2')
_node_3 = ZQtTreeModelItem(parent=_node_root, column_attrs=_columns, label='node_3')
_node_4 = ZQtTreeModelItem(parent=_node_root, column_attrs=_columns, label='node_4')
_node_11 = ZQtTreeModelItem(parent=_node_1, column_attrs=_columns, label='node_11')
_node_12 = ZQtTreeModelItem(parent=_node_1, column_attrs=_columns, label='node_12')
_node_21 = ZQtTreeModelItem(parent=_node_2, column_attrs=_columns, label='node_21')
_node_31 = ZQtTreeModelItem(parent=_node_3, column_attrs=_columns, label='node_31')
_node_32 = ZQtTreeModelItem(parent=_node_3, column_attrs=_columns, label='node_32')
_node_33 = ZQtTreeModelItem(parent=_node_3, column_attrs=_columns, label='node_33')
_node_41 = ZQtTreeModelItem(parent=_node_4, column_attrs=_columns, label='node_41')
# _model.assignTree(_node_root)
_model = ZQtTreeModel(column_names=['col0'])
_model.assignTree(_node_root)

_model.setFlag(_model.index(1, 0, _model.index(2, 0)), QtCore.Qt.ItemFlag.ItemIsEnabled, False)
view = QtWidgets.QTreeView()
_model.iconProvider = view.style()
view.setModel(_model)
view.setWindowTitle('TreeModelTest')
view.setAlternatingRowColors(True)
view.setUniformRowHeights(True)  # Allows for scrolling optimizations.
header = view.header()
header.setStretchLastSection(False)
# header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
# header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
# view.setSelectionMode(QAbstractItemView.ExtendedSelection) #Multiselection with ctrl key
view.expandAll()
view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
view.clicked.connect(on_clicked)
view.doubleClicked.connect(on_db_clicked)
view.customContextMenuRequested.connect(on_cm_req)
view.show()
sys.exit(app.exec())
