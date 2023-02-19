from core.gui.qtimp import QtCore, QtGui, QtWidgets


class ElidingLabelMgr:
    def __init__(self, _this):
        '''
          init

        Parameters
        ----------
        _this : CElidingLabel
        '''
        self._this = _this
        self.elideMode = QtCore.Qt.TextElideMode.ElideNone
        self.text = ''
        self.isElided = False

    def elideText(self, width: int):
        '''
        Elide text

        Parameters
        ----------
        width : int
        '''
        if self.isModeElideNone():
            return

        _fm = self._this.fontMetrics()
        _text = _fm.elidedText(self.text, self.elideMode,
                               width - self._this.margin() * 2 - self._this.indent())
        if _text == "…":
            _text = self.text[0]
        _was_elided = self.isElided
        self.isElided = _text != self.text
        if self.isElided != _was_elided:
            self._this.sigElidedChanged.emit(self.isElided)
        QtWidgets.QLabel.setText(self._this,_text)

    def isModeElideNone(self) -> bool:
        '''
        Convenience function to check if the

        Returns
        -------
        value : bool
        '''
        return QtCore.Qt.TextElideMode.ElideNone == self.elideMode


class CElidingLabel(QtWidgets.QLabel):
    # This signal is emitted if the user clicks on the label (i.e. pressed down
    # then released while the mouse cursor is inside the label)
    sigClicked = QtCore.Signal()
    # This signal is emitted if the user does a double click on the label
    sigDoubleClicked = QtCore.Signal()
    sigElidedChanged = QtCore.Signal(bool)

    def __init__(self, text='', parent: QtWidgets.QWidget = None,
                 flags: QtCore.Qt.WindowFlags = QtCore.Qt.WindowFlags()):
        '''
        init

        Parameters
        ----------
        parent : QWidget
        flags : Qt.WindowFlags
        '''
        super().__init__(text, parent=parent, f=flags)
        self._mgr = ElidingLabelMgr(self)

        if text:
            self._mgr.text = text
            self.setToolTip(text)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        '''
        Mousereleaseevent

        Parameters
        ----------
        event : QMouseEvent
        '''
        super().mouseReleaseEvent(event)
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return

        self.sigClicked.emit()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        '''
        Resizeevent

        Parameters
        ----------
        event : QResizeEvent
        '''
        if not self._mgr.isModeElideNone():
            self._mgr.elideText(event.size().width())

        super().resizeEvent(event)

    def mouseDoubleClickEvent(self, ev: QtGui.QMouseEvent):
        '''
        Mousedoubleclickevent

        Parameters
        ----------
        ev : QMouseEvent
            Unused
        '''
        self.sigDoubleClicked.emit()
        super().mouseDoubleClickEvent(ev)

    def elideMode(self) -> QtCore.Qt.TextElideMode:
        '''
        Returns the text elide mode. The default mode is ElideNone

        Returns
        -------
        value : Qt.TextElideMode
        '''
        return self._mgr.elideMode

    def setElideMode(self, mode: QtCore.Qt.TextElideMode):
        '''
        Sets the text elide mode

        Parameters
        ----------
        mode : Qt.TextElideMode
        '''
        self._mgr.elideMode = mode
        self._mgr.elideText(self.size().width())

    def isElided(self):
        return self._mgr.isElided

    def minimumSizeHint(self) -> QtCore.QSize:
        '''
        Minimumsizehint

        Returns
        -------
        value : QSize
        '''
        if self.pixmap() is not None or self._mgr.isModeElideNone():
            return super().minimumSizeHint()

        _fm = self.fontMetrics()
        return QtCore.QSize(_fm.width(self._mgr.text[:2] + "…"), _fm.height())

    def sizeHint(self) -> QtCore.QSize:
        '''
        Sizehint

        Returns
        -------
        value : QSize
        '''
        _has_pm=not self.pixmap().isNull()
        if _has_pm or self._mgr.isModeElideNone():
            return super().sizeHint()
        # fixme: low qt version to compatible
        _fm = self.fontMetrics()
        return QtCore.QSize(_fm.horizontalAdvance(self._mgr.text), super().sizeHint().height())

    def setText(self, text: str):
        '''
        Settext

        Parameters
        ----------
        text : str
        '''
        if self._mgr.isModeElideNone():
            super().setText(text)
        else:
            self._mgr.text = text
            self.setToolTip(text)
            self._mgr.elideText(self.size().width())

    def text(self) -> str:
        '''
        Text

        Returns
        -------
        value : str
        '''
        return self._mgr.text
