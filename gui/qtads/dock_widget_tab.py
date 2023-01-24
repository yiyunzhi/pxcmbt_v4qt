from typing import TYPE_CHECKING, no_type_check
import logging
from PySide6 import QtCore, QtGui, QtWidgets

from .floating_drag_preview import CFloatingDragPreview
from .util import (startDragDistance, setButtonIcon,
                   getQApp, evtDockedWidgetDragStartEvent,
                   evtFloatingWidgetDragStartEvent, globalPositionOf,
                   repolishStyle, EnumRepolishChildOptions)
from .define import (EnumDragState,
                     EnumDockFlags,
                     EnumDockWidgetArea,
                     EnumDockMgrConfigFlag,
                     DOCK_MANAGER_DEFAULT_CONFIG,
                     AUTO_HIDE_DEFAULT_CONFIG,
                     EnumAutoHideFlag,
                     EnumSideBarLocation,
                     EnumDockWidgetFeature,
                     EnumADSIcon)
from .eliding_label import CElidingLabel

if TYPE_CHECKING:
    from .dock_manager import CDockManager
    from .dock_widget import CDockWidget
    from .dock_area_widget import CDockAreaWidget
    from .floating_dock_container import CFloatingDockContainer

logger = logging.getLogger(__name__)


class DockWidgetTabMgr:
    _this: 'CDockWidgetTab'
    dockWidget: 'CDockWidget'
    iconLabel: QtWidgets.QLabel
    titleLabel: QtWidgets.QLabel
    globalDragStartMousePosition: QtCore.QPoint
    dragStartMousePosition: QtCore.QPoint
    isActiveTab: bool
    dockArea: 'CDockAreaWidget'
    dragState: EnumDragState
    floatingWidget: 'IFloatingWidget'
    icon: QtGui.QIcon
    closeButton: QtWidgets.QPushButton
    iconTextSpacer: QtWidgets.QSpacerItem
    tabDragStartPosition: QtCore.QPoint
    iconSize: QtCore.QSize

    @no_type_check
    def __init__(self, _this: 'CDockWidgetTab'):
        '''
        Private data constructor

        Parameters
        ----------
        _this : DockWidgetTab
        '''
        self._this = _this
        self.dockWidget = None
        self.iconLabel = None
        self.titleLabel = None
        self.globalDragStartMousePosition = None
        self.dragStartMousePosition = None
        self.isActiveTab = False
        self.dockArea = None
        self.dragState = EnumDragState.INACTIVE
        self.floatingWidget = None
        self.icon = None
        self.closeButton = None
        self.iconTextSpacer = None
        self.tabDragStartPosition = None
        self.iconSize = None

    def createCloseButton(self):
        if EnumDockMgrConfigFlag.TabCloseButtonIsToolButton in DOCK_MANAGER_DEFAULT_CONFIG:
            _btn = QtWidgets.QToolButton()
            _btn.setAutoRaise(True)
            return _btn
        else:
            return QtWidgets.QPushButton()

    def updateCloseButtonVisibility(self, active):
        _dock_widget_closable = EnumDockWidgetFeature.CLOSEABLE in self.dockWidget.features()
        _active_tab_has_close_button = EnumDockMgrConfigFlag.ActiveTabHasCloseButton in DOCK_MANAGER_DEFAULT_CONFIG
        _all_tab_have_close_button = EnumDockMgrConfigFlag.AllTabsHaveCloseButton in DOCK_MANAGER_DEFAULT_CONFIG
        _tab_has_close_btn = (_active_tab_has_close_button and active) | _all_tab_have_close_button
        self.closeButton.setVisible(_dock_widget_closable and _tab_has_close_btn)

    def updateCloseButtonSizePolicy(self):
        _features = self.dockWidget.features()
        _size_policy = self.closeButton.sizePolicy()
        _cond1 = EnumDockWidgetFeature.CLOSEABLE in _features
        _cond2 = EnumDockMgrConfigFlag.RetainTabSizeWhenCloseButtonHidden in DOCK_MANAGER_DEFAULT_CONFIG
        _size_policy.setRetainSizeWhenHidden(_cond1 and _cond2)
        self.closeButton.setSizePolicy(_size_policy)

    def updateIcon(self):
        if not self.iconLabel or self.icon is None:
            return
        if self.iconSize.isValid():
            self.iconLabel.setPixmap(self.icon.pixmap(self.iconSize))
        else:
            self.iconLabel.setPixmap(self.icon.pixmap(
                self._this.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize, None, self._this)))
        self.iconLabel.setVisible(True)

    def createFloatingWidget(self, widget: QtWidgets.QWidget, opaque_undocking):
        from . import CFloatingDockContainer, CFloatingDragPreview,CDockWidget,CDockAreaWidget
        if opaque_undocking:
            if isinstance(widget, CDockWidget):
                return CFloatingDockContainer(dock_widget=widget)
            elif isinstance(widget, CDockAreaWidget):
                return CFloatingDockContainer(dock_area=widget)
        else:
            _w = CFloatingDragPreview(widget)
            _w.sigDraggingCanceled.connect(self._onCreateFloatingWidgetPreview)
            return _w

    def saveDragStartMousePosition(self, pos: QtCore.QPoint):
        self.globalDragStartMousePosition = pos
        self.dragStartMousePosition = self._this.mapFromGlobal(pos)

    def _onCreateFloatingWidgetPreview(self, evt):
        self.dragState = EnumDragState.INACTIVE

    def createLayout(self):
        '''
        Creates the complete layout including all controls
        '''
        self.titleLabel = CElidingLabel(text=self.dockWidget.windowTitle())
        self.titleLabel.setElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.titleLabel.setObjectName("dockWidgetTabLabel")
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.sigElidedChanged.connect(self._this.sigElidedChanged)

        self.closeButton = QtWidgets.QPushButton()
        self.closeButton.setObjectName("tabCloseButton")

        setButtonIcon(self.closeButton,
                      QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton, EnumADSIcon.CLOSE)

        self.closeButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,
                                       QtWidgets.QSizePolicy.Policy.Fixed)
        self.closeButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.updateCloseButtonSizePolicy()
        self.closeButton.setToolTip("Close Tab")
        self.closeButton.clicked.connect(self._this.sigCloseRequested)

        _fm = QtGui.QFontMetrics(self.titleLabel.font())
        _spacing = round(_fm.height() / 4.0)

        # Fill the layout
        _layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.LeftToRight)
        _layout.setContentsMargins(2 * _spacing, 0, 0, 0)
        _layout.setSpacing(0)
        self._this.setLayout(_layout)
        _layout.addWidget(self.titleLabel, 1)
        _layout.addSpacing(_spacing)
        _layout.addWidget(self.closeButton)
        _layout.addSpacing(round(_spacing * 4.0 / 3.0))
        _layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setVisible(True)

    def moveTab(self, ev: QtGui.QMouseEvent):
        '''
        Moves the tab depending on the position in the given mouse event

        Parameters
        ----------
        ev : QMouseEvent
        '''
        ev.accept()
        # left, top, right, bottom = self.public.getContentsMargins()
        _distance = globalPositionOf(ev) - self.globalDragStartMousePosition
        _distance.setY(0)
        _target_pos = _distance + self.tabDragStartPosition
        _target_pos.setX(max(_target_pos.x(), 0))
        _target_pos.setY(min(self._this.parentWidget().rect().right() - self._this.width() + 1, _target_pos.x()))

        self._this.move(_target_pos)
        self._this.raise_()

    def createAutoHideToAction(self, title: str, location: EnumSideBarLocation, menu: QtWidgets.QMenu):
        _action = menu.addAction(title)
        _action.setProperty('Location', location)
        _action.triggered.connect(self._this.onAutoHideToActionClicked)
        return _action

    def focusController(self):
        return self.dockWidget.dockManager().dockFocusController()

    def isDraggingState(self, drag_state: EnumDragState) -> bool:
        '''
        Test function for current drag state

        Parameters
        ----------
        drag_state : EnumDragState

        Returns
        -------
        value : bool
        '''
        return self.dragState == drag_state

    def startFloating(
            self,
            dragging_state: EnumDragState = EnumDragState.FLOATING_WIDGET
    ) -> bool:
        '''
        Starts floating of the dock widget that belongs to this title bar
        Returns true, if floating has been started and false if floating is not
        possible for any reason

        Parameters
        ----------
        dragging_state : EnumDragState

        Returns
        -------
        value : bool
        '''
        _dock_container = self.dockWidget.dockContainer()
        if _dock_container is None:
            return False

        logger.debug('is_floating %s',
                     _dock_container.isFloating())
        logger.debug('area_count %s',
                     _dock_container.dockAreaCount())
        logger.debug('widget_count %s',
                     self.dockWidget.dockAreaWidget().dockWidgetsCount())

        # if this is the last dock widget inside of this floating widget,
        # then it does not make any sense, to make it floating because
        # it is already floating
        if (_dock_container.isFloating()
                and (_dock_container.visibleDockAreaCount() == 1)
                and (self.dockWidget.dockAreaWidget().dockWidgetsCount() == 1)):
            return False

        logger.debug('startFloating')
        self.dragState = dragging_state
        _floating_w = None
        _opaque_undocking = EnumDockMgrConfigFlag.OpaqueUndocking in DOCK_MANAGER_DEFAULT_CONFIG or dragging_state != EnumDragState.FLOATING_WIDGET

        _size = self.dockArea.size()

        if self.dockArea.dockWidgetsCount() > 1:
            # If section widget has multiple tabs, we take only one tab
            _floating_w = self.createFloatingWidget(self.dockWidget, _opaque_undocking)
            _size = self.dockWidget.size()
        else:
            # If section widget has only one content widget, we can move the complete
            # dock area into floating widget
            _floating_w = self.createFloatingWidget(self.dockArea, _opaque_undocking)
            _size = self.dockArea.size()

        if dragging_state == EnumDragState.FLOATING_WIDGET:
            _floating_w.startFloating(self.dragStartMousePosition,
                                      _size, EnumDragState.FLOATING_WIDGET, self._this)

            _overlay = self.dockWidget.dockManager().containerOverlay()
            _overlay.setAllowedAreas(EnumDockWidgetArea.OUTER_DOCK_AREAS)
            self.floatingWidget = _floating_w
            getQApp().postEvent(self.dockWidget, QtCore.QEvent(QtCore.QEvent.Type(evtDockedWidgetDragStartEvent)))
        else:
            _floating_w.startFloating(self.dragStartMousePosition, _size, EnumDragState.INACTIVE, None)
        return True


class CDockWidgetTab(QtWidgets.QFrame):
    sigActiveTabChanged = QtCore.Signal()
    sigClicked = QtCore.Signal()
    sigCloseRequested = QtCore.Signal()
    sigCloseOtherTabsRequested = QtCore.Signal()
    sigMoved = QtCore.Signal(QtCore.QPoint)
    sigElidedChanged = QtCore.Signal(bool)

    def __init__(self, dock_widget: 'CDockWidget', parent: QtWidgets.QWidget = None):
        '''
        Parameters
        ----------
        dock_widget : DockWidget
            The dock widget this title bar
        parent : QWidget
            The parent widget of this title bar
        '''
        super().__init__(parent)
        self._mgr = DockWidgetTabMgr(self)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoMousePropagation, True)
        self._mgr.dockWidget = dock_widget
        self._mgr.createLayout()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        '''
        Mousepressevent

        Parameters
        ----------
        ev : QMouseEvent
        '''
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            ev.accept()
            self._mgr.saveDragStartMousePosition(globalPositionOf(ev))
            self._mgr.dragState = EnumDragState.MOUSE_PRESSED
            if EnumDockMgrConfigFlag.FocusHighlighting in DOCK_MANAGER_DEFAULT_CONFIG:
                self._mgr.focusController().setDockWidgetTabFocused(self)
            self.sigClicked.emit()
            return

        super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent):
        '''
        Mouse release event

        Parameters
        ----------
        ev : QMouseEvent
        '''
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            _current_drag_state = self._mgr.dragState
            self._mgr.globalDragStartMousePosition = QtCore.QPoint()
            self._mgr.dragStartMousePosition = QtCore.QPoint()
            self._mgr.dragState = EnumDragState.INACTIVE
            if _current_drag_state == EnumDragState.TAB:
                if self._mgr.dockArea:
                    ev.accept()
                    self.sigMoved.emit(globalPositionOf(ev))
            elif _current_drag_state == EnumDragState.FLOATING_WIDGET:
                ev.accept()
                self._mgr.floatingWidget.finishDragging()
        elif ev.button() == QtCore.Qt.MouseButton.MiddleButton:
            if EnumDockMgrConfigFlag.MiddleMouseButtonClosesTab in DOCK_MANAGER_DEFAULT_CONFIG and EnumDockWidgetFeature.CLOSEABLE in self._mgr.dockWidget.features():
                # Only attempt to close if the mouse is still
                # on top of the widget, to allow the user to cancel.
                if self.rect().contains(self.mapFromGlobal(QtGui.QCursor.pos())):
                    ev.accept()
                    self.sigCloseRequested.emit()
        super().mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent):
        '''
        Mousemoveevent

        Parameters
        ----------
        ev : QMouseEvent
        '''
        if (not (ev.buttons() & QtCore.Qt.MouseButton.LeftButton)
                or self._mgr.isDraggingState(EnumDragState.INACTIVE)):
            self._mgr.dragState = EnumDragState.INACTIVE
            super().mouseMoveEvent(ev)
            return

        # move floating window
        if self._mgr.isDraggingState(EnumDragState.FLOATING_WIDGET):
            self._mgr.floatingWidget.moveFloating()
            super().mouseMoveEvent(ev)
            return

        # move tab
        if self._mgr.isDraggingState(EnumDragState.TAB):
            # Moving the tab is always allowed because it does not mean moving
            # the dock widget around
            self._mgr.moveTab(ev)
        _mapped_pos = self.mapToParent(ev.pos())
        _mouse_outside_bar = (_mapped_pos.x() < 0 or _mapped_pos.x() > self.parentWidget().rect().right())
        _drag_distance_y = QtCore.qAbs(self._mgr.globalDragStartMousePosition.y() - globalPositionOf(ev).y())
        if _drag_distance_y >= QtWidgets.QApplication.startDragDistance() * 1.5 or _mouse_outside_bar:
            # If this is the last dock area in a dock container with only
            # one single dock widget it does not make  sense to move it to a new
            # floating widget and leave this one empty
            if (self._mgr.dockArea.dockContainer().isFloating()
                    and self._mgr.dockArea.openDockWidgetsCount() == 1
                    and self._mgr.dockArea.dockContainer().visibleDockAreaCount() == 1):
                return
            # Floating is only allowed for widgets that are floatable
            # If we do non opaque undocking, then can create the drag preview
            # if the widget is movable.
            _features = self._mgr.dockWidget.features()
            _is_opaque_undocking = EnumDockMgrConfigFlag.OpaqueUndocking in DOCK_MANAGER_DEFAULT_CONFIG
            if (EnumDockWidgetFeature.FLOATABLE in _features
                    or (EnumDockWidgetFeature.MOVABLE in _features and not _is_opaque_undocking)):
                # If we undock, we need to restore the initial position of this
                # tab because it looks strange if it remains on its dragged position
                if self._mgr.isDraggingState(EnumDragState.TAB) and not _is_opaque_undocking:
                    self.parentWidget().layout().update()
                self._mgr.startFloating()
            return
        elif self._mgr.dockArea.openDockWidgetsCount() > 1 and (
                globalPositionOf(ev) - self._mgr.globalDragStartMousePosition).manhattanLength() >= QtWidgets.QApplication.startDragDistance():
            # If we start dragging the tab, we save its inital position to restore it later
            if self._mgr.dragState != EnumDragState.TAB:
                self._mgr.tabDragStartPosition = self.pos()
            self._mgr.dragState = EnumDragState.TAB
            return

        super().mouseMoveEvent(ev)

    def contextMenuEvent(self, ev: QtGui.QContextMenuEvent):
        '''
        Context menu event

        Parameters
        ----------
        ev : QContextMenuEvent
        '''
        ev.accept()
        if self._mgr.isDraggingState(EnumDragState.FLOATING_WIDGET):
            return
        self._mgr.saveDragStartMousePosition(ev.globalPos())
        _is_floatable = EnumDockWidgetFeature.FLOATABLE in self._mgr.dockWidget.features()
        _is_not_only_tab_in_container = not self._mgr.dockArea.dockContainer().hasTopLevelDockWidget()
        _is_top_level_area = self._mgr.dockArea.isTopLevelArea()
        _is_detachable = _is_floatable and _is_not_only_tab_in_container

        _menu = QtWidgets.QMenu()
        if not _is_top_level_area:
            _action = QtGui.QAction('detach', self)
            _action.setEnabled(_is_detachable)
            _action.triggered.connect(self.onDetachDockWidget)
            _menu.addAction(_action)
            if EnumAutoHideFlag.AutoHideFeatureEnabled in AUTO_HIDE_DEFAULT_CONFIG:
                _is_pinnable = EnumDockWidgetFeature.PINNABLE in self._mgr.dockWidget.features()
                _action = QtGui.QAction('Pin to', self)
                _action.setEnabled(_is_pinnable)
                # fixme: what slot bind to?
                # _action.triggered.connect(self.onDetachDockWidget)
                _s_menu = _menu.addMenu('Pin to')
                self._mgr.createAutoHideToAction('top', EnumSideBarLocation.TOP, _s_menu)
                self._mgr.createAutoHideToAction('Left', EnumSideBarLocation.LEFT, _s_menu)
                self._mgr.createAutoHideToAction('Right', EnumSideBarLocation.RIGHT, _s_menu)
                self._mgr.createAutoHideToAction('Bottom', EnumSideBarLocation.BOTTOM, _s_menu)
        _menu.addSeparator()
        _action = QtGui.QAction('close', self)
        _action.setEnabled(self.isClosable())
        _action.triggered.connect(self.sigCloseRequested)
        _menu.addAction(_action)

        if self._mgr.dockArea.openDockWidgetsCount() > 1:
            _action = QtGui.QAction('close others', self)
            _action.triggered.connect(self.sigCloseOtherTabsRequested)
            _menu.addAction(_action)

        _menu.exec(ev.globalPos())

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        '''
        Double clicking the tab widget makes the assigned dock widget floating

        Parameters
        ----------
        event : QMouseEvent
        '''
        # If this is the last dock area in a dock container it does not make
        # sense to move it to a new floating widget and leave this one
        # empty
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            _floatable = self._mgr.dockArea.dockContainer().isFloating()
            _has_widgets = self._mgr.dockArea.openDockWidgetsCount() > 1
            _allow_floatable = EnumDockWidgetFeature.FLOATABLE in self._mgr.dockWidget.features()
            if (not _floatable or _has_widgets) and _allow_floatable:
                event.accept()
                self._mgr.saveDragStartMousePosition(globalPositionOf(event))
                self._mgr.startFloating(EnumDragState.INACTIVE)
        super().mouseDoubleClickEvent(event)

    def isActiveTab(self) -> bool:
        '''
        Returns true, if this is the active tab

        Returns
        -------
        value : bool
        '''
        return self._mgr.isActiveTab

    def setVisible(self, visible):
        visible &= EnumDockWidgetFeature.NO_TAB not in self._mgr.dockWidget.features()
        super().setVisible(visible)

    def setActiveTab(self, active: bool):
        '''
        Set this true to make this tab the active tab

        Parameters
        ----------
        active : bool
        '''
        self._mgr.updateCloseButtonVisibility(active)
        if EnumDockMgrConfigFlag.FocusHighlighting in DOCK_MANAGER_DEFAULT_CONFIG and not self._mgr.dockWidget.dockManager().isRestoringState():
            _update_focus_style = False
            if active and not self.hasFocus():
                self._mgr.focusController().setDockWidgetTabFocused(self)
                _update_focus_style = True
            if self._mgr.isActiveTab == active:
                if _update_focus_style:
                    self.updateStyle()
                return
        elif self._mgr.isActiveTab == active:
            return
        self._mgr.isActiveTab = active
        self.updateStyle()
        self.update()
        self.updateGeometry()
        self.sigActiveTabChanged.emit()

    def dockWidget(self) -> 'CDockWidget':
        '''
        Returns the dock widget this title widget belongs to

        Returns
        -------
        value : DockWidget
        '''
        return self._mgr.dockWidget

    def setDockAreaWidget(self, dock_area: 'CDockAreaWidget'):
        '''
        Sets the dock area widget the dockWidget returned by dockWidget() function belongs to.

        Parameters
        ----------
        dock_area : CDockAreaWidget
        '''
        self._mgr.dockArea = dock_area

    def dockAreaWidget(self) -> 'CDockAreaWidget':
        '''
        Returns the dock area widget this title bar belongs to.

        Returns
        -------
        value : DockAreaWidget
        '''
        return self._mgr.dockArea

    def setIcon(self, icon: QtGui.QIcon):
        '''
        Sets the icon to show in title bar

        Parameters
        ----------
        icon : QIcon
        '''
        _layout = self.layout()
        if not self._mgr.iconLabel and icon.isNull():
            return

        if not self._mgr.iconLabel:
            self._mgr.iconLabel = QtWidgets.QLabel()
            self._mgr.iconLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
            self._mgr.iconLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
            self._mgr.iconLabel.setToolTip(self._mgr.titleLabel.toolTip())
            _layout.insertWidget(0, self._mgr.iconLabel, QtCore.Qt.AlignmentFlag.AlignVCenter)
            _layout.insertSpacing(1, round(1.5 * _layout.contentsMargins().left() / 2.0))

        elif icon.isNull():
            # Remove icon label and spacer item
            _layout.removeWidget(self._mgr.iconLabel)
            _layout.removeItem(_layout.itemAt(0))
            self._mgr.iconLabel.deleteLater()
            self._mgr.iconLabel = None

        self._mgr.icon = icon
        self._mgr.updateIcon()

    def icon(self) -> QtGui.QIcon:
        '''
        Returns the icon

        Returns
        -------
        value : QIcon
        '''
        return self._mgr.icon

    def text(self) -> str:
        '''
        Returns the tab text

        Returns
        -------
        value : str
        '''
        return self._mgr.titleLabel.text()

    def setText(self, title: str):
        '''
        Sets the tab text

        Parameters
        ----------
        title : str
        '''
        self._mgr.titleLabel.setText(title)

    def setElideMode(self, mode: QtCore.Qt.TextElideMode):
        self._mgr.titleLabel.setElideMode(mode)

    def isTitleElided(self):
        return self._mgr.titleLabel.isElided()

    def isClosable(self) -> bool:
        '''
        This function returns true if the assigned dock widget is closeable

        Returns
        -------
        value : bool
        '''
        return (self._mgr.dockWidget and
                EnumDockWidgetFeature.CLOSEABLE in self._mgr.dockWidget.features())

    def onDetachDockWidget(self):
        if EnumDockWidgetFeature.FLOATABLE not in self._mgr.dockWidget.features():
            return
        self._mgr.saveDragStartMousePosition(QtGui.QCursor.pos())
        self._mgr.startFloating(EnumDragState.INACTIVE)

    def onDockWidgetFeaturesChanged(self):
        self._mgr.updateCloseButtonSizePolicy()
        self._mgr.updateCloseButtonVisibility(self.isActiveTab())

    def onAutoHideToActionClicked(self):
        _loc = self.sender().property('Location')
        self.dockWidget().toggleAutoHide(_loc)

    def autoHideDockWidget(self):
        return self._mgr.dockWidget.setAutoHide(True)

    def event(self, e: QtCore.QEvent) -> bool:
        '''
        Track event ToolTipChange and set child ToolTip

        Parameters
        ----------
        e : QEvent

        Returns
        -------
        value : bool
        '''
        if e.type() == QtCore.QEvent.Type.ToolTipChange:
            _text = self.toolTip()
            self._mgr.titleLabel.setToolTip(_text)
            if self._mgr.iconLabel:
                self._mgr.iconLabel.setToolTip(_text)
        if e.type() == QtCore.QEvent.Type.StyleChange:
            self._mgr.updateIcon()
        return super().event(e)

    def updateStyle(self):
        repolishStyle(self, EnumRepolishChildOptions.RepolishDirectChildren)

    def iconSize(self):
        return self._mgr.iconSize

    def setIconSize(self, size: QtCore.QSize):
        self._mgr.iconSize = size
        self._mgr.updateIcon()

    activeTab = QtCore.Property(bool, isActiveTab,setActiveTab)
    # fixme: iconSize set could use pIconSize=xxx:QtCore.QSize
    pIconSize= QtCore.Property(QtCore.QSize,iconSize,setIconSize)