import logging
from typing import TYPE_CHECKING
import math
from PySide6 import QtCore, QtGui, QtWidgets

from ..define import EnumDragState
from ..eliding_label import CElidingLabel
from ..util import setButtonIcon, createTransparentPixmap, repolishStyle, EnumRepolishChildOptions

if TYPE_CHECKING:
    from ..floating_dock_container import CFloatingDockContainer

logger = logging.getLogger(__name__)


class FloatingWidgetTitleBarPrivate:
    _this: 'CFloatingWidgetTitleBar'
    iconLabel: QtWidgets.QLabel
    titleLabel: CElidingLabel
    closeButton: QtWidgets.QToolButton
    maximizeButton: QtWidgets.QToolButton
    floatingWidget: 'CFloatingDockContainer'
    dragState: EnumDragState
    maximizeIcon: QtGui.QIcon
    normalIcon: QtGui.QIcon
    maximized: bool

    def __init__(self, _this: 'FloatingWidgetTitleBar'):
        '''
        Private data constructor

        Parameters
        ----------
        _this : FloatingWidgetTitleBar
        '''
        self._this = _this
        self.iconLabel = None
        self.titleLabel = None
        self.closeButton = None
        self.maximizeButton = None
        self.floatingWidget = None
        self.dragState = EnumDragState.INACTIVE
        self.maximizeIcon = None
        self.normalIcon = None
        self.maximized = False

    def createLayout(self):
        '''
        Creates the complete layout including all controls
        '''
        self.titleLabel = CElidingLabel()
        self.titleLabel.setElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.titleLabel.setText("DockWidget->windowTitle()")
        self.titleLabel.setObjectName("floatingTitleLabel")
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft
                                     | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.closeButton = QtWidgets.QToolButton()
        self.closeButton.setObjectName("floatingTitleCloseButton")
        self.closeButton.setAutoRaise(True)

        self.maximizeButton = QtWidgets.QToolButton()
        self.maximizeButton.setObjectName("floatingTitleMaximizeButton")
        self.maximizeButton.setAutoRaise(True)

        _close_icon = QtGui.QIcon()
        _normal_pxm = self._this.style().standardPixmap(QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton, 0, self.closeButton)
        _close_icon.addPixmap(_normal_pxm, QtGui.QIcon.Mode.Normal)
        _close_icon.addPixmap(createTransparentPixmap(_normal_pxm, 0.25), QtGui.QIcon.Mode.Disabled)

        self.closeButton.setIcon(self._this.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton))
        self.closeButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.closeButton.setVisible(True)
        self.closeButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.closeButton.clicked.connect(self._this.sigCloseRequested)

        self._this.setMaximizedIcon(False)
        self.maximizeButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,
                                          QtWidgets.QSizePolicy.Policy.Fixed)
        self.maximizeButton.setVisible(True)
        self.maximizeButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.maximizeButton.clicked.connect(self._this.sigMaximizeRequested)

        _fm = QtGui.QFontMetrics(self.titleLabel.font())
        _spacing = round(_fm.height() / 4.0)

        # Fill the layout
        _layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.LeftToRight)
        _layout.setContentsMargins(6, 0, 0, 0)
        _layout.setSpacing(0)
        self._this.setLayout(_layout)
        _layout.addWidget(self.titleLabel, 1)
        _layout.addSpacing(_spacing)
        _layout.addWidget(self.maximizeButton)
        _layout.addWidget(self.closeButton)
        _layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setVisible(True)


class CFloatingWidgetTitleBar(QtWidgets.QFrame):
    sigCloseRequested = QtCore.Signal()
    sigMaximizeRequested = QtCore.Signal()

    def __init__(self, parent: 'CFloatingDockContainer'):
        super().__init__(parent)
        self._mgr = FloatingWidgetTitleBarPrivate(self)
        self._mgr.floatingWidget = parent
        self._mgr.createLayout()
        _normal_pxmp = self.style().standardPixmap(QtWidgets.QStyle.StandardPixmap.SP_TitleBarNormalButton, 0, self._mgr.maximizeButton)
        self._mgr.normalIcon.addPixmap(_normal_pxmp, QtGui.QIcon.Mode.Normal)
        self._mgr.normalIcon.addPixmap(createTransparentPixmap(_normal_pxmp, 0.25), QtGui.QIcon.Mode.Disabled)

        _max_pxmp = self.style().standardPixmap(QtWidgets.QStyle.StandardPixmap.SP_TitleBarMaxButton, 0, self._mgr.maximizeButton)
        self._mgr.normalIcon.addPixmap(_max_pxmp, QtGui.QIcon.Mode.Normal)
        self._mgr.normalIcon.addPixmap(createTransparentPixmap(_max_pxmp, 0.25), QtGui.QIcon.Mode.Disabled)
        self.setMaximizedIcon(self._mgr.maximized)

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            self._mgr.dragState = EnumDragState.FLOATING_WIDGET
            self._mgr.floatingWidget.startDragging(
                ev.pos(), self._mgr.floatingWidget.size(), self)
            return

        super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent):
        logger.debug('FloatingWidgetTitleBar.mouseReleaseEvent')
        self._mgr.dragState = EnumDragState.INACTIVE
        if self._mgr.floatingWidget is not None:
            self._mgr.floatingWidget.finishDragging()
        super().mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent):
        if not (ev.buttons() & QtCore.Qt.MouseButton.LeftButton) or self._mgr.dragState == EnumDragState.INACTIVE:
            self._mgr.dragState = EnumDragState.INACTIVE
            super().mouseMoveEvent(ev)
            return
        if self._mgr.dragState == EnumDragState.FLOATING_WIDGET:
            # Move floating window
            if self._mgr.floatingWidget.isMaximized():
                self._mgr.floatingWidget.showNormal(True)
            self._mgr.floatingWidget.moveFloating()
            super().mouseMoveEvent(ev)
            return
        super().mouseMoveEvent(ev)

    def enableCloseButton(self, enable: bool):
        self._mgr.closeButton.setEnabled(enable)

    def setTitle(self, text: str):
        self._mgr.titleLabel.setText(text)

    def updateStyle(self):
        repolishStyle(self, EnumRepolishChildOptions.RepolishDirectChildren)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.sigMaximizeRequested.emit()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def setMaximizedIcon(self, maximized: bool):
        self._mgr.maximized = maximized
        if maximized:
            self._mgr.maximizeButton.setIcon(self._mgr.normalIcon)
        else:
            self._mgr.maximizeButton.setIcon(self._mgr.maximizeIcon)

    def setMaximizeIcon(self, icon: QtGui.QIcon):
        self._mgr.maximizeIcon = icon
        if self._mgr.maximized:
            self.setMaximizedIcon(self._mgr.maximized)

    def setNormalIcon(self, icon: QtGui.QIcon):
        self._mgr.normalIcon = icon
        if not self._mgr.maximized:
            self.setMaximizedIcon(self._mgr.maximized)

    def maximizeIcon(self):
        return self._mgr.maximizeIcon

    def normalIcon(self):
        return self._mgr.normalIcon
