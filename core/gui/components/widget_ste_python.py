# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_ste_python.py
# ------------------------------------------------------------------------------
#
# File          : widget_ste_python.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import keyword
from core.gui.qtimp import QtGui, QtCore, QtWidgets
from .widget_ste import STETextEdit, STENumberBar


def _ste_font_format(color, style=''):
    '''Return a QTextCharFormat with the given attributes.
    '''
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Weight.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    if 'italicbold' in style:
        _format.setFontItalic(True)
        _format.setFontWeight(QtGui.QFont.Weight.Bold)
    return _format


_ste_mybrawn = ("#7E5916")
# Syntax styles that can be shared by all languages
_STE_STYLES = {
    'keyword': _ste_font_format('#CC7832', 'bold'),
    'operator': _ste_font_format('#9575CD'),
    'brace': _ste_font_format('darkred'),
    'defclass': _ste_font_format('#26A69A', 'bold'),
    'classes': _ste_font_format('#00897B', 'bold'),
    'Qtclass': _ste_font_format('black', 'bold'),
    'string': _ste_font_format(_ste_mybrawn),
    'string2': _ste_font_format('#629755', 'italic'),
    'comment': _ste_font_format('#629755', 'italic'),
    'self': _ste_font_format('#D63030', 'italicbold'),
    'selfnext': _ste_font_format('#2e3436', 'bold'),
    'Qnext': _ste_font_format('#2e3436', 'bold'),
    'numbers': _ste_font_format('#90A4AE'),
}


class STEPythonHighlighter(QtGui.QSyntaxHighlighter):
    '''Syntax highlighter for the Python language.
    '''
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'super', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]
    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]
    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)
        _tri = ("'''")
        _trid = ('"""')
        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QtCore.QRegularExpression(_tri), 1, _STE_STYLES['string2'])
        self.tri_double = (QtCore.QRegularExpression(_trid), 2, _STE_STYLES['string2'])
        _rules = []
        # Keyword, operator, and brace rules
        _rules += [(r'\b%s\b' % w, 0, _STE_STYLES['keyword'])
                   for w in self.keywords]
        _rules += [(r'%s' % o, 0, _STE_STYLES['operator'])
                   for o in self.operators]
        _rules += [(r'%s' % b, 0, _STE_STYLES['brace'])
                   for b in self.braces]
        # All other rules
        _rules += [
            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, _STE_STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, _STE_STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, _STE_STYLES['numbers']),

            # 'self'
            (r'\bself\b', 0, _STE_STYLES['self']),

            # Double-quoted string, possibly containing escape sequences ### "\"([^\"]*)\"" ### "\"(\\w)*\""
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, _STE_STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, _STE_STYLES['string']),

            # 'def' followed by a word
            (r'\bdef\b\s*(\w+)', 1, _STE_STYLES['defclass']),  ### (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),

            # 'self.' followed by a word
            (r'\bself\b)', 1, _STE_STYLES['selfnext']),  ### (r'\bself.\b\s*(\w+)', 1, STYLES['selfnext']),

            # 'Q' followed by a word
            (r'\b[Q.]\b\s*(\w+)', 1, _STE_STYLES['Qnext']),

            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, _STE_STYLES['classes']),

            # From '#' until a newline
            (r'#[^\n]*', 0, _STE_STYLES['comment']),

            # 'Q'  word
            # (r'\\bQ[A-Za-z]+\\b', 1, STYLES['Qtclass']), #(QRegExp("\\bQ[A-Za-z]+\\b")
        ]
        # Build a QRegExp for each pattern
        self.rules = [(QtCore.QRegularExpression(pat), index, fmt) for (pat, index, fmt) in _rules]

    def highlightBlock(self, text):
        # Apply syntax highlighting to the given block of text.
        # Do other syntax formatting
        for expression, nth, format_ in self.rules:
            _match = expression.match(text, 0)
            _index = _match.capturedStart()
            while _index >= 0:
                _index = _match.capturedStart(nth)
                _length = _match.capturedLength()
                self.setFormat(_index, _length, format_)
                _match = expression.match(text, _index + _length)
                _index = _match.capturedStart()

        self.setCurrentBlockState(0)
        # Do multi-line strings
        _in_multiline = self.match_multiline(text, *self.tri_single)
        if not _in_multiline:
            _in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        '''Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegularExpression`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        '''
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            _start = 0
            _len = 0
        # Otherwise, look for the delimiter on this line
        else:
            _match = delimiter.match(text)
            _start = _match.capturedStart()
            # Move past this match
            _len = _match.capturedLength()
        # As long as there's a delimiter match on this line...
        while _start >= 0:
            # Look for the ending delimiter
            _match = delimiter.match(text, _start + _len)
            _end = _match.capturedEnd()
            # Ending delimiter on this line?
            if _end >= _len:
                _length = _end - _start + _len + _match.capturedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                _length = len(text) - _start + _len
            # Apply formatting
            self.setFormat(_start, _length, style)
            # Look for the next match
            _match = delimiter.match(text, _start + _length)
            _start = _match.capturedStart()
        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


class PythonSTE(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.editor = STETextEdit(self)
        self.lnWidget = STENumberBar(self.editor)
        self.highlighter = STEPythonHighlighter(self.editor.document())
        self.completer = None
        self._init_completer()
        # layout
        self.mainLayout.addWidget(self.lnWidget)
        self.mainLayout.setSpacing(1)
        self.mainLayout.addWidget(self.editor)
        self.setLayout(self.mainLayout)
        self.editor.setFocus()

    def _init_completer(self):
        self.completer = QtWidgets.QCompleter(self.editor)
        self.completer.setModel(self._init_keyword_model())
        self.completer.setModelSorting(QtWidgets.QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setWrapAround(False)
        self.completer.setCompletionRole(QtCore.Qt.ItemDataRole.EditRole)
        self.editor.setCompleter(self.completer)

    def _init_keyword_model(self):
        return QtCore.QStringListModel(keyword.kwlist, self.completer)
