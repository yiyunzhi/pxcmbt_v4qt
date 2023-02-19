# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_ste.py
# ------------------------------------------------------------------------------
#
# File          : widget_ste.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtGui, QtCore, QtWidgets

lineBarColor = QtGui.QColor("#eeeeee")
lineHighlightColor = QtGui.QColor("#fce94f")
tab = chr(9)
eof = "\n"
iconsize = QtCore.QSize(16, 16)


#####################################################################
class STETextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super(STETextEdit, self).__init__(parent)
        self.installEventFilter(self)
        self._completer = None
        self.setStyleSheet("""
        QPlainTextEdit:focus{
                border: 1px solid #B4BBC3;
            }
        QPlainTextEdit {
                border: 1px solid transparent;
        }
        """)

    def setCompleter(self, c):
        if self._completer is not None:
            self._completer.activated.disconnect()
        self._completer = c
        #c.popup().setStyleSheet("background-color: #555753; color: #eeeeec; font-size: 8pt; selection-background-color: #4e9a06;")
        c.setWidget(self)
        c.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        c.activated.connect(self.insertCompletion)

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return
        _tc = self.textCursor()
        _extra = len(completion) - len(self._completer.completionPrefix())
        _tc.movePosition(QtGui.QTextCursor.MoveOperation.Left)
        _tc.movePosition(QtGui.QTextCursor.MoveOperation.EndOfWord)
        _tc.insertText(completion[-_extra:])
        self.setTextCursor(_tc)

    def textUnderCursor(self):
        _tc = self.textCursor()
        _tc.select(QtGui.QTextCursor.SelectionType.WordUnderCursor)
        return _tc.selectedText()

    def focusInEvent(self, e):
        if self._completer is not None and self._completer.widget() is not self:
            self._completer.setWidget(self)
        super(STETextEdit, self).focusInEvent(e)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key.Key_Tab:
            self.textCursor().insertText("    ")
            return
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return):
                e.ignore()
                # Let the completer do default behavior.
                return

        _is_shortcut = ((e.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier) != 0 and e.key() == QtCore.Qt.Key.Key_Escape)
        if self._completer is None or not _is_shortcut:
            # Do not process the shortcut when we have a completer.
            super(STETextEdit, self).keyPressEvent(e)

        _ctrl_or_shift = e.modifiers() & (QtCore.Qt.KeyboardModifier.ControlModifier | QtCore.Qt.KeyboardModifier.ShiftModifier)
        if self._completer is None or (_ctrl_or_shift and len(e.text()) == 0):
            return

        _eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        _has_modifier = (e.modifiers() != QtCore.Qt.KeyboardModifier.NoModifier) and not _ctrl_or_shift
        _completion_prefix = self.textUnderCursor()

        if not _is_shortcut and (_has_modifier or len(e.text()) == 0 or e.text()[-1] in _eow or len(_completion_prefix) < 0):
            self._completer.popup().hide()
            return

        if _completion_prefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(_completion_prefix)
            self._completer.popup().setCurrentIndex(
                self._completer.completionModel().index(0, 0))

        _cr = self.cursorRect()
        _cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(_cr)


class STENumberBar(QtWidgets.QWidget):
    def __init__(self, parent: STETextEdit = None):
        super(STENumberBar, self).__init__(parent)
        self.editor = parent
        self.editor.blockCountChanged.connect(self.update_width)
        self.editor.updateRequest.connect(self.update_on_scroll)
        self.update_width('1')

    def update_on_scroll(self, rect, scroll):
        if self.isVisible():
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update()

    def update_width(self, string):
        _width = self.fontMetrics().boundingRect(str(string)).width() + 8
        if self.width() != _width:
            self.setFixedWidth(_width)

    def paintEvent(self, event):
        if self.isVisible():
            _block = self.editor.firstVisibleBlock()
            _height = self.fontMetrics().height()
            _number = _block.blockNumber()
            _painter = QtGui.QPainter(self)
            _painter.fillRect(event.rect(), lineBarColor)
            #_painter.drawRect(0, 0, event.rect().width() - 1, event.rect().height() - 1)
            _font = _painter.font()
            _current_block = self.editor.textCursor().block().blockNumber() + 1
            _condition = True
            while _block.isValid() and _condition:
                _block_geometry = self.editor.blockBoundingGeometry(_block)
                _offset = self.editor.contentOffset()
                _block_top = _block_geometry.translated(_offset).top()
                _number += 1
                rect = QtCore.QRect(0, _block_top + 2, self.width() - 5, _height)
                if _number == _current_block:
                    _font.setBold(True)
                else:
                    _font.setBold(False)
                _painter.setFont(_font)
                _painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignRight, '%i' % _number)
                if _block_top > event.rect().bottom():
                    _condition = False
                _block = _block.next()
            _painter.end()




