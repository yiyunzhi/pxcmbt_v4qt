# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_search_completer.py
# ------------------------------------------------------------------------------
#
# File          : class_search_completer.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import re
from collections import OrderedDict
from gui import QtCore, QtWidgets, QtGui
from ..core.define import EnumViewFeature, EnumViewNavStyle


class SearchCompleter(QtWidgets.QCompleter):
    """
    QCompleter adapted from:
    https://stackoverflow.com/questions/5129211/qcompleter-custom-completion-rules
    """

    def __init__(self, nodes=None, parent=None):
        super(SearchCompleter, self).__init__(nodes, parent)
        self.setCompletionMode(self.CompletionMode.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._localCompletionPrefix = ''
        self._usingOrigModel = False
        self._sourceModel = None
        self._filterModel = None

    def splitPath(self, path):
        self._localCompletionPrefix = path
        self.updateModel()

        if self._filterModel.rowCount() == 0:
            self._usingOrigModel = False
            self._filterModel.setSourceModel(QtCore.QStringListModel([]))
            return []
        return []

    def updateModel(self):
        if not self._usingOrigModel:
            self._filterModel.setSourceModel(self._sourceModel)

        _pattern = QtCore.QRegularExpression(self._localCompletionPrefix,
                                             QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption)
        self._filterModel.setFilterRegExp(_pattern)

    def setModel(self, model):
        self._sourceModel = model
        self._filterModel = QtCore.QSortFilterProxyModel(self)
        self._filterModel.setSourceModel(self._sourceModel)
        super(SearchCompleter, self).setModel(self._filterModel)
        self._usingOrigModel = True


class SearchLineEditWidget(QtWidgets.QLineEdit):
    sigTabPressed = QtCore.Signal()

    def __init__(self, parent=None):
        super(SearchLineEditWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setMinimumSize(200, 22)

    def keyPressEvent(self, event):
        super(SearchLineEditWidget, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key.Key_Tab:
            self.sigTabPressed.emit()


class SearchMenuWidget(QtWidgets.QMenu):
    sigSearchSubmitted = QtCore.Signal(str)

    def __init__(self, node_dict=None):
        super(SearchMenuWidget, self).__init__()

        self.lineEdit = SearchLineEditWidget()
        self.lineEdit.sigTabPressed.connect(self._close)

        self._nodeDict = node_dict or {}
        if self._nodeDict:
            self._generate_items_from_node_dict()

        _search_widget = QtWidgets.QWidgetAction(self)
        _search_widget.setDefaultWidget(self.lineEdit)
        self.addAction(_search_widget)

        self._actions = {}
        self._menus = {}
        self._searchedActions = []

        self._blockSubmit = False

        self.rebuild = False

        self._wire_signals()

    def __repr__(self):
        return '<{} at {}>'.format(self.__class__.__name__, hex(id(self)))

    def keyPressEvent(self, event):
        super(SearchMenuWidget, self).keyPressEvent(event)
        self.lineEdit.keyPressEvent(event)

    @staticmethod
    def _fuzzy_finder(key, collection):
        _suggestions = []
        _pattern = '.*?'.join(key.lower())
        _regex = re.compile(_pattern)
        for item in collection:
            _match = _regex.search(item.lower())
            if _match:
                _suggestions.append((len(_match.group()), _match.start(), item))

        return [x for _, _, x in sorted(_suggestions)]

    def _wire_signals(self):
        self.lineEdit.returnPressed.connect(self._on_search_submitted)
        self.lineEdit.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        self._clear_actions()

        if not text:
            self._set_menu_visible(True)
            return

        self._set_menu_visible(False)

        _action_names = self._fuzzy_finder(text, self._actions.keys())

        self._searchedActions = [self._actions[name] for name in _action_names]
        self.addActions(self._searchedActions)

        if self._searchedActions:
            self.setActiveAction(self._searchedActions[0])

    def _clear_actions(self):
        for action in self._searchedActions:
            self.removeAction(action)
            action.triggered.connect(self._on_search_submitted)
        del self._searchedActions[:]

    def _set_menu_visible(self, visible):
        for menu in self._menus.values():
            menu.menuAction().setVisible(visible)

    def _close(self):
        self._set_menu_visible(False)
        self.setVisible(False)
        self.menuAction().setVisible(False)
        self._blockSubmit = True

    def _show(self):
        self.lineEdit.setText("")
        self.lineEdit.setFocus()
        self._set_menu_visible(True)
        self._blockSubmit = False
        self.exec_(QtGui.QCursor.pos())

    def _on_search_submitted(self):
        if not self._blockSubmit:
            _action = self.sender()
            if type(_action) is not QtGui.QAction:
                if len(self._searchedActions) > 0:
                    _action = self._searchedActions[0]
                else:
                    self._close()
                    return

            _text = _action.text()
            _node_type = self._nodeDict.get(_text)
            if _node_type:
                self.sigSearchSubmitted.emit(_node_type)

        self._close()

    def build_menu_tree(self):
        _node_types = sorted(self._nodeDict.values())
        _node_names = sorted(self._nodeDict.keys())
        _menu_tree = OrderedDict()

        _max_depth = 0
        for node_type in _node_types:
            _trees = '.'.join(node_type.split('.')[:-1]).split('::')
            for depth, menu_name in enumerate(_trees):
                _new_menu = None
                _menu_path = '::'.join(_trees[:depth + 1])
                if depth in _menu_tree.keys():
                    if menu_name not in _menu_tree[depth].keys():
                        _new_menu = QtWidgets.QMenu(menu_name)
                        _new_menu.keyPressEvent = self.keyPressEvent
                        _menu_tree[depth][_menu_path] = _new_menu
                else:
                    _new_menu = QtWidgets.QMenu(menu_name)
                    _menu_tree[depth] = {_menu_path: _new_menu}
                if depth > 0 and _new_menu:
                    _new_menu.parentPath = '::'.join(_trees[:depth])

                _max_depth = max(_max_depth, depth)
        if _menu_tree:
            for i in range(_max_depth + 1):
                _menus = _menu_tree[i]
                for menu_path, menu in _menus.items():
                    self._menus[menu_path] = menu
                    if i == 0:
                        self.addMenu(menu)
                    else:
                        _parent_menu = self._menus[menu.parentPath]
                        _parent_menu.addMenu(menu)

        for name in _node_names:
            _action = QtGui.QAction(name, self)
            _action.setText(name)
            _action.triggered.connect(self._on_search_submitted)
            self._actions[name] = _action

            _menu_name = self._nodeDict[name]
            _menu_path = '.'.join(_menu_name.split('.')[:-1])

            if _menu_path in self._menus.keys():
                self._menus[_menu_path].addAction(_action)
            else:
                self.addAction(_action)

    def set_nodes(self, node_dict=None):
        if not self._nodeDict or self.rebuild:
            self._nodeDict.clear()
            self._clear_actions()
            self._set_menu_visible(False)
            for menu in self._menus.values():
                self.removeAction(menu.menuAction())
            self._actions.clear()
            self._menus.clear()
            for name, node_types in node_dict.items():
                if len(node_types) == 1:
                    self._nodeDict[name] = node_types[0]
                    continue
                for node_id in node_types:
                    self._nodeDict['{} ({})'.format(name, node_id)] = node_id
            self.build_menu_tree()
            self.rebuild = False

        self._show()
