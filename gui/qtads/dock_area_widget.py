import logging
from typing import TYPE_CHECKING, Optional
from PySide6 import QtCore, QtGui, QtWidgets

from .dock_components_factory import DEFAULT_COMPONENT_FACTORY

from .auto_hide_dock_container import CAutoHideDockContainer

from .dock_state_reader import CDockStateReader
from .util import (findParent, DEBUG_LEVEL, hideEmptyParentSplitters,
                   emitTopLevelEventForWidget, testFlag, LINUX, WINDOWS,setFlag)
from .define import (EnumTitleBarButton,
                     EnumDockWidgetFeature,
                     EnumDockWidgetArea,
                     EnumDockAreaFlag,
                     EnumBitwiseOP,
                     EnumBorderLocation,
                     EnumSideBarLocation,
                     EnumDockMgrConfigFlag)
from .dock_area_layout import CDockAreaLayout

if TYPE_CHECKING:
    from .dock_container_widget import CDockContainerWidget
    from .dock_splitter import CDockSplitter
    from . import (DockContainerWidget, DockWidget)

logger = logging.getLogger(__name__)


class DockAreaWidgetMgr:
    _this: 'CDockAreaWidget'
    layout: QtWidgets.QBoxLayout
    contentsLayout: CDockAreaLayout
    titleBar: 'CDockAreaTitleBar'
    dockManager: 'CDockManager'
    autoHideDockContainer: 'CAutoHideDockContainer'
    updateTitleBarButtons: bool
    allowedAreas: EnumDockWidgetArea
    minSizeHint: QtCore.QSize
    flags: EnumDockAreaFlag

    def __init__(self, _this):
        '''
        Private data constructor

        Parameters
        ----------
        _this : CDockAreaWidget
        '''
        self._this = _this
        self.layout = None
        self.contentsLayout = None
        self.titleBar = None
        self.dockManager = None
        self.updateTitleBarButtons = False
        self.autoHideDockContainer = None
        self.allowedAreas = EnumDockWidgetArea.ALL_DOCK_AREAS
        self.minSizeHint = QtCore.QSize()
        self.flags = EnumDockAreaFlag.DefaultFlags

    def createTitleBar(self):
        '''
        Creates the layout for top area with tabs and close button
        '''
        self.titleBar = DEFAULT_COMPONENT_FACTORY.createDockAreaTitleBar(self._this)
        self.layout.addWidget(self.titleBar)

        _tab_bar = self.tabBar()
        _tab_bar.sigTabCloseRequested.connect(self._this.onTabCloseRequested)
        self.titleBar.sigTabBarClicked.connect(self._this.setCurrentIndex)
        _tab_bar.sigTabMoved.connect(self._this.reorderDockWidget)

    def dockWidgetAt(self, index: int) -> 'CDockWidget':
        '''
        Returns the dock widget with the given index

        Parameters
        ----------
        index : int

        Returns
        -------
        value : DockWidget
        '''
        return self.contentsLayout.widget(index)

    def tabWidgetAt(self, index: int) -> 'CDockWidgetTab':
        '''
        Convenience function to ease title widget access by index

        Parameters
        ----------
        index : int

        Returns
        -------
        value : DockWidgetTab
        '''
        return self.dockWidgetAt(index).tabWidget()

    def dockWidgetTabAction(self, dock_widget: 'CDockWidget') -> QtGui.QAction:
        '''
        Returns the tab action of the given dock widget

        Parameters
        ----------
        dock_widget : DockWidget

        Returns
        -------
        value : QAction
        '''
        # todo: property in const defined
        return dock_widget.property('action')

    def dockWidgetIndex(self, dock_widget: 'CDockWidget') -> int:
        '''
        Returns the index of the given dock widget

        Parameters
        ----------
        dock_widget : DockWidget

        Returns
        -------
        value : int
        '''
        return dock_widget.property('index')

    def tabBar(self) -> 'CDockAreaTabBar':
        '''
        Convenience function for tabbar access

        Returns
        -------
        value : DockAreaTabBar
        '''
        return self.titleBar.tabBar()

    def updateTitleBarButtonStates(self):
        '''
        Udpates the enable state of the close/detach buttons
        '''
        if self._this.isHidden():
            self.updateTitleBarButtons = True
            return

        _close_button = self.titleBar.button(EnumTitleBarButton.CLOSE)
        _close_button.setEnabled(testFlag(self._this.features(), EnumDockWidgetFeature.CLOSEABLE))
        _undock_button = self.titleBar.button(EnumTitleBarButton.UNDOCK)
        _undock_button.setEnabled(testFlag(self._this.features(), EnumDockWidgetFeature.FLOATABLE))
        _pinn_button = self.titleBar.button(EnumTitleBarButton.AUTO_HIDE)
        _pinn_button.setEnabled(testFlag(self._this.features(), EnumDockWidgetFeature.PINNABLE))
        self.updateTitleBarButtons = False

    def updateTitleBarButtonVisibility(self, is_top_level: bool):
        _container = self._this.dockContainer()
        if _container is None:
            return
        if is_top_level:
            self.titleBar.button(EnumTitleBarButton.CLOSE).setVisible(not _container.isFloating())
            self.titleBar.button(EnumTitleBarButton.AUTO_HIDE).setVisible(not _container.isFloating())
            self.titleBar.button(EnumTitleBarButton.UNDOCK).setVisible(not _container.isFloating() and not self._this.isAutoHide())
            self.titleBar.button(EnumTitleBarButton.TABS_MENU).setVisible(not self._this.isAutoHide())
        else:
            self.titleBar.button(EnumTitleBarButton.CLOSE).setVisible(True)
            self.titleBar.button(EnumTitleBarButton.AUTO_HIDE).setVisible(True)
            self.titleBar.button(EnumTitleBarButton.UNDOCK).setVisible(not self._this.isAutoHide())
            self.titleBar.button(EnumTitleBarButton.TABS_MENU).setVisible(not self._this.isAutoHide())

    def updateMinimumSizeHint(self):
        _min_size = QtCore.QSize()
        for i in range(self.contentsLayout.count()):
            _w = self.contentsLayout.widget(i)
            self.minSizeHint.setHeight(max(self.minSizeHint.height(), _w.minimumSizeHint().height()))
            self.minSizeHint.setWidth(max(self.minSizeHint.width(), _w.minimumSizeHint().width()))


class CDockAreaWidget(QtWidgets.QFrame):
    # This signal is emitted when user clicks on a tab at an index.
    sigTabBarClicked = QtCore.Signal(int)
    # This signal is emitted when the tab bar's current tab is about to be
    # changed. The new current has the given index, or -1 if there isn't a new one.
    sigCurrentChanging = QtCore.Signal(int)

    # This signal is emitted when the tab bar's current tab changes. The new
    # current has the given index, or -1 if there isn't a new one
    sigCurrentChanged = QtCore.Signal(int)

    # This signal is emitted if the visibility of this dock area is toggled via
    # toggle view function
    sigViewToggled = QtCore.Signal(bool)

    def __init__(self, dock_manager: 'CDockManager',
                 parent: 'CDockContainerWidget'):
        '''
        Default Constructor

        Parameters
        ----------
        dock_manager : DockManager
        parent : DockContainerWidget
        '''
        super().__init__(parent)
        self._mgr = DockAreaWidgetMgr(self)
        self._mgr.dockManager = dock_manager
        self._mgr.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
        self._mgr.layout.setContentsMargins(0, 0, 0, 0)
        self._mgr.layout.setSpacing(0)
        self.setLayout(self._mgr.layout)
        self._mgr.createTitleBar()
        self._mgr.contentsLayout = CDockAreaLayout(self._mgr.layout)
        if self._mgr.dockManager:
            self._mgr.dockManager.sigDockAreaCreated.emit(self)

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def onTabCloseRequested(self, index: int):
        '''
        On tab close requested

        Parameters
        ----------
        index : int
        '''
        logger.debug('DockAreaWidget.onTabCloseRequested %s', index)
        _dw = self.dockWidget(index)
        if (testFlag(_dw.features(), EnumDockWidgetFeature.DELETE_ON_CLOSE) or
                testFlag(_dw.features(), EnumDockWidgetFeature.CUSTOM_CLOSE_HANDLING)):
            _dw.closeDockWidgetInternal()
        else:
            _dw.toggleView(False)

    def onDockWidgetFeaturesChanged(self):
        if self._mgr.titleBar is not None:
            self._mgr.updateTitleBarButtonStates()

    def reorderDockWidget(self, from_index: int, to_index: int):
        '''
        Reorder the index position of DockWidget at fromIndx to toIndex if a
        tab in the tabbar is dragged from one index to another one

        Parameters
        ----------
        from_index : int
        to_index : int
        '''
        logger.debug('DockAreaWidget.reorderDockWidget')
        if (from_index >= self._mgr.contentsLayout.count() or
                from_index < 0 or
                to_index >= self._mgr.contentsLayout.count() or
                to_index < 0 or
                from_index == to_index):
            logger.debug('Invalid index for tab movement %s:%s', from_index,
                         to_index)
            return

        _widget = self._mgr.contentsLayout.widget(from_index)
        self._mgr.contentsLayout.removeWidget(_widget)
        self._mgr.contentsLayout.insertWidget(to_index, _widget)
        self.setCurrentIndex(to_index)

    def insertDockWidget(self, index: int, dock_widget: 'CDockWidget',
                         activate: bool = True):
        '''
        Inserts a dock widget into dock area.

        All dockwidgets in the dock area tabified in a stacked layout with
        tabs. The index indicates the index of the new dockwidget in the tabbar
        and in the stacked layout. If the Activate parameter is true, the new
        DockWidget will be the active one in the stacked layout

        Parameters
        ----------
        index : int
        dock_widget : DockWidget
        activate : bool, optional
        '''
        if index < 0 or index > self._mgr.contentsLayout.count():
            index = self._mgr.contentsLayout.count()
        self._mgr.contentsLayout.insertWidget(index, dock_widget)
        dock_widget.tabWidget().setDockAreaWidget(self)
        _tab_widget = dock_widget.tabWidget()

        # Inserting the tab will change the current index which in turn will
        # make the tab widget visible in the slot
        _tab_bar = self._mgr.tabBar()
        _tab_bar.blockSignals(True)
        _tab_bar.insertTab(index, _tab_widget)
        _tab_bar.blockSignals(False)

        _tab_widget.setVisible(not dock_widget.isClosed())
        self._mgr.titleBar.autoHideTitleLabel().setText(dock_widget.windowTitle())

        dock_widget.setProperty('index', index)
        self._mgr.minSizeHint.setHeight(max(self._mgr.minSizeHint.height(), dock_widget.minimumSizeHint().height()))
        self._mgr.minSizeHint.setWidth(max(self._mgr.minSizeHint.width(), dock_widget.minimumSizeHint().width()))
        if activate:
            self.setCurrentIndex(index)
            dock_widget.setClosedState(False)
        if not self.isVisible() and self._mgr.contentsLayout.count() > 1 and not self.dockManager().isRestoringState():
            dock_widget.toggleViewInternal(True)
        self._mgr.updateTitleBarButtonStates()
        self.updateTitleBarVisibility()

    def addDockWidget(self, dock_widget: 'CDockWidget'):
        '''
        Add a new dock widget to dock area. All dockwidgets in the dock area tabified in a stacked layout with tabs

        Parameters
        ----------
        dock_widget : CDockWidget
        '''
        self.insertDockWidget(self._mgr.contentsLayout.count(), dock_widget)

    def removeDockWidget(self, dock_widget: 'CDockWidget'):
        '''
        Removes the given dock widget from the dock area

        Parameters
        ----------
        dock_widget : DockWidget
        '''
        logger.debug('DockAreaWidget.removeDockWidget')
        if dock_widget is None:
            return
        if self.isAutoHide():
            self.autoHideDockContainer().cleanupAndDelete()
            return
        _current_dock_widget = self.currentDockWidget()
        _next_open_dock_widget = self.nextOpenDockWidget(dock_widget) if dock_widget == _current_dock_widget else None
        self._mgr.contentsLayout.removeWidget(dock_widget)
        _tab_w = dock_widget.tabWidget()
        _tab_w.hide()
        self._mgr.tabBar().removeTab(_tab_w)
        _tab_w.setParent(dock_widget)
        dock_widget.setDockArea(None)
        _dock_container = self.dockContainer()
        if _next_open_dock_widget is not None:
            self.setCurrentDockWidget(_next_open_dock_widget)
        elif self._mgr.contentsLayout.isEmpty() and _dock_container.dockAreaCount >= 1:
            logger.debug('Dock Area empty')
            _dock_container.removeDockArea(self)
            self.deleteLater()
            if _dock_container.dockAreaCount() == 0:
                _fwc = _dock_container.floatingWidget()
                if _fwc:
                    _fwc.hide()
                    _fwc.deleteLater()
        elif dock_widget == _current_dock_widget:
            self.hideAreaWithNoVisibleContent()
        self._mgr.updateTitleBarButtonStates()
        self.updateTitleBarVisibility()
        self._mgr.updateMinimumSizeHint()
        _top_level_dw = _dock_container.topLevelDockWidget()
        if _top_level_dw:
            _top_level_dw.emitTopLevelChanged(True)

        if DEBUG_LEVEL > 0:
            _dock_container.dump_layout()

    def toggleDockWidgetView(self, dock_widget: 'DockWidget', open_: bool):
        '''
        Called from dock widget if it is opened or closed

        Parameters
        ----------
        dock_widget : DockWidget
            Unused
        open : bool
            Unused
        '''
        # pylint: disable=unused-argument
        self.updateTitleBarVisibility()

    def nextOpenDockWidget(self, dock_widget: 'DockWidget'
                           ) -> Optional['DockWidget']:
        '''
        This is a helper function to get the next open dock widget to activate
        if the given DockWidget will be closed or removed. The function returns
        the next widget that should be activated or nullptr in case there are
        no more open widgets in this area.

        Parameters
        ----------
        dock_widget : DockWidget

        Returns
        -------
        value : DockWidget
        '''
        _open_dock_widgets = self.openedDockWidgets()
        _count = len(_open_dock_widgets)
        if _count > 1 or (_count == 1 and _open_dock_widgets[0] != dock_widget):
            if _open_dock_widgets[-1] == dock_widget:
                _next_dock_widget = _open_dock_widgets[-2]
                # search backwards for widget with tab
                for i in reversed(range(len(_open_dock_widgets) - 2)):
                    _dw = _open_dock_widgets[i]
                    if not testFlag(_dw.features(), EnumDockWidgetFeature.NO_TAB):
                        return _dw
                return _next_dock_widget
            else:
                _idx = _open_dock_widgets.index(dock_widget)
                _next_dock_widget = _open_dock_widgets[_idx + 1]
                # search forwards for widget with tab
                for i in range(_idx + 1, _count):
                    _dw = _open_dock_widgets[i]
                    if not testFlag(_dw.features(), EnumDockWidgetFeature.NO_TAB):
                        return _dw
                # search backwards for widget with tab
                for i in reversed(range(_idx - 1)):
                    _dw = _open_dock_widgets[i]
                    if not testFlag(_dw.features(), EnumDockWidgetFeature.NO_TAB):
                        return _dw
                return _next_dock_widget
        return None

    def index(self, dock_widget: 'CDockWidget') -> int:
        '''
        Returns the index of the given DockWidget in the internal layout

        Parameters
        ----------
        dock_widget : DockWidget

        Returns
        -------
        value : int
        '''
        return self._mgr.contentsLayout.indexOf(dock_widget)

    def hideAreaWithNoVisibleContent(self):
        '''
        Call this function, if you already know, that the dock does not contain
        any visible content (any open dock widgets).
        '''
        self.toggle_view(False)

        # Hide empty parent splitters
        _splitter = findParent(CDockSplitter, self)
        hideEmptyParentSplitters(_splitter)

        # Hide empty floating widget
        _container = self.dockContainer()
        if not _container.isFloating() and not testFlag(self.dockManager().flags(), EnumDockAreaFlag.HideSingleWidgetTitleBar):
            return

        self.updateTitleBarVisibility()
        _top_level_widget = _container.topLevelDockWidget()
        _floating_widget = _container.floatingWidget()
        if _top_level_widget is not None:
            if _floating_widget:
                _floating_widget.update_window_title()
            emitTopLevelEventForWidget(_top_level_widget, True)

        elif not _container.openedDockAreas() and _floating_widget:
            _floating_widget.hide()
        if self.isAutoHide():
            self.autoHideDockContainer().hide()

    def updateTitleBarVisibility(self):
        '''
        Updates the dock area layout and components visibility
        '''
        _container = self.dockContainer()
        if not _container:
            return
        if self._mgr.titleBar is None:
            return
        _is_auto_hide = self.isAutoHide()
        if not testFlag(self.dockManager().flags(), EnumDockMgrConfigFlag.AlwaysShowTabs):
            _hidden = _container.hasTopLevelDockWidget() and _container.isFloating() or testFlag(self.dockManager().flags,
                                                                                                 EnumDockMgrConfigFlag.HideSingleCentralWidgetTitleBar)
            _hidden |= testFlag(self._mgr.flags, EnumDockAreaFlag.HideSingleWidgetTitleBar) and self.openDockWidgetsCount() == 1
            _hidden &= not _is_auto_hide
            self._mgr.titleBar.setVisible(not _hidden)
        if self.isAutoHideFeatureEnabled():
            _tb = self._mgr.titleBar.tabBar()
            _tb.setVisible(not _is_auto_hide)
            self._mgr.titleBar.autoHideTitleLabel().setVisible(_is_auto_hide)
            self.updateTitleBarButtonVisibility(_container.topLevelDockArea() is self)

    def updateAutoHideButtonCheckState(self):
        _ah_btn = self.titleBarButton(EnumTitleBarButton.AUTO_HIDE)
        _ah_btn.blockSignals(True)
        _ah_btn.setChecked(self.isAutoHide())
        _ah_btn.blockSignals(False)

    def updateTitleBarButtonVisibility(self, is_top_level):
        self._mgr.updateTitleBarButtonVisibility(is_top_level)

    def updateTitleBarButtonsToolTips(self):
        _btn = self.titleBarButton(EnumTitleBarButton.CLOSE)
        _btn.setToolTip(self.titleBar().titleBarButtonToolTip(EnumTitleBarButton.CLOSE))
        _btn = self.titleBarButton(EnumTitleBarButton.AUTO_HIDE)
        _btn.setToolTip(self.titleBar().titleBarButtonToolTip(EnumTitleBarButton.AUTO_HIDE))

    def internalSetCurrentDockWidget(self, dock_widget: 'CDockWidget'):
        '''
        This is the internal private function for setting the current widget.
        This function is called by the public setCurrentDockWidget() function
        and by the dock manager when restoring the state

        Parameters
        ----------
        dock_widget : DockWidget
        '''
        _index = self.index(dock_widget)
        if _index < 0:
            return

        self.setCurrentIndex(_index)
        dock_widget.setCloseState(False)

    def markTitleBarMenuOutdated(self):
        '''
        Marks tabs menu to update
        '''
        if self._mgr.titleBar:
            self._mgr.titleBar.markTabsMenuOutdated()

    def minimumSizeHint(self) -> QtCore.QSize:
        if not self._mgr.minSizeHint.isValid():
            return super().minimumSizeHint()
        if self._mgr.titleBar.isVisible():
            return self._mgr.minSizeHint + QtCore.QSize(0, self._mgr.titleBar.minimumSizeHint().height())
        else:
            return self._mgr.minSizeHint

    def toggleView(self, open_: bool):
        '''
        Toggle view

        Parameters
        ----------
        open_ : bool
        '''
        self.setVisible(open_)
        self.sigViewToggled.emit(open_)

    def toggleAutoHide(self, location: EnumSideBarLocation=EnumSideBarLocation.NONE):

        if not self.isAutoHideFeatureEnable():
            return
        self.setAutoHide(not self.isAutoHide(), location)

    def dockManager(self) -> 'CDockManager':
        '''
        Returns the dock manager object this dock area belongs to

        Returns
        -------
        value : DockManager
        '''
        return self._mgr.dockManager

    def dockContainer(self) -> 'CDockContainerWidget':
        '''
        Returns the dock container widget this dock area widget belongs to or 0 if there is no

        Returns
        -------
        value : DockContainerWidget
        '''

        return findParent('DockContainerWidget', self)

    def autoHideDockContainer(self):
        return self._mgr.autoHideDockContainer

    def setAutoHide(self, enable: bool, location: EnumSideBarLocation):
        if not self.isAutoHideFeatureEnable():
            return
        if not enable:
            if self.isAutoHide():
                self.autoHideDockContainer().moveContentsToParent()
            return
        _area = self.calculateSideTabBarArea() if location == EnumSideBarLocation.NONE else location
        for x in self.openedDockWidgets():
            if enable == self.isAutoHide():
                continue
            if not testFlag(x.features(), EnumDockWidgetFeature.PINNABLE):
                continue
            self.dockContainer().createAndSetupAutoHideContainer(_area, x)

    def setAutoHideDockContainer(self, auto_hide_dock_container: CAutoHideDockContainer):
        self._mgr.autoHideDockContainer = auto_hide_dock_container
        self.updateAutoHideButtonCheckState()
        self.updateTitleBarButtonsToolTips()

    def isTopLevelArea(self):
        _c = self.dockContainer()
        if _c is None:
            return
        return _c.topLevelArea() is self

    def isAutoHide(self):
        return self._mgr.autoHideDockContainer is not None

    def isCentralWidgetArea(self):
        if self.dockWidgetsCount() != 1:
            return False
        return self.dockManager().centralWidget() is self.dockWidgets().constFirst()

    def titleBarGeometry(self) -> QtCore.QRect:
        '''
        Returns the rectangle of the title area

        Returns
        -------
        value : QRect
        '''
        return self._mgr.titleBar.geometry()

    def contentAreaGeometry(self) -> QtCore.QRect:
        '''
        Returns the rectangle of the content

        Returns
        -------
        value : QRect
        '''
        return self._mgr.contentsLayout.geometry()

    def containsCentralWidget(self):
        _cw = self.dockManager().centeralWidget()
        for x in self.dockWidgets():
            if x is _cw:
                return True
        return False

    def dockWidgetsCount(self) -> int:
        '''
        Returns the number of dock widgets in this area

        Returns
        -------
        value : int
        '''
        return self._mgr.contentsLayout.count()

    def dockWidgets(self) -> list:
        '''
        Returns a list of all dock widgets in this dock area. This list
        contains open and closed dock widgets.

        Returns
        -------
        value : list of DockWidget
        '''
        return [
            self.dockWidget(i)
            for i in range(self._mgr.contentsLayout.count())
        ]

    def openDockWidgetsCount(self) -> int:
        '''
        Returns the number of dock widgets in this area

        Returns
        -------
        value : int
        '''
        _cnt = 0
        for i in range(self._mgr.contentsLayout.count()):
            if not self.dockWidget(i).isClosed():
                _cnt += 1
        return _cnt

    def openedDockWidgets(self) -> list:
        '''
        Returns a list of dock widgets that are not closed

        Returns
        -------
        value : list of DockWidget
        '''
        return [self.dockWidget(i) for i in range(self._mgr.contentsLayout.count())
                if not self.dockWidget(i).isClosed()
                ]

    def dockWidget(self, index: int) -> 'CDockWidget':
        '''
        Returns a dock widget by its index

        Parameters
        ----------
        index : int

        Returns
        -------
        value : DockWidget
        '''
        return self._mgr.contentsLayout.widget(index)

    def currentIndex(self) -> int:
        '''
        Returns the index of the current active dock widget or -1 if there are
        is no active dock widget (ie.e if all dock widgets are closed)

        Returns
        -------
        value : int
        '''
        return self._mgr.contentsLayout.currentIndex()

    def indexOfFirstOpenDockWidget(self) -> int:
        '''
        Returns the index of the first open dock widgets in the list of dock
        widgets.

        This function is here for performance reasons. Normally it would be
        possible to take the first dock widget from the list returned by
        openedDockWidgets() function. But that function enumerates all dock widgets
        while this functions stops after the first open dock widget. If there are no
        open dock widgets, the function returns -1.

        Returns
        -------
        value : int
        '''
        for i in range(self._mgr.contentsLayout.count()):
            if not self.dock_widget(i).isClosed():
                return i

        return -1

    def currentDockWidget(self) -> Optional['CDockWidget']:
        '''
        Returns the current active dock widget or a nullptr if there is no
        active dock widget (i.e. if all dock widgets are closed)

        Returns
        -------
        value : DockWidget
        '''
        _current_index = self.currentIndex()
        if _current_index < 0:
            return None

        return self.dockWidget(_current_index)

    def setCurrentDockWidget(self, dock_widget: 'CDockWidget'):
        '''
        Shows the tab with the given dock widget

        Parameters
        ----------
        dock_widget : DockWidget
        '''
        if self.dockManager().isRestoringState():
            return

        self.internalSetCurrentDockWidget(dock_widget)

    def saveState(self, stream: QtCore.QXmlStreamWriter):
        '''
        Saves the state into the given stream

        Parameters
        ----------
        stream : QXmlStreamWriter
        '''
        stream.writeStartElement("Area")
        stream.writeAttribute("Tabs", str(self._mgr.contentsLayout.count()))
        _current_dock_widget = self.currentDockWidget()
        _name = _current_dock_widget.objectName() if _current_dock_widget else ''
        stream.writeAttribute("Current", _name)

        if self._mgr.allowedAreas != self.defaultAllowedAreas:
            stream.writeAttribute("AllowedAreas", str(self._mgr.allowedAreas))
        if self._mgr.flags != self.defaultFlags:
            stream.writeAttribute("Flags", str(self._mgr.flags))
        logger.debug('DockAreaWidget.saveState TabCount: %s current: %s',
                     self._mgr.contentsLayout.count(), _name)

        for i in range(self._mgr.contentsLayout.count()):
            self.dockWidget(i).saveState(stream)
        stream.writeEndElement()

    def restoreState(self, s: CDockStateReader, created_widget: 'CDockAreaWidget', testing: bool, container: 'CDockContainerWidget'):
        # todo: different
        _ok = int(s.attributes().value("Tabs"))
        if not _ok:
            return False
        _current_w = s.attributes().value("Current")
        logger.debug('Restore NodeDockArea Tabs:: %s current: %s',
                     _ok, _current_w)
        _dm = container.dockManager()
        _da = None
        if not testing:
            _da = CDockAreaWidget(_dm, container)
            _allowed_areas_attr = s.attributes().value("AllowedAreas")
            if not _allowed_areas_attr.isEmpty():
                _da.setAllowedAreas(int(_allowed_areas_attr))
            _flags_attr = s.attributes().value("Flags")
            if not _flags_attr.isEmpty():
                _da.setDockAreaFlags(int(_flags_attr))
        while s.readNextStartElement():
            if s.name() != 'Widget':
                continue
            _obj_name = s.attributes().value("Name")
            if _obj_name.isEmpty():
                return False
            _closed = s.attributes().value("Closed")
            if not int(_closed):
                return False
            s.skipCurrentElement()
            _dw = self.dockManager().findDockWidget(_obj_name.toString())
            if _dw is None or testing:
                continue
            logger.debug('Dock Widget found - parent=%s' % _dw.parent())
            if _dw.autoHideDockContainer():
                _dw.autoHideDockContainer().cleanupAndDelete()
            _da.hide()
            _da.addDockWidget(_dw)
            _dw.setToggleViewActionChecked(not _closed)
            _dw.setClosedState(_closed)
            _dw.setProperty('close', _closed)
            _dw.setProperty('dirty', False)
        if testing:
            return True
        if not _da.dockWidgetsCount():
            _da = None
        else:
            _da.setProperty('currentDockWidget', _current_w)
        created_widget = _da
        return True

    def features(self, mode: EnumBitwiseOP=EnumBitwiseOP.AND) -> 'EnumDockWidgetFeature':
        '''
        This functions returns the dock widget features of all dock widget in
        this area. A bitwise and is used to combine the flags of all dock
        widgets. That means, if only dock widget does not support a certain
        flag, the whole dock are does not support the flag.

        Returns
        -------
        value : DockWidgetFeature
        '''

        if EnumBitwiseOP.AND == mode:
            _features = EnumDockWidgetFeature.ALL
            for x in self.dockWidgets():
                _features &= x.features()
            return _features
        else:
            _features = EnumDockWidgetFeature.NONE
            for x in self.dockWidgets():
                _features |= x.features()
            return _features

    def titleBarButton(self, which: EnumTitleBarButton) -> QtWidgets.QAbstractButton:
        '''
        Returns the title bar button corresponding to the given title bar button identifier

        Parameters
        ----------
        which : EnumTitleBarButton

        Returns
        -------
        value : QAbstractButton
        '''
        return self._mgr.titleBar.button(which)

    def titleBar(self):
        return self._mgr.titleBar

    def setVisible(self, visible: bool):
        '''
        Update the close button if visibility changed

        Parameters
        ----------
        visible : bool
        '''
        super().setVisible(visible)
        if self._mgr.updateTitleBarButtons:
            self._mgr.updateTitleBarButtonStates()

    def setCurrentIndex(self, index: int):
        '''
        This activates the tab for the given tab index. If the dock widget for
        the given tab is not visible, the this function call will make it visible.

        Parameters
        ----------
        index : int
        '''
        _tab_bar = self._mgr.tabBar()
        if index < 0 or index > (_tab_bar.count() - 1):
            logger.warning('Invalid index %s', index)
            return
        _cw = self._mgr.contentsLayout.currentWidget()
        _nw = self._mgr.contentsLayout.widget(index)
        if _cw is _nw and not _nw.isHidden():
            return
        self.sigCurrentChanging.emit(index)
        _tab_bar.setCurrentIndex(index)
        self._mgr.contentsLayout.setCurrentIndex(index)
        self._mgr.contentsLayout.currentWidget().show()
        self.sigCurrentChanging.emit(index)

    def allowedAreas(self):
        return self._mgr.allowedAreas

    def setAllowedAreas(self, areas: EnumDockWidgetArea):
        self._mgr.allowedAreas = areas

    def dockAreaFlags(self):
        return self._mgr.flags

    def setDockAreaFlags(self, flags: EnumDockAreaFlag):
        _changed_flags = self._mgr.flags ^ flags
        self._mgr.flags = flags
        if testFlag(_changed_flags, EnumDockAreaFlag.HideSingleWidgetTitleBar):
            self.updateTitleBarVisibility()

    def setDockAreaFlag(self, flag, on):
        _flags = self.dockAreaFlags()
        _flags=setFlag(_flags, flag, on)
        self.setDockAreaFlags(_flags)

    def closeArea(self):
        '''
        Closes the dock area and all dock widgets in this area
        '''
        _dws = self.openedDockWidgets()
        if len(_dws) == 1 and (testFlag(_dws[0].features(), EnumDockWidgetFeature.DELETE_ON_CLOSE) or
                               testFlag(_dws[0].features(), EnumDockWidgetFeature.CUSTOM_CLOSE_HANDLING)) and not self.isAutoHide():
            _dws[0].closeDockWidgetInternal()
        else:
            for x in _dws:
                if (testFlag(_dws[0].features(), EnumDockWidgetFeature.DELETE_ON_CLOSE) or
                        testFlag(_dws[0].features(), EnumDockWidgetFeature.CUSTOM_CLOSE_HANDLING) or testFlag(_dws[0].features(),
                                                                                                              EnumDockWidgetFeature.FORCE_CLOSE_WITH_AREA)):
                    x.closeDockWidgetInternal()
                elif testFlag(_dws[0].features(), EnumDockWidgetFeature.DELETE_ON_CLOSE) and self.isAutoHide():
                    x.closeDockWidgetInternal()
                else:
                    x.toggleView(False)

    def calculateSideTabBarArea(self):
        _container = self.dockContainer()
        _content_rect = _container.contentRect()
        _borders = EnumBorderLocation.BorderNone
        _da_t_l = self.mapTo(_container, _content_rect.topLeft())
        _da_rect = QtCore.QRect()
        _da_rect.moveTo(_da_t_l)
        _aspect_ration = _da_rect.width() / (max(1, _da_rect.height()) * 1.0)
        _size_ratio = _content_rect.width() / _da_rect.width()
        _mini_border_distance = 16
        _horizontal_orientation = (_aspect_ration > 1.0 and _size_ratio < 3.0)
        # measure border distances - a distance less than 16 px means we touch the
        _border_distance = []
        _distance = abs(_content_rect.topLeft().y() - _da_rect.topLeft().y())
        _border_distance[EnumSideBarLocation.TOP] = 0 if (_distance < _mini_border_distance) else _distance
        if not _border_distance[EnumSideBarLocation.TOP]:
            _borders |= EnumBorderLocation.BorderTop

        _distance = abs(_content_rect.bottomRight().y() - _da_rect.bottomRight().y())
        _border_distance[EnumSideBarLocation.BOTTOM] = 0 if (_distance < _mini_border_distance) else _distance
        if not _border_distance[EnumSideBarLocation.BOTTOM]:
            _borders |= EnumBorderLocation.BorderBottom

        _distance = abs(_content_rect.topLeft().x() - _da_rect.topLeft().x())
        _border_distance[EnumSideBarLocation.LEFT] = 0 if (_distance < _mini_border_distance) else _distance
        if not _border_distance[EnumSideBarLocation.LEFT]:
            _borders |= EnumBorderLocation.BorderLeft

        _distance = abs(_content_rect.bottomRight().x() - _da_rect.bottomRight().x())
        _border_distance[EnumSideBarLocation.RIGHT] = 0 if (_distance < _mini_border_distance) else _distance
        if not _border_distance[EnumSideBarLocation.RIGHT]:
            _borders |= EnumBorderLocation.BorderRight

        _side_tab_loc = EnumSideBarLocation.RIGHT
        if _borders:
            if _borders == EnumBorderLocation.BorderAll:
                _side_tab_loc = EnumSideBarLocation.BOTTOM if _horizontal_orientation else EnumSideBarLocation.RIGHT
            elif _borders == EnumBorderLocation.BorderVerticalBottom:
                _side_tab_loc = EnumSideBarLocation.BOTTOM
            elif _borders == EnumBorderLocation.BorderVerticalTop:
                _side_tab_loc = EnumSideBarLocation.TOP
            elif _borders == EnumBorderLocation.BorderHorizontalLeft:
                _side_tab_loc = EnumSideBarLocation.LEFT
            elif _borders == EnumBorderLocation.BorderHorizontalRight:
                _side_tab_loc = EnumSideBarLocation.RIGHT
            elif _borders == EnumBorderLocation.BorderVertical:
                _side_tab_loc = EnumSideBarLocation.BOTTOM
            elif _borders == EnumBorderLocation.BorderHorizontal:
                _side_tab_loc = EnumSideBarLocation.RIGHT
            # corner
            elif _borders == EnumBorderLocation.BorderTopLeft:
                _side_tab_loc = EnumSideBarLocation.TOP if _horizontal_orientation else EnumSideBarLocation.LEFT
            elif _borders == EnumBorderLocation.BorderTopRight:
                _side_tab_loc = EnumSideBarLocation.TOP if _horizontal_orientation else EnumSideBarLocation.RIGHT
            elif _borders == EnumBorderLocation.BorderBottomLeft:
                _side_tab_loc = EnumSideBarLocation.BOTTOM if _horizontal_orientation else EnumSideBarLocation.LEFT
            elif _borders == EnumBorderLocation.BorderBottomRight:
                _side_tab_loc = EnumSideBarLocation.BOTTOM if _horizontal_orientation else EnumSideBarLocation.RIGHT
            # only one border touched
            elif _borders == EnumBorderLocation.BorderLeft:
                _side_tab_loc = EnumSideBarLocation.LEFT
            elif _borders == EnumBorderLocation.BorderRight:
                _side_tab_loc = EnumSideBarLocation.RIGHT
            elif _borders == EnumBorderLocation.BorderTop:
                _side_tab_loc = EnumSideBarLocation.TOP
            elif _borders == EnumBorderLocation.BorderBottom:
                _side_tab_loc = EnumSideBarLocation.BOTTOM
        return _side_tab_loc

    def closeOtherAreas(self):
        '''
        This function closes all other areas except of this area
        '''
        self.dockContainer().closeOtherAreas(self)


if WINDOWS:
    def event(self, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.Type.PlatformSurface:
            return True
        return super().event(event)
