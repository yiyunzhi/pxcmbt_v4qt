import typing
from typing import TYPE_CHECKING, Optional
import logging
from PySide6 import QtCore, QtGui, QtWidgets

from .define import (EnumDockFlags, EnumDragState, EnumBitwiseOP,
                     EnumDockWidgetFeature, EnumTitleBarButton,
                     EnumSideBarLocation, EnumDockMgrConfigFlag,
                     DOCK_MANAGER_DEFAULT_CONFIG, EnumAutoHideFlag,
                     AUTO_HIDE_DEFAULT_CONFIG, EnumDockWidgetArea, EnumADSIcon)
from .util import setButtonIcon, getQApp, evtDockedWidgetDragStartEvent
from .floating_drag_preview import CFloatingDragPreview
from .dock_area_tab_bar import CDockAreaTabBar
from .eliding_label import CElidingLabel

if TYPE_CHECKING:
    from .dock_area_widget import CDockAreaWidget
    from .dock_manager import CDockManager
    from .floating_dock_container import IFloatingWidget

logger = logging.getLogger(__name__)


class CTitleBarButton(QtWidgets.QToolButton):
    def __init__(self, visible=True, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._visible = visible
        self._hideWhenDisabled = EnumDockMgrConfigFlag.DockAreaHideDisabledButtons in DOCK_MANAGER_DEFAULT_CONFIG

    def setVisible(self, visible: bool) -> None:
        visible = visible and self._visible
        if visible and self._hideWhenDisabled:
            visible = self.isEnabled()
        super().setVisible(visible)

    def event(self, e: QtCore.QEvent) -> bool:
        if QtCore.QEvent.Type.EnabledChange == e.type() and self._hideWhenDisabled:
            QtCore.QMetaObject.invokeMethod(self, 'setVisible', QtCore.Qt.ConnectionType.QueuedConnection, self.isEnabled())
        return super().event(e)


class CSpacerWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setStyleSheet('border:none;background:none;')


class DockAreaTitleBarMgr:
    _this: 'CDockAreaTitleBar'
    tabsMenuButton: QtWidgets.QToolButton
    undockButton: QtWidgets.QToolButton
    closeButton: QtWidgets.QToolButton
    autoHideButton: QtWidgets.QToolButton
    layout: QtWidgets.QBoxLayout
    dockArea: 'CDockAreaWidget'
    tabBar: 'CDockAreaTabBar'
    autoHideTitleLabel: 'CElidingLabel'
    menuOutdated: bool
    tabsMenu: QtWidgets.QMenu
    dockWidgetActionsButtons: typing.List[QtWidgets.QToolButton]
    dragStartMousePos: QtCore.QPoint
    dragState: EnumDragState
    floatingWidget: 'IFloatingWidget'

    def __init__(self, _this: 'CDockAreaTitleBar'):
        self._this = _this
        self.tabsMenuButton = None
        self.undockButton = None
        self.closeButton = None
        self.layout = None
        self.dockArea = None
        self.autoHideTitleLabel = None
        self.tabBar = None
        self.menuOutdated = True
        self.tabsMenu = None
        self.dockWidgetActionsButtons = None
        self.dragStartMousePos = None
        self.dragState = EnumDragState.INACTIVE
        self.floatingWidget = None

    def dockManager(self):
        return self.dockArea.dockManager()

    def isDraggingState(self, drag_state: EnumDragState):
        return self.dragState == drag_state

    def createAutoHideTitleLabel(self):
        self.autoHideTitleLabel = CElidingLabel('')
        self.autoHideTitleLabel.setObjectName('autoHideTitleLabel')
        self.layout.addWidget(self.autoHideTitleLabel)

    def createAutoHideToAction(self, title: str, location: EnumSideBarLocation, menu: QtWidgets.QMenu):
        _action = menu.addAction(title)
        _action.setProperty('Location', location)
        _action.triggered.connect(self._this.onAutoHideToActionClicked)
        return _action

    def createButtons(self):
        '''
        Creates the title bar close and menu buttons
        '''
        _btn_sp = (QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        # tabs menu button

        self.tabsMenuButton = CTitleBarButton(EnumDockMgrConfigFlag.DockAreaHasTabsMenuButton in DOCK_MANAGER_DEFAULT_CONFIG)
        self.tabsMenuButton.setObjectName("tabsMenuButton")
        self.tabsMenuButton.setAutoRaise(True)
        self.tabsMenuButton.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)

        _style = self._this.style()
        setButtonIcon(self.tabsMenuButton, QtWidgets.QStyle.StandardPixmap.SP_TitleBarUnshadeButton, EnumADSIcon.AREA_MENU)

        self.tabsMenu = QtWidgets.QMenu(self.tabsMenuButton)
        self.tabsMenu.setToolTipsVisible(True)
        self.tabsMenu.aboutToShow.connect(self._this.onTabsMenuAboutToShow)
        self.tabsMenuButton.setMenu(self.tabsMenu)
        self.tabsMenuButton.setToolTip("List all tabs")

        self.tabsMenuButton.setSizePolicy(*_btn_sp)
        self.layout.addWidget(self.tabsMenuButton, 0)
        self.tabsMenuButton.menu().triggered.connect(self._this.onTabsMenuActionTriggered)

        # Undock button
        self.undockButton = CTitleBarButton(EnumDockMgrConfigFlag.DockAreaHasUndockButton in DOCK_MANAGER_DEFAULT_CONFIG)
        self.undockButton.setObjectName("undockButton")
        self.undockButton.setAutoRaise(True)
        self.undockButton.setToolTip("Detach Group")

        setButtonIcon(self.undockButton,
                      QtWidgets.QStyle.StandardPixmap.SP_TitleBarNormalButton, EnumADSIcon.AREA_UNDOCK)

        self.undockButton.setSizePolicy(*_btn_sp)
        self.layout.addWidget(self.undockButton, 0)
        self.undockButton.clicked.connect(self._this.onUndockButtonClicked)
        # autohide button

        _auto_hide_enable = EnumAutoHideFlag.AutoHideFeatureEnabled in AUTO_HIDE_DEFAULT_CONFIG
        _has_auto_hide = EnumAutoHideFlag.DockAreaHasAutoHideButton in AUTO_HIDE_DEFAULT_CONFIG
        self.autoHideButton = CTitleBarButton(_auto_hide_enable and _has_auto_hide)
        self.autoHideButton.setObjectName('dockAreaAutoHideButton')
        self.autoHideButton.setAutoRaise(True)
        self.autoHideButton.setToolTip(self._this.titleBarButtonToolTip(EnumTitleBarButton.AUTO_HIDE))
        setButtonIcon(self.autoHideButton,
                      QtWidgets.QStyle.StandardPixmap.SP_DialogOkButton, EnumADSIcon.AUTO_HIDE)
        self.autoHideButton.setSizePolicy(*_btn_sp)

        self.autoHideButton.setCheckable(EnumAutoHideFlag.AutoHideButtonCheckable in AUTO_HIDE_DEFAULT_CONFIG)
        self.autoHideButton.setChecked(False)
        self.layout.addWidget(self.autoHideButton, 0)
        self.autoHideButton.clicked.connect(self._this.onAutoHideButtonClicked)
        # Close button

        self.closeButton = CTitleBarButton(EnumDockMgrConfigFlag.DockAreaHasCloseButton in DOCK_MANAGER_DEFAULT_CONFIG)
        self.closeButton.setObjectName("dockAreaCloseButton")
        self.closeButton.setAutoRaise(True)
        setButtonIcon(self.closeButton, QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton, EnumADSIcon.AREA_CLOSE)

        self.closeButton.setToolTip(self._this.titleBarButtonToolTip(EnumTitleBarButton.CLOSE))

        self.closeButton.setSizePolicy(*_btn_sp)
        self.closeButton.setIconSize(QtCore.QSize(16, 16))
        self.layout.addWidget(self.closeButton, 0)
        self.closeButton.clicked.connect(self._this.onCloseButtonClicked)

    def createTabBar(self):
        '''
        Creates the internal TabBar
        '''

        self.tabBar = CDockAreaTabBar(self.dockArea)
        self.tabBar.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum,
                                  QtWidgets.QSizePolicy.Policy.Preferred)
        self.layout.addWidget(self.tabBar)

        self.tabBar.sigTabClosed.connect(self._this.markTabsMenuOutdated)
        self.tabBar.sigTabOpened.connect(self._this.markTabsMenuOutdated)
        self.tabBar.sigTabInserted.connect(self._this.markTabsMenuOutdated)
        self.tabBar.sigRemovingTab.connect(self._this.markTabsMenuOutdated)
        self.tabBar.sigTabMoved.connect(self._this.markTabsMenuOutdated)
        self.tabBar.sigCurrentChanged.connect(self._this.onCurrentTabChanged)
        self.tabBar.sigTabBarClicked.connect(self._this.sigTabBarClicked)
        self.tabBar.sigElidedChanged.connect(self._this.markTabsMenuOutdated)

    def makeAreaFloating(self, offset: QtCore.QPoint, drage_state: EnumDragState):
        _size = self.dockArea.size()
        self.dragState = drage_state

        _opaque_undocking = EnumDockMgrConfigFlag.OpaqueUndocking in DOCK_MANAGER_DEFAULT_CONFIG or self.dragState != EnumDragState.FLOATING_WIDGET
        _float_dock_container = None
        _float_widget = None
        if _opaque_undocking:
            from .floating_dock_container import CFloatingDockContainer
            _float_widget = _float_dock_container = CFloatingDockContainer(dock_area=self.dockArea)
        else:
            _w = CFloatingDragPreview(self.dockArea)
            _w.sigDraggingCanceled.connect(self._onAreaFloatingDraggingCanceled)
            _float_widget = _w
        _float_widget.startFloating(offset, _size, self.dragState, None)
        if _float_dock_container:
            _top_level_dock_widget = _float_dock_container.topLevelDockWidget()
            if _top_level_dock_widget is not None:
                _top_level_dock_widget.emitTopLevelChanged(True)
        return _float_widget

    def startFloating(self, offset: QtCore.QPoint):
        if self.dockArea.autoHideDockContainer() is not None:
            self.dockArea.autoHideDockContainer().hide()
        self.floatingWidget = self.makeAreaFloating(offset, EnumDragState.FLOATING_WIDGET)
        getQApp().postEvent(self.dockArea, QtCore.QEvent(QtCore.QEvent.Type(evtDockedWidgetDragStartEvent)))

    def _onAreaFloatingDraggingCanceled(self):
        self.dragState = EnumDragState.INACTIVE

    def testConfigFlag(self, flag: EnumDockFlags) -> bool:
        '''
        Returns true if the given config flag is set

        Parameters
        ----------
        flag : DockFlags

        Returns
        -------
        value : bool
        '''
        return flag in self.dockArea.dockManager().configFlags()


class CDockAreaTitleBar(QtWidgets.QFrame):
    # This signal is emitted if a tab in the tab bar is clicked by the user or
    # if the user clicks on a tab item in the title bar tab menu.
    sigTabBarClicked = QtCore.Signal(int)
    LocationProperty = "Location"

    def __init__(self, parent: 'CDockAreaWidget'):
        '''
        Default Constructor

        Parameters
        ----------
        parent : DockAreaWidget
        '''
        super().__init__(parent)
        self._mgr = DockAreaTitleBarMgr(self)
        self._mgr.dockArea = parent
        self.setObjectName("dockAreaTitleBar")

        self._mgr.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.LeftToRight)
        self._mgr.layout.setContentsMargins(0, 0, 0, 0)
        self._mgr.layout.setSpacing(0)
        self.setLayout(self._mgr.layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self._mgr.createTabBar()
        self._mgr.createAutoHideTitleLabel()
        self._mgr.autoHideTitleLabel.setVisible(False)
        self._mgr.layout.addWidget(CSpacerWidget(self))
        self._mgr.createButtons()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    # def destroy(self, destroyWindow: bool = ..., destroySubWindows: bool = ...) -> None:
    #     if self._mgr.closeButton is not None:
    #         self._mgr.closeButton = None
    #     if self._mgr.tabsMenuButton is not None:
    #         self._mgr.tabsMenuButton = None
    #     if self._mgr.undockButton is not None:
    #         self._mgr.undockButton = None
    #     self._mgr = None
    #     super().destroy(destroyWindow, destroySubWindows)

    def onTabsMenuAboutToShow(self):
        if not self._mgr.menuOutdated:
            return

        _menu = self._mgr.tabsMenuButton.menu()
        if _menu is not None:
            _menu.clear()

        for i in range(self._mgr.tabBar.count()):
            if not self._mgr.tabBar.isTabOpen(i):
                continue

            _tab = self._mgr.tabBar.tab(i)
            if _tab.icon() is not None:
                _icon = _tab.icon()
            else:
                _spm = QtWidgets.QStyle.StandardPixmap.SP_TitleBarNormalButton
                _icon = self.style().standardIcon(_spm)
            _action = QtGui.QAction(_icon, _tab.text(), self)
            _action.setToolTip(_tab.toolTip())
            _action.setData(i)
            _menu.addAction(_action)
        self._mgr.menuOutdated = False

    def onCloseButtonClicked(self):
        logger.debug('DockAreaTitleBar.onCloseButtonClicked')
        if EnumDockMgrConfigFlag.DockAreaCloseButtonClosesTab in DOCK_MANAGER_DEFAULT_CONFIG:
            self._mgr.tabBar.closeTab(self._mgr.tabBar.currentIndex())
        else:
            self._mgr.dockArea.closeArea()

    def onAutoHideButtonClicked(self):
        _c1 = EnumAutoHideFlag.AutoHideButtonTogglesArea in AUTO_HIDE_DEFAULT_CONFIG
        _c2 = getQApp().keyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier==QtCore.Qt.KeyboardModifier.ControlModifier
        if _c1 or _c2:
            self._mgr.dockArea.toggleAutoHide()
        else:
            self._mgr.dockArea.currentDockWidget().toggleAutoHide()

    def onUndockButtonClicked(self):
        if EnumDockWidgetFeature.FLOATABLE in self._mgr.dockArea.features():
            if self._mgr.dockArea.autoHideDockContainer():
                self._mgr.dockArea.autoHideDockContainer().cleanupAndDelete()
            self._mgr.makeAreaFloating(self.mapFromGlobal(QtGui.QCursor.pos()), EnumDragState.INACTIVE)

    def onAutoHideDockAreaActionClicked(self):
        self._mgr.dockArea.toggleAutoHide()

    def onAutoHideToActionClicked(self):
        _loc = self.sender().property(self.LocationProperty)
        self._mgr.dockArea.toggleAutoHide(_loc)

    def onTabsMenuActionTriggered(self, action: QtGui.QAction):
        '''
        On tabs menu action triggered

        Parameters
        ----------
        action : QAction
        '''
        _index = action.data()
        self._mgr.tabBar.setCurrentIndex(_index)
        self.sigTabBarClicked.emit(_index)

    def updateDockWidgetActionsButtons(self):
        _tab = self._mgr.tabBar.currentTab()
        if _tab is None:
            return
        _dock_widget = _tab.dockWidget()
        if self._mgr.dockWidgetActionsButtons:
            for x in self._mgr.dockWidgetActionsButtons:
                self._mgr.layout.removeWidget(x)
            self._mgr.dockWidgetActionsButtons.clear()
        _actions = _dock_widget.titleBarActions()
        if not _actions:
            return
        _insert_idx = self.indexOf(self._mgr.tabsMenuButton)
        for x in _actions:
            _btn = CTitleBarButton(True, self)
            _btn.setDefaultAction(x)
            _btn.setAutoRaise(True)
            _btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
            _btn.setObjectName(x.objectName())
            _insert_idx += 1
            self._mgr.layout.insertWidget(_insert_idx, _btn, 0)
            self._mgr.dockWidgetActionsButtons.append(_btn)

    def onCurrentTabChanged(self, index: int):
        '''
        On current tab changed

        Parameters
        ----------
        index : int
        '''
        if index < 0:
            return

        if EnumDockMgrConfigFlag.DockAreaCloseButtonClosesTab in DOCK_MANAGER_DEFAULT_CONFIG:
            _dock_widget = self._mgr.tabBar.tab(index).dockWidget()
            _enabled = EnumDockWidgetFeature.CLOSEABLE in _dock_widget.features()
            self._mgr.closeButton.setEnabled(_enabled)
        self.updateDockWidgetActionsButtons()

    def markTabsMenuOutdated(self):
        if EnumDockMgrConfigFlag.DockAreaDynamicTabsMenuButtonVisibility in DOCK_MANAGER_DEFAULT_CONFIG:
            _has_elided_tab_title = False
            for i in range(self._mgr.tabBar.count()):
                if not self._mgr.tabBar.isTabOpen(i):
                    continue
                _tab = self._mgr.tabBar.tab(i)
                if _tab.isTitleElided():
                    _has_elided_tab_title = True
            _visible = (_has_elided_tab_title and self._mgr.tabBar.count() > 1)
            QtCore.QMetaObject.invokeMethod(self._mgr.tabsMenuButton, 'setVisible', QtCore.Qt.ConnectionType.QueuedConnection, _visible)
            self._mgr.menuOutdated = True

    def tabBar(self) -> 'CDockAreaTabBar':
        '''
        Returns the pointer to the tabBar

        Returns
        -------
        value : DockAreaTabBar
        '''
        return self._mgr.tabBar

    def button(self, which: CTitleBarButton) -> Optional[QtWidgets.QAbstractButton]:
        '''
        Returns the button corresponding to the given title bar button identifier

        Parameters
        ----------
        which : CTitleBarButton

        Returns
        -------
        value : QAbstractButton
        '''
        if which == EnumTitleBarButton.TABS_MENU:
            return self._mgr.tabsMenuButton
        if which == EnumTitleBarButton.UNDOCK:
            return self._mgr.undockButton
        if which == EnumTitleBarButton.CLOSE:
            return self._mgr.closeButton
        if which == EnumTitleBarButton.AUTO_HIDE:
            return self._mgr.autoHideButton

        return None

    def autoHideTitleLabel(self):
        return self._mgr.autoHideTitleLabel

    def setVisible(self, visible: bool):
        '''
        This function is here for debug reasons

        Parameters
        ----------
        visible : bool
        '''
        super().setVisible(visible)
        self.markTabsMenuOutdated()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            event.accept()
            self._mgr.dragStartMousePos = event.pos()
            self._mgr.dragState = EnumDragState.MOUSE_PRESSED
            if EnumDockMgrConfigFlag.FocusHighlighting in DOCK_MANAGER_DEFAULT_CONFIG:
                self._mgr.dockManager().dockFocusController().setDockWidgetTabFocused(self._mgr.tabBar.currentTab())
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            logger.debug('CDockAreaTitleBar::mouseReleaseEvent')
            event.accept()
            _current_drag_state = self._mgr.dragState
            self._mgr.dragStartMousePos = QtCore.QPoint()
            self._mgr.dragState = EnumDragState.INACTIVE
            if EnumDragState.FLOATING_WIDGET == _current_drag_state:
                self._mgr.floatingWidget.finishDragging()
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        _is_left_btn = event.buttons() & QtGui.Qt.MouseButton.LeftButton
        _is_inactive_drag = self._mgr.isDraggingState(EnumDragState.INACTIVE)
        if not _is_left_btn or _is_inactive_drag:
            self._mgr.dragState = EnumDragState.INACTIVE
            return
            # move floating window
        if self._mgr.isDraggingState(EnumDragState.FLOATING_WIDGET):
            self._mgr.floatingWidget.moveFloating()
            return
            # If this is the last dock area in a floating dock container it does not make
        # sense to move it to a new floating widget and leave this one empty
        _is_floating = self._mgr.dockArea.dockContainer().isFloating()
        _only_one_visible = self._mgr.dockArea.dockContainer().visibleDockAreaCount() == 1
        _da_is_auto_hide = self._mgr.dockArea.isAutoHide()
        if _is_floating and _only_one_visible and _da_is_auto_hide:
            return
            # If one single dock widget in this area is not floatable then the whole
        # area is not floatable
        # If we do non opaque undocking, then we can create the floating drag
        # preview if the dock widget is movable
        _features = self._mgr.dockArea.features()
        if (EnumDockWidgetFeature.FLOATABLE not in _features
                and EnumDockWidgetFeature.MOVABLE not in _features
                and EnumDockMgrConfigFlag.OpaqueUndocking not in DOCK_MANAGER_DEFAULT_CONFIG):
            return

        _drag_distance = (self._mgr.dragStartMousePos - event.pos()).manhattanLength()
        if _drag_distance >= QtWidgets.QApplication.startDragDistance() * 1.5:
            logger.debug('CDockAreaTitleBar::startFloating')
            self._mgr.startFloating(self._mgr.dragStartMousePos)
            _overlay = self._mgr.dockArea.dockManager().containerOverlay()
            _overlay.setAllowedAreas(EnumDockWidgetArea.OUTER_DOCK_AREAS)
        return

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        """

        :param event:
        :return:
        """
        # If this is the last dock area in a dock container it does not make
        # sense to move it to a new floating widget and leave this one
        # empty
        _is_floating = self._mgr.dockArea.dockContainer().isFloating()
        _only_one = self._mgr.dockArea.dockContainer().dockAreaCount() == 1
        if _is_floating and _only_one:
            return
        if EnumDockWidgetFeature.FLOATABLE not in self._mgr.dockArea.features():
            return
        if self._mgr.dockArea.autoHideDockContainer():
            self._mgr.dockArea.autoHideDockContainer().cleanupAndDelete()
        self._mgr.makeAreaFloating(event.pos(), EnumDragState.INACTIVE)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        event.accept()
        if self._mgr.isDraggingState(EnumDragState.FLOATING_WIDGET):
            return
        _is_auto_hide = self._mgr.dockArea.isAutoHide()
        _is_top_level_area = self._mgr.dockArea.isTopLevelArea()
        _menu = QtWidgets.QMenu(self)
        if not _is_top_level_area:
            _action = QtGui.QAction('detach' if _is_auto_hide else 'detach group', self)
            _menu.addAction(_action)
            _action.triggered.connect(self.onUndockButtonClicked)
            _action.setEnabled(EnumDockWidgetFeature.FLOATABLE in self._mgr.dockArea.features())

            if EnumAutoHideFlag.AutoHideFeatureEnabled in AUTO_HIDE_DEFAULT_CONFIG:
                _action = QtGui.QAction('unpin (dock)' if _is_auto_hide else 'Pin group', self)
                _menu.addAction(_action)
                _action.triggered.connect(self.onAutoHideDockAreaActionClicked)
                _area_is_pinnable = EnumDockWidgetFeature.PINNABLE in self._mgr.dockArea.features()
                _action.setEnabled(_area_is_pinnable)

                if not _is_auto_hide:
                    _s_menu = _menu.addMenu('Pin Group To...')
                    _s_menu.setEnabled(_area_is_pinnable)
                    self._mgr.createAutoHideToAction('top', EnumSideBarLocation.TOP, _s_menu)
                    self._mgr.createAutoHideToAction('Left', EnumSideBarLocation.LEFT, _s_menu)
                    self._mgr.createAutoHideToAction('Right', EnumSideBarLocation.RIGHT, _s_menu)
                    self._mgr.createAutoHideToAction('Bottom', EnumSideBarLocation.BOTTOM, _s_menu)
            _menu.addSeparator()
        _action = QtGui.QAction('close' if _is_auto_hide else 'close group', self)
        _menu.addAction(_action)
        _action.triggered.connect(self.onCloseButtonClicked)
        _action.setEnabled(EnumDockWidgetFeature.CLOSEABLE in self._mgr.dockArea.features())

        if not _is_auto_hide and not _is_top_level_area:
            _action = QtGui.QAction('close other groups', self._mgr.dockArea)
            _menu.addAction(_action)
            _action.triggered.connect(self._mgr.dockArea.closeOtherAreas)

        _menu.exec(event.globalPos())

    def insertWidget(self, index, widget: QtWidgets.QWidget):
        self._mgr.layout.insertWidget(index, widget)

    def indexOf(self, widget: QtWidgets.QWidget):
        return self._mgr.layout.indexOf(widget)

    def titleBarButtonToolTip(self, button: EnumTitleBarButton):
        # todo: add translate
        if button == EnumTitleBarButton.AUTO_HIDE:
            if self._mgr.dockArea.isAutoHide():
                return 'Unpin (Dock)'
            if EnumAutoHideFlag.AutoHideButtonTogglesArea in AUTO_HIDE_DEFAULT_CONFIG:
                return 'Pin Group'
            else:
                return 'Pin Active Tab (Press Ctrl to Pin Group)'
        elif button == EnumTitleBarButton.CLOSE:
            if self._mgr.dockArea.isAutoHide():
                return 'Close'
            if EnumDockMgrConfigFlag.DockAreaCloseButtonClosesTab in DOCK_MANAGER_DEFAULT_CONFIG:
                return 'Close Active Tab'
            else:
                return 'Close Group'
        return ''
