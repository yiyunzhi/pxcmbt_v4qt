# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_node_nav_widget.py
# ------------------------------------------------------------------------------
#
# File          : class_node_nav_widget.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtGui, QtCore, QtWidgets
from ..core.define import EnumViewNavStyle, EnumNodeStyleProperty


class NodeNavigationDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        """
        Args:
            painter (QtGui.QPainter):
            option (QtGui.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        """
        if index.column() != 0:
            super(NodeNavigationDelegate, self).paint(painter, option, index)
            return
        _item = index.model().item(index.row(), index.column())
        _margin = 1.0, 1.0
        _rect = QtCore.QRectF(
            option.rect.x() + _margin[0],
            option.rect.y() + _margin[1],
            option.rect.width() - (_margin[0] * 2),
            option.rect.height() - (_margin[1] * 2)
        )
        painter.save()
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        # background.
        _bg_color = QtGui.QColor(*EnumViewNavStyle.ITEM_COLOR.value)
        _itm_color = QtGui.QColor(80, 128, 123)
        if option.state & QtWidgets.QStyle.StateFlag.State_Selected:
            _bg_color = _bg_color.lighter(120)
            _itm_color = QtGui.QColor(*EnumNodeStyleProperty.SELECTED_BORDER_COLOR.value)
        _roundness = 2.0
        painter.setBrush(_bg_color)
        painter.drawRoundedRect(_rect, _roundness, _roundness)
        if index.row() != 0:
            _txt_offset = 8.0
            _m = 6.0
            _x = _rect.left() + 2.0 + _m
            _y = _rect.top() + _m + 2
            _h = _rect.height() - (_m * 2) - 2
            painter.setBrush(_itm_color)
            for i in range(4):
                _itm_rect = QtCore.QRectF(_x, _y, 1.3, _h)
                painter.drawRoundedRect(_itm_rect, 1.0, 1.0)
                _x += 2.0
                _y += 2
                _h -= 4
        else:
            _txt_offset = 5.0
            _x = _rect.left() + 4.0
            _size = 10.0
            for clr in [QtGui.QColor(0, 0, 0, 80), _itm_color]:
                _itm_rect = QtCore.QRectF(_x, _rect.center().y() - (_size / 2), _size, _size)
                painter.setBrush(clr)
                painter.drawRoundedRect(_itm_rect, 2.0, 2.0)
                _size -= 5.0
                _x += 2.5
        # text
        _pen_color = option.palette.text().color()
        _pen = QtGui.QPen(_pen_color, 0.5)
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(_pen)

        _font = painter.font()
        _font_metrics = QtGui.QFontMetrics(_font)
        _item_text = _item.text().replace(' ', '_')
        if hasattr(_font_metrics, 'horizontalAdvance'):
            _font_width = _font_metrics.horizontalAdvance(_item_text)
        else:
            _font_width = _font_metrics.width(_item_text)
        _font_height = _font_metrics.height()
        _text_rect = QtCore.QRectF(
            _rect.center().x() - (_font_width / 2) + _txt_offset,
            _rect.center().y() - (_font_height / 2),
            _font_width, _font_height)
        painter.drawText(_text_rect, _item.text())
        painter.restore()


class NodeNavigationWidget(QtWidgets.QListView):
    sigNavigationChanged = QtCore.Signal(str, list)

    def __init__(self, parent=None):
        super(NodeNavigationWidget, self).__init__(parent)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setResizeMode(self.ResizeMode.Adjust)
        self.setViewMode(self.ViewMode.ListMode)
        self.setFlow(self.Flow.LeftToRight)
        self.setDragEnabled(False)
        self.setMinimumHeight(20)
        self.setMaximumHeight(36)
        self.setSpacing(0)
        # self.viewport().setAutoFillBackground(False)
        self.setStyleSheet(
            'QListView {{border: 0px;background-color: rgb({0},{1},{2});}}'
            .format(*EnumViewNavStyle.BACKGROUND_COLOR.value)
        )
        self.setItemDelegate(NodeNavigationDelegate(self))
        self.setModel(QtGui.QStandardItemModel())

    def keyPressEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        super(NodeNavigationWidget, self).mouseReleaseEvent(event)
        if not self.selectedIndexes():
            return
        _index = self.selectedIndexes()[0]
        _rows = reversed(range(1, self.model().rowCount()))
        if _index.row() == 0:
            _rows = [r for r in _rows if r > 0]
        else:
            _rows = [r for r in _rows if _index.row() < r]
        if not _rows:
            return
        _rm_node_ids = [self.model().item(r, 0).toolTip() for r in _rows]
        _node_id = self.model().item(_index.row(), 0).toolTip()
        [self.model().removeRow(r) for r in _rows]
        self.sigNavigationChanged.emit(_node_id, _rm_node_ids)

    def clear(self):
        self.model().sourceMode().clear()

    def add_label_item(self, label, node_id):
        _item = QtGui.QStandardItem(label)
        _item.setToolTip(node_id)
        _metrics = QtGui.QFontMetrics(_item.font())
        if hasattr(_metrics, 'horizontalAdvance'):
            _width = _metrics.horizontalAdvance(_item.text()) + 30
        else:
            _width = _metrics.width(_item.text()) + 30
        _item.setSizeHint(QtCore.QSize(_width, 20))
        self.model().appendRow(_item)
        self.selectionModel().setCurrentIndex(
            self.model().indexFromItem(_item),
            QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)

    def remove_label_item(self, node_id):
        _rows = reversed(range(1, self.model().rowCount()))
        _node_ids = [self.model().item(r, 0).toolTip() for r in _rows]
        if node_id not in _node_ids:
            return
        _index = _node_ids.index(node_id)
        if _index == 0:
            _rows = [r for r in _rows if r > 0]
        else:
            _rows = [r for r in _rows if _index < r]
        [self.model().removeRow(r) for r in _rows]
