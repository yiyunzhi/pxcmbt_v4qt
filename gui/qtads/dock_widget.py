import logging
import typing
from typing import TYPE_CHECKING, Callable
from PySide6 import QtCore, QtGui, QtWidgets
from .define import (EnumDockWidgetFeature, EnumDockMgrConfigFlag,
                     DOCK_MANAGER_DEFAULT_CONFIG, AUTO_HIDE_DEFAULT_CONFIG,
                     EnumAutoHideFlag,
                     EnumWidgetState, EnumToggleViewActionMode,
                     EnumInsertMode, EnumMinimumSizeHintMode,
                     EnumSideBarLocation)
from .dock_components_factory import DEFAULT_COMPONENT_FACTORY
from .util import findParent, emitTopLevelEventForWidget, setFlag
from .floating_dock_container import CFloatingDockContainer

if TYPE_CHECKING:
    from .dock_manager import CDockManager
    from .dock_area_widget import CDockAreaWidget
    from .dock_widget_tab import CDockWidgetTab
    from .auto_hide_tab import CAutoHideTab

logger = logging.getLogger(__name__)


class WidgetFactory:
    def __init__(self, func: Callable, insert_mode: EnumInsertMode):
        self.createWidget = None
        self.insertMode = EnumInsertMode.AUTO_SCROLL_AREA


class DockWidgetMgr:
    _this: ['CDockWidget', None]
    layout: [QtWidgets.QBoxLayout, None]
    widget: [QtWidgets.QWidget, None]
    tabWidget: ['CDockWidgetTab', None]
    features: EnumDockWidgetFeature
    dockManager: ['CDockManager', None]
    dockArea: ['CDockAreaWidget', None]
    toggleView_action: [QtGui.QAction, None]
    closed: bool
    scrollArea: [QtWidgets.QScrollArea, None]
    toolBar: [QtWidgets.QToolBar, None]
    toolBarStyleDocked: QtCore.Qt.ToolButtonStyle
    toolBarStyleFloating: QtCore.Qt.ToolButtonStyle
    toolBarIconSizeDocked: QtCore.QSize
    toolBarIconSizeFloating: QtCore.QSize
    isFloatingTopLevel: bool
    titleBarActions: list
    minimumSizeHintMode: EnumMinimumSizeHintMode
    factory: [WidgetFactory, None] = None
    sideTabWidget: 'CAutoHideTab'

    def __init__(self, _this: 'CDockWidget'):
        self._this = _this
        self.layout = None
        self.widget = None
        self.tabWidget = None
        self.features = EnumDockWidgetFeature.DEFAULT
        self.dockManager = None
        self.dockArea = None
        self.toggleViewAction = None
        self.closed = False
        self.scrollArea = None
        self.toolBar = None
        self.sideTabWidget = None
        self.toolBarStyleDocked = QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly
        self.toolBarStyleFloating = QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon
        self.toolBarIconSizeDocked = QtCore.QSize(16, 16)
        self.toolBarIconSizeFloating = QtCore.QSize(24, 24)
        self.isFloatingTopLevel = False
        self.titleBarActions = []
        self.minimumSizeHintMode = EnumMinimumSizeHintMode.FROM_DOCK_WIDGET
        self.factory = None

    def showDockWidget(self):
        '''
        Show dock widget
        '''
        if not self.widget:
            if not self.createWidgetFromFactory():
                assert EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE not in self.features, "DeleteContentOnClose flag was set, but the widget factory is missing or it doesnt return a valid QWidget. "
                return
        if not self.dockArea:
            _floating_widget = CFloatingDockContainer(dock_widget=self._this)
            _floating_widget.resize(self.widget.sizeHint() if self.widget else self._this.sizeHint())
            self.tabWidget.show()
            _floating_widget.show()
        else:
            self.dockArea.setCurrentDockWidget(self._this)
            self.dockArea.toggleView(True)
            self.tabWidget.show()
            _splitter = findParent(QtWidgets.QSplitter, self.dockArea)
            while _splitter and not _splitter.isVisible() and not self.dockArea.isAutoHide():
                _splitter.show()
                _splitter = findParent(QtWidgets.QSplitter, _splitter)
            _container = self.dockArea.dockContainer()
            if _container.isFloating():
                _floating_w = findParent(CFloatingDockContainer, _container)
                _floating_w.show()
            # If this widget is pinned and there are no opened dock widgets, unpin the auto hide widget by moving it's contents to parent container
            # While restoring state, opened dock widgets are not valid
            if len(_container.openedDockWidgets()) == 0 and self.dockArea.isAutoHide() and not self.dockManager.isRestoringState():
                self.dockArea.autoHideDockContainer().moveContentsToParent()

    def hideDockWidget(self):
        '''
        Hide dock widget.
        '''
        self.tabWidget.hide()
        self.updateParentDockArea()
        self.closeAutoHideDockWidgetsIfNeeded()
        if EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE in self.features:
            self.widget.deleteLater()
            self.widget = None

    def updateParentDockArea(self):
        '''
        Hides a dock area if all dock widgets in the area are closed. This
        function updates the current selected tab and hides the parent dock
        area if it is empty
        '''
        if not self.dockArea:
            return
        """
        we don't need to change the current tab if the
	    current dock widget is not the one being closed
        """
        if self.dockArea.currentDockWidget() is not self._this:
            return

        _next_dock_widget = self.dockArea.nextOpenDockWidget(self._this)
        if _next_dock_widget is not None:
            self.dockArea.setCurrentDockWidget(_next_dock_widget)
        else:
            self.dockArea.hideAreaWithNoVisibleContent()

    def closeAutoHideDockWidgetsIfNeeded(self):
        _container = self._this.dockContainer()
        if _container is None:
            return
        if self._this.dockManager().isRestoringState():
            return
        if _container.openedDockWidgets():
            return
        for x in _container.autoHideWidgets():
            _w = x.dockWidget()
            if _w is self._this:
                continue
            _w.toggleView(False)

    def setupToolBar(self):
        '''
        Setup the top tool bar
        '''
        self.toolBar = QtWidgets.QToolBar(self._this)
        self.toolBar.setObjectName("dockWidgetToolBar")
        self.layout.insertWidget(0, self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(16, 16))
        self.toolBar.toggleViewAction().setEnabled(False)
        self.toolBar.toggleViewAction().setVisible(False)
        self._this.topLevelChanged.connect(self._this.setToolbarFloatingStyle)

    def setupScrollArea(self):
        '''
        Setup the main scroll area
        '''
        self.scrollArea = QtWidgets.QScrollArea(self._this)
        self.scrollArea.setObjectName("dockWidgetScrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.layout.addWidget(self.scrollArea)

    def createWidgetFromFactory(self):
        if EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE not in self.features:
            return False
        if self.factory is None:
            return False
        _w = self.factory.createWidget(self._this)
        if _w is None:
            return False
        self._this.setWidget(_w, self.factory.insertMode)
        return True


class CDockWidget(QtWidgets.QFrame):
    # This signal is emitted if the dock widget is opened or closed
    sigViewToggled = QtCore.Signal(bool)
    # This signal is emitted if the dock widget is closed
    sigClosed = QtCore.Signal()
    # This signal is emitted if the window title of this dock widget changed
    sigTitleChanged = QtCore.Signal(str)
    # This signal is emitted when the floating property changes. The topLevel
    # parameter is true if the dock widget is now floating; otherwise it is
    # false.
    sigTopLevelChanged = QtCore.Signal(bool)
    sigFeaturesChanged = QtCore.Signal(EnumDockWidgetFeature)
    sigVisibilityChanged = QtCore.Signal(bool)
    sigCloseRequested = QtCore.Signal()

    def __init__(self, title: str, parent: QtWidgets.QWidget = None):
        '''
        This constructor creates a dock widget with the given title. The title
        is the text that is shown in the window title when the dock widget is
        floating and it is the title that is shown in the titlebar or the tab
        of this dock widget if it is tabified. The object name of the dock
        widget is also set to the title. The object name is required by the
        dock manager to properly save and restore the state of the dock widget.
        That means, the title needs to be unique. If your title is not unique
        or if you would like to change the title during runtime, you need to
        set a unique object name explicitely by calling setObjectName() after
        construction. Use the layoutFlags to configure the layout of the dock
        widget.

        Parameters
        ----------
        title : str
        parent : QWidget
        '''
        super().__init__(parent)
        self._mgr = DockWidgetMgr(self)
        self._mgr.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
        self._mgr.layout.setContentsMargins(0, 0, 0, 0)
        self._mgr.layout.setSpacing(0)
        self.setLayout(self._mgr.layout)
        self.setWindowTitle(title)
        self.setObjectName(title)

        self._mgr.tabWidget = DEFAULT_COMPONENT_FACTORY.createDockWidgetTab(self)
        self._mgr.toggleViewAction = QtGui.QAction(title, self)
        self._mgr.toggleViewAction.setCheckable(True)
        self._mgr.toggleViewAction.triggered.connect(self.toggleView)
        self.setToolbarFloatingStyle(False)
        if EnumDockMgrConfigFlag.FocusHighlighting in DOCK_MANAGER_DEFAULT_CONFIG:
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

    def __repr__(self):
        return f'<{self.__class__.__name__} title={self.windowTitle()!r}>'

    def setToggleViewActionChecked(self, checked):
        _action = self._mgr.toggleViewAction
        _action.blockSignals(True)
        _action.setChecked(checked)
        _action.blockSignals(False)

    def setWidget(self, widget: QtWidgets.QWidget, insert_mode: EnumInsertMode = EnumInsertMode.AUTO_SCROLL_AREA):
        '''
                Sets the widget for the dock widget to widget. The InsertMode defines
                how the widget is inserted into the dock widget. The content of a dock
                widget should be resizable do a very small size to prevent the dock
                widget from blocking the resizing. To ensure, that a dock widget can be
                resized very well, it is better to insert the content+ widget into a
                scroll area or to provide a widget that is already a scroll area or
                that contains a scroll area. If the InsertMode is AutoScrollArea, the
                DockWidget tries to automatically detect how to insert the given
                widget.

                If the widget is derived from QScrollArea (i.e. an QAbstractItemView),
                then the widget is inserted directly. If the given widget is not a
                scroll area, the widget will be inserted into a scroll area. To force
                insertion into a scroll area, you can also provide the InsertMode
                ForceScrollArea. To prevent insertion into a scroll area, you can
                provide the InsertMode ForceNoScrollArea

                Parameters
                ----------
                widget : QWidget
                insert_mode : InsertMode
                '''
        if self._mgr.widget:
            self.takeWidget()
        _is_scroll_area = isinstance(widget, QtWidgets.QAbstractScrollArea)
        if _is_scroll_area or EnumInsertMode.FORCE_NO_SCROLL_AREA == insert_mode:
            self._mgr.layout.addWidget(widget)
            if _is_scroll_area:
                _viewport = widget.viewport()
                if _viewport is not None:
                    _viewport.setProperty("dockWidgetContent", True)
        else:
            self._mgr.setupScrollArea()
            self._mgr.scrollArea.setWidget(widget)
        self._mgr.widget = widget
        self._mgr.widget.setProperty("dockWidgetContent", True)

    def setWidgetFactory(self, create_widget: Callable, insert_mode: EnumInsertMode):
        if self._mgr.factory:
            del self._mgr.factory
        self._mgr.factory = WidgetFactory(create_widget, insert_mode)

    def takeWidget(self):
        _w = None
        if self._mgr.scrollArea is not None:
            self._mgr.layout.removeWidget(self._mgr.scrollArea)
            _w = self._mgr.scrollArea.takeWidget()
            self._mgr.scrollArea = None
            self._mgr.widget = None
        elif self._mgr.widget is not None:
            self._mgr.layout.removeWidget(self._mgr.widget)
            _w = self._mgr.widget
            self._mgr.widget = None
        if _w is not None:
            _w.setParent(None)
        return _w

    def autoHideDockContainer(self):
        if self._mgr.dockArea is None:
            return None
        return self._mgr.dockArea.autoHideDockContainer()

    def features(self):
        return self._mgr.features

    def setFeatures(self, features: EnumDockWidgetFeature):
        if self._mgr.features == features:
            return
        self._mgr.features = features
        self.sigFeaturesChanged.emit(self._mgr.features)
        self._mgr.tabWidget.onDockWidgetFeaturesChanged()
        if self.dockAreaWidget():
            self.dockAreaWidget().onDockWidgetFeaturesChanged()

    def setFeature(self, flag: EnumDockWidgetFeature, on: bool):
        _features = self.features()
        setFlag(_features, flag, on)
        self.setFeatures(_features)

    def dockManager(self):
        return self._mgr.dockManager

    def setDockManager(self, dm: 'CDockManager'):
        self._mgr.dockManager = dm

    def dockContainer(self):
        if self._mgr.dockArea:
            return self._mgr.dockArea.dockContainer()
        else:
            return None

    def floatingDockContainer(self):
        _dc = self.dockContainer()
        return _dc.floatingWidget() if _dc is not None else None

    def dockAreaWidget(self):
        return self._mgr.dockArea

    def sideTabWidget(self):
        return self._mgr.sideTabWidget

    def setSideTabWidget(self, side_tab: 'CAutoHideTab'):
        self._mgr.sideTabWidget = side_tab

    def isAutoHide(self):
        # modified: the widget remove from layout still referenced by self._mgr.sideTabWidget
        if self._mgr.sideTabWidget is None:
            return False
        else:
            return self._mgr.sideTabWidget.sideBar() is not None
        # return self._mgr.sideTabWidget is not None

    def isFloating(self):
        if not self.isInFloatingContainer():
            return False
        return self.dockContainer().topLevelDockWidget() is self

    def isInFloatingContainer(self):
        _c = self.dockContainer()
        if _c is None:
            return False
        if not _c.isFloating():
            return False
        return True

    def isClosed(self):
        return self._mgr.closed

    def toggleViewAction(self):
        return self._mgr.toggleViewAction

    def setToggleViewActionMode(self, mode: EnumToggleViewActionMode):
        if EnumToggleViewActionMode.TOGGLE == mode:
            self._mgr.toggleViewAction.setCheckable(True)
            self._mgr.toggleViewAction.setIcon(QtGui.QIcon())
        else:
            self._mgr.toggleViewAction.setCheckable(False)
            self._mgr.toggleViewAction.setIcon(self._mgr.tabWidget.icon())

    def setMinimumSizeHintMode(self, mode: EnumMinimumSizeHintMode):
        self._mgr.minimumSizeHintMode = mode

    def isCentralWidget(self):
        return self.dockManager().centerWidget() is self

    def setToolbarFloatingStyle(self, floating: bool):
        '''
        Adjusts the toolbar icon sizes according to the floating state

        Parameters
        ----------
        floating : bool
        '''
        if not self._mgr.toolBar:
            return

        _icon_size = (self._mgr.toolBarIconSizeFloating
                      if floating
                      else self._mgr.toolBarIconSizeDocked
                      )
        if _icon_size != self._mgr.toolBar.iconSize():
            self._mgr.toolBar.setIconSize(_icon_size)

        _button_style = (self._mgr.toolBarIconSizeFloating
                         if floating
                         else self._mgr.toolBarIconSizeDocked
                         )
        if _button_style != self._mgr.toolBar.toolButtonStyle():
            self._mgr.toolBar.setToolButtonStyle(_button_style)

    def setDockArea(self, dock_area_widget: ['CDockAreaWidget', None]):
        '''
        If this dock widget is inserted into a dock area, the dock area will be
        registered on this widget via this function. If a dock widget is
        removed from a dock area, this function will be called with nullptr
        value.

        Parameters
        ----------
        dock_area : DockAreaWidget
        '''
        self._mgr.dockArea = dock_area_widget
        self._mgr.toggleViewAction.setChecked(dock_area_widget is not None and not self.isClosed())
        self.setParent(dock_area_widget)

    def saveState(self, stream: QtCore.QXmlStreamWriter):
        '''
        Saves the state into the given stream

        Parameters
        ----------
        stream : QXmlStreamWriter
        '''
        stream.writeStartElement("Widget")
        stream.writeAttribute("Name", self.objectName())
        stream.writeAttribute("Closed", '1' if self._mgr.closed else '0')
        stream.writeEndElement()

    def flagAsUnassigned(self):
        '''
        This is a helper function for the dock manager to flag this widget as
        unassigned. When calling the restore function, it may happen, that the
        saved state contains less dock widgets then currently available. All
        widgets whose data is not contained in the saved state, are flagged as
        unassigned after the restore process. If the user shows an unassigned
        dock widget, a floating widget will be created to take up the dock
        widget.
        '''
        self._mgr.closed = True
        logger.debug('flag_as_unassigned %s -> setParent %s', self,
                     self._mgr.dockManager)
        self.setParent(self._mgr.dockManager)
        self.setVisible(False)
        self.setDockArea(None)

        _tab_widget = self.tabWidget()
        logger.debug('flag_as_unassigned %s -> setParent %s', _tab_widget,
                     self)
        _tab_widget.setParent(self)

    def emitTopLevelEventForWidget(self, top_level_dock_widget: 'CDockWidget', floating: bool):
        if top_level_dock_widget:
            top_level_dock_widget.dockAreaWidget().updateTitleBarVisibility()
            top_level_dock_widget.emitTopLevelChanged(floating)

    def emitTopLevelChanged(self, floating: bool):
        '''
        Use this function to emit a top level changed event. Do never use emit
        top_level_changed(). Always use this function because it only emits a
        signal if the floating state has really changed

        Parameters
        ----------
        floating : bool
        '''
        if floating != self._mgr.isFloatingTopLevel:
            self._mgr.isFloatingTopLevel = floating
            self.sigTopLevelChanged.emit(self._mgr.isFloatingTopLevel)

    def setClosedState(self, closed: bool):
        '''
        Internal function for modifying the closed state when restoring a saved
        docking state

        Parameters
        ----------
        closed : bool
        '''
        self._mgr.closed = closed

    def toggleViewInternal(self, open_: bool):
        '''
        Internal toggle view function that does not check if the widget already
        is in the given state

        Parameters
        ----------
        open_ : bool
        '''
        _dock_container = self.dockContainer()
        _top_level_dock_widget_before = (_dock_container.topLevelDockWidget()
                                         if _dock_container else None)
        self._mgr.closed = not open_
        if open_:
            self._mgr.showDockWidget()
        else:
            self._mgr.hideDockWidget()

        self._mgr.toggleViewAction.blockSignals(True)
        self._mgr.toggleViewAction.setChecked(open_)
        self._mgr.toggleViewAction.blockSignals(False)
        if self._mgr.dockArea:
            self._mgr.dockArea.toggleDockWidgetView(self, open_)
        if self._mgr.dockArea.isAutoHide():
            self._mgr.dockArea.autoHideDockContainer().toggleView(open_)
        if open_ and _top_level_dock_widget_before:
            emitTopLevelEventForWidget(_top_level_dock_widget_before, False)

        # Here we need to call the dockContainer() function again, because if
        # this dock widget was unassigned before the call to showDockWidget() then
        # it has a dock container now
        _dock_container = self.dockContainer()
        _top_level_dock_widget_after = (_dock_container.topLevelDockWidget()
                                        if _dock_container
                                        else None)
        emitTopLevelEventForWidget(_top_level_dock_widget_after, True)
        if _dock_container is not None:
            _floating_container = _dock_container.floatingWidget()
            if _floating_container is not None:
                _floating_container.updateWindowTitle()

        if not open_:
            self.sigClosed.emit()

        self.sigViewToggled.emit(open_)

    def minimumSizeHint(self) -> QtCore.QSize:
        '''
        We return a fixed minimum size hint for all dock widgets

        Returns
        -------
        value : QSize
        '''

        if self._mgr.minimumSizeHintMode == EnumMinimumSizeHintMode.FROM_DOCK_WIDGET or self._mgr.widget is None:
            return QtCore.QSize(60, 40)
        return self._mgr.widget.minimumSizeHint()

    def setFloating(self):
        if self.isClosed():
            return
        self._mgr.tabWidget.detachDockWidget()

    def deleteDockWidget(self):
        _mgr = self.dockManager()
        if _mgr:
            _mgr.removeDockWidget(self)
        self.deleteLater()
        self._mgr.closed = True

    def closeDockWidget(self):
        self.closeDockWidgetInternal(True)

    def closeDockWidgetInternal(self, force=False):
        if not force:
            self.sigCloseRequested.emit()

        if not force and EnumDockWidgetFeature.CUSTOM_CLOSE_HANDLING in self.features():
            return False
        if EnumDockWidgetFeature.DELETE_ON_CLOSE in self.features():
            # If the dock widget is floating, then we check if we also need to
            # delete the floating widget
            if self.isFloating():
                _fw = findParent(CFloatingDockContainer, self)
                if _fw is not None:
                    if len(_fw.dockWidgets()) == 1:
                        _fw.deleteLater()
                    else:
                        _fw.hide()
            if self._mgr.dockArea and self._mgr.dockArea.isAutoHide():
                self._mgr.dockArea.autoHideDockContainer().cleanupAndDelete()
            self.deleteDockWidget()
            self.sigClosed.emit()
        else:
            self.toggleView(False)
        return True

    def widget(self) -> 'CDockWidget':
        '''
        Returns the widget for the dock widget. This function returns None if
        the widget has not been set.

        Returns
        -------
        value : QWidget
        '''
        return self._mgr.widget

    def tabWidget(self) -> 'CDockWidgetTab':
        '''
        Returns the title bar widget of this dock widget

        Returns
        -------
        value : DockWidgetTab
        '''
        return self._mgr.tabWidget

    # def set_features(self, features: DockWidgetFeature):
    #     '''
    #     Sets, whether the dock widget is movable, closable, and floatable.
    #
    #     Parameters
    #     ----------
    #     features : DockWidgetFeature
    #     '''
    #     self._mgr.features = features
    #
    # def set_feature(self, flag: DockWidgetFeature, on: bool = True):
    #     '''
    #     Sets the feature flag for this dock widget if on is true; otherwise
    #     clears the flag.
    #
    #     Parameters
    #     ----------
    #     flag : DockWidgetFeature
    #     on : bool
    #     '''
    #     if on:
    #         self._mgr.features |= flag
    #     else:
    #         self._mgr.features &= ~flag

    # def features(self) -> EnumDockWidgetFeature:
    #     '''
    #     This property holds whether the dock widget is movable, closable, and
    #     floatable. By default, this property is set to a combination of
    #     DockWidgetClosable, DockWidgetMovable and DockWidgetFloatable.
    #
    #     Returns
    #     -------
    #     value : DockWidgetFeature
    #     '''
    #     return self._mgr.features

    # def dock_manager(self) -> 'DockManager':
    #     '''
    #     Returns the dock manager that manages the dock widget or 0 if the
    #     widget has not been assigned to any dock manager yet
    #
    #     Returns
    #     -------
    #     value : DockManager
    #     '''
    #     return self._mgr.dock_manager
    #
    # def dock_container(self) -> Optional['DockContainerWidget']:
    #     '''
    #     Returns the dock container widget this dock area widget belongs to or
    #     None if this dock widget has not been docked yet
    #
    #     Returns
    #     -------
    #     value : DockContainerWidget
    #     '''
    #     return self._mgr.dock_area.dock_container() if self._mgr.dock_area else None
    #
    # def dock_area_widget(self) -> 'DockAreaWidget':
    #     '''
    #     Returns the dock area widget this dock widget belongs to or 0 if this
    #     dock widget has not been docked yet
    #
    #     Returns
    #     -------
    #     value : DockAreaWidget
    #     '''
    #     return self._mgr.dock_area
    #
    # def is_floating(self) -> bool:
    #     '''
    #     This property holds whether the dock widget is floating. A dock widget
    #     is only floating, if it is the one and only widget inside of a floating
    #     container. If there are more than one dock widget in a floating
    #     container, the all dock widgets are docked and not floating.
    #
    #     Returns
    #     -------
    #     value : bool
    #     '''
    #     if not self.is_in_floating_container():
    #         return False
    #
    #     return self.dock_container().top_level_dock_widget() is self
    #
    # def is_in_floating_container(self) -> bool:
    #     '''
    #     This function returns true, if this dock widget is in a floating. The
    #     function returns true, if the dock widget is floating and it also
    #     returns true if it is docked inside of a floating container.
    #
    #     Returns
    #     -------
    #     value : bool
    #     '''
    #     container = self.dock_container()
    #     return container and container.is_floating()
    #
    # def is_closed(self) -> bool:
    #     '''
    #     Returns true, if this dock widget is closed.
    #
    #     Returns
    #     -------
    #     value : bool
    #     '''
    #     return self._mgr.closed
    #
    # def toggle_view_action(self) -> QAction:
    #     '''
    #     Returns a checkable action that can be used to show or close this dock
    #     widget. The action's text is set to the dock widget's window title.
    #
    #     Returns
    #     -------
    #     value : QAction
    #     '''
    #     return self._mgr.toggle_view_action
    #
    # def set_toggle_view_action_mode(self, mode: ToggleViewActionMode):
    #     '''
    #     Configures the behavior of the toggle view action.
    #
    #     Parameters
    #     ----------
    #     mode : ToggleViewActionMode
    #     '''
    #     is_action_mode = ToggleViewActionMode.toggle == mode
    #     self._mgr.toggle_view_action.setCheckable(is_action_mode)
    #     icon = QIcon() if is_action_mode else self._mgr.tab_widget.icon()
    #     if icon is not None:
    #         self._mgr.toggle_view_action.setIcon(icon)

    def setIcon(self, icon: QtGui.QIcon):
        '''
        Sets the dock widget icon that is shown in tabs and in toggle view actions

        Parameters
        ----------
        icon : QIcon
        '''
        self._mgr.tabWidget.setIcon(icon)
        if self._mgr.sideTabWidget:
            self._mgr.sideTabWidget.setIcon(icon)
        if not self._mgr.toggleViewAction.isCheckable():
            self._mgr.toggleViewAction.setIcon(icon)

    def icon(self) -> QtGui.QIcon:
        '''
        Returns the icon that has been assigned to the dock widget

        Returns
        -------
        value : QIcon
        '''
        return self._mgr.tabWidget.icon()

    def toolBar(self) -> QtWidgets.QToolBar:
        '''
        If the WithToolBar layout flag is enabled, then this function returns
        the dock widget toolbar. If the flag is disabled, the function returns
        a nullptr. This function returns the dock widget top tool bar. If no
        toolbar is assigned, this function returns nullptr. To get a vaild
        toolbar you either need to create a default empty toolbar via
        createDefaultToolBar() function or you need to assign you custom
        toolbar via setToolBar().

        Returns
        -------
        value : QToolBar
        '''
        return self._mgr.toolBar

    def createDefaultToolBar(self) -> QtWidgets.QToolBar:
        '''
        If you would like to use the default top tool bar, then call this
        function to create the default tool bar. After this function the
        toolBar() function will return a valid toolBar() object.

        Returns
        -------
        value : QToolBar
        '''
        if not self._mgr.toolBar:
            self._mgr.setupToolBar()

        return self._mgr.toolBar

    def setToolBar(self, tool_bar: QtWidgets.QToolBar):
        '''
        Assign a new tool bar that is shown above the content widget. The dock
        widget will become the owner of the tool bar and deletes it on
        destruction

        Parameters
        ----------
        tool_bar : QToolBar
        '''
        if self._mgr.toolBar:
            self._mgr.toolBar.deleteLater()
            self._mgr.toolBar = None

        self._mgr.toolBar = tool_bar
        self._mgr.layout.insertWidget(0, self._mgr.toolBar)
        self.sigTopLevelChanged.connect(self.setToolbarFloatingStyle)
        self.setToolbarFloatingStyle(self.isFloating())

    def setToolBarStyle(self, style: QtCore.Qt.ToolButtonStyle, state: EnumWidgetState):
        '''
        This function sets the tool button style for the given dock widget
        state. It is possible to switch the tool button style depending on the
        state. If a dock widget is floating, then here are more space and it is
        possible to select a style that requires more space like
        Qt.ToolButtonTextUnderIcon. For the docked state
        Qt.ToolButtonIconOnly might be better.

        Parameters
        ----------
        style : Qt.ToolButtonStyle
        state : WidgetState
        '''
        if EnumWidgetState.FLOATING == state:
            self._mgr.toolBarStyleFloating = style
        else:
            self._mgr.toolBarStyleDocked = style

        self.setToolbarFloatingStyle(self.isFloating())

    def toolBarStyle(self, state: EnumWidgetState) -> QtCore.Qt.ToolButtonStyle:
        '''
        Returns the tool button style for the given docking state.

        Parameters
        ----------
        state : WidgetState

        Returns
        -------
        value : Qt.ToolButtonStyle
        '''
        return (self._mgr.toolBarStyleFloating
                if EnumWidgetState.FLOATING == state
                else self._mgr.toolBarStyleDocked
                )

    def setToolBarIconSize(self, icon_size: QtCore.QSize, state: EnumWidgetState):
        '''
        This function sets the tool button icon size for the given state. If a
        dock widget is floating, there is more space an increasing the icon
        size is possible. For docked widgets, small icon sizes, eg. 16 x 16
        might be better.

        Parameters
        ----------
        icon_size : QSize
        state : WidgetState
        '''
        if EnumWidgetState.FLOATING == state:
            self._mgr.toolBarIconSizeFloating = icon_size
        else:
            self._mgr.toolBarIconSizeDocked = icon_size

        self.setToolbarFloatingStyle(self.isFloating())

    def toolBarIconSize(self, state: EnumWidgetState) -> QtCore.QSize:
        '''
        Returns the icon size for a given docking state.

        Parameters
        ----------
        state : WidgetState

        Returns
        -------
        value : QSize
        '''
        return (self._mgr.toolBarIconSizeFloating
                if EnumWidgetState.FLOATING == state
                else self._mgr.toolBarIconSizeDocked)

    def setTabToolTip(self, text: str):
        '''
        This is function sets text tooltip for title bar widget and tooltip for toggle view action

        Parameters
        ----------
        text : str
        '''
        if self._mgr.tabWidget:
            self._mgr.tabWidget.setToolTip(text)

        if self._mgr.toggleViewAction:
            self._mgr.toggleViewAction.setToolTip(text)

        if self._mgr.dockArea:
            # update tabs menu
            self._mgr.dockArea.markTitleBarMenuOutdated()

    def event(self, e: QtCore.QEvent) -> bool:
        '''
        Emits titleChanged signal if title change event occurs

        Parameters
        ----------
        e : QEvent

        Returns
        -------
        value : bool
        '''
        if e.type() == QtCore.QEvent.Type.Hide:
            self.sigVisibilityChanged.emit(False)
        elif e.type() == QtCore.QEvent.Type.Show:
            self.sigVisibilityChanged.emit(self.geometry().right() >= 0 and self.geometry().bottom() >= 0)
        elif e.type() == QtCore.QEvent.Type.WindowTitleChange:
            _title = self.windowTitle()
            if self._mgr.tabWidget:
                self._mgr.tabWidget.setText(_title)
            if self._mgr.sideTabWidget:
                self._mgr.sideTabWidget.setText(_title)
            if self._mgr.toggleViewAction:
                self._mgr.toggleViewAction.setText(_title)
            if self._mgr.dockArea:
                # update tabs menu
                self._mgr.dockArea.markTitleBarMenuOutdated()
            _fw = self.floatingDockContainer()
            if _fw:
                _fw.updateWindowTitle()
            self.sigTitleChanged.emit(_title)

        return super().event(e)

    def toggleView(self, open_: bool):
        '''
        This property controls whether the dock widget is open or closed. The
        toogleViewAction triggers this slot

        Parameters
        ----------
        open_ : bool
        '''
        # If the toggle view action mode is ActionModeShow, then Open is always
        # true if the sender is the toggle view action
        _sender = self.sender()
        if _sender is self._mgr.toggleViewAction and not self._mgr.toggleViewAction.isCheckable():
            open_ = True

        # If the dock widget state is different, then we really need to toggle
        # the state. If we are in the right state, then we simply make this
        # dock widget the current dock widget
        if self._mgr.closed != (not open_):
            self.toggleViewInternal(open_)
        elif open_ and self._mgr.dockArea:
            self.raise_()

    def setTitleBarActions(self, actions: typing.List[QtGui.QAction]):
        self._mgr.titleBarActions = actions

    def titleBarActions(self):
        return self._mgr.titleBarActions

    def showFullScreen(self):
        if self.isFloating():
            self.dockContainer().floatingWidget().showFullScreen()
        else:
            super().showFullScreen()

    def showNormal(self) -> None:
        if self.isFloating():
            self.dockContainer().floatingWidget().showNormal()
        else:
            super().showNormal()

    def isFullScreen(self) -> bool:
        if self.isFloating():
            return self.dockContainer().floatingWidget().isFullScreen()
        else:
            return super().isFullScreen()

    def setAsCurrentTab(self):
        if self._mgr.dockArea and not self.isClosed():
            self._mgr.dockArea.setCurrentDockWidget(self)

    def isTabbed(self):
        return self._mgr.dockArea and len(self._mgr.dockArea.openDockWidgetsCount()) > 1

    def isCurrentTab(self):
        return self._mgr.dockArea and self._mgr.dockArea.currentDockWidget() is self

    def raise_(self) -> None:
        if self.isClosed():
            return
        self.setAsCurrentTab()
        if self.isInFloatingContainer():
            _fw = self.window()
            _fw.raise_()
            _fw.activateWindow()

    def setAutoHide(self, enable, location: EnumSideBarLocation = EnumSideBarLocation.RIGHT):
        if EnumAutoHideFlag.AutoHideFeatureEnabled not in AUTO_HIDE_DEFAULT_CONFIG:
            return
        if self.isAutoHide() == enable:
            return
        _da = self.dockAreaWidget()
        if not enable:
            _da.setAutoHide(False)
        else:
            _area = _da.calculateSideTabBarArea() if location == EnumSideBarLocation.NONE else location
            self.dockContainer().createAndSetupAutoHideContainer(_area, self)

    def toggleAutoHide(self, location: EnumSideBarLocation = EnumSideBarLocation.RIGHT):
        if EnumAutoHideFlag.AutoHideFeatureEnabled not in AUTO_HIDE_DEFAULT_CONFIG:
            return
        self.setAutoHide(not self.isAutoHide(), location)
