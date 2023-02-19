from typing import TYPE_CHECKING
import logging
from core.gui.qtimp import QtCore, QtGui, QtWidgets

from .define import (EnumDockWidgetFeature, EnumDragState, EnumDockWidgetArea,
                     DOCK_MANAGER_DEFAULT_CONFIG, EnumDockMgrConfigFlag)
from .floating_base import IFloatingWidget
from .util import (LINUX, WINDOWS, eventFilterDecorator, getQApp, evtFloatingWidgetDragStartEvent)
from .dock_container_widget import CDockContainerWidget
from .dock_state_reader import CDockStateReader

if LINUX:
    from .linux.floating_widget_title_bar import CFloatingWidgetTitleBar

if TYPE_CHECKING:
    from .dock_manager import CDockManager
    from .dock_area_widget import CDockAreaWidget
    from .dock_widget import CDockWidget

logger = logging.getLogger(__name__)


class FloatingDockContainerMgr:
    _this: 'CFloatingDockContainer'
    dockContainer: CDockContainerWidget
    zOrderIndex: int
    dockManager: 'CDockManager'
    draggingState: EnumDragState
    dragStartMousePosition: QtCore.QPoint
    dropContainer: CDockContainerWidget
    singleDockArea: 'CDockAreaWidget'
    dragStartPos: QtCore.QPoint
    hiding: bool
    autoHideChildren: bool
    if LINUX:
        mouseEventHandler: QtWidgets.QWidget
        titleBar: CFloatingWidgetTitleBar
        isResizing: bool

    def __init__(self, _this):
        '''
        Private data constructor

        Parameters
        ----------
        _this : FloatingDockContainer
        '''
        self._this = _this
        self.dockContainer = None
        CFloatingDockContainer.Z_ORDER_COUNTER += 1
        self.zOrderIndex = CFloatingDockContainer.Z_ORDER_COUNTER

        self.dockManager = None
        self.draggingState = EnumDragState.INACTIVE
        self.dragStartMousePosition = QtCore.QPoint()
        self.dropContainer = None
        self.singleDockArea = None
        self.dragStartPos = None
        self.hiding = False
        self.autoHideChildren = True

        if LINUX:
            self.mouseEventHandler = None
            self.titleBar = None
            self.isResizing = False

    def isState(self, state_id):
        return state_id == self.draggingState

    def setState(self, state: EnumDragState):
        if state == self.draggingState:
            return
        self.draggingState = state
        getQApp().postEvent(self._this, QtCore.QEvent(QtCore.QEvent.Type(evtFloatingWidgetDragStartEvent)))

    def reflectCurrentWidget(self, current_widget: 'CDockWidget'):
        # Reflect the current dock widget title in the floating widget windowTitle()
        # depending on the CDockManager::FloatingContainerHasWidgetTitle flag
        if EnumDockMgrConfigFlag.FloatingContainerHasWidgetTitle in DOCK_MANAGER_DEFAULT_CONFIG:
            self.setWindowTitle(current_widget.windowTitle())
        else:
            self.setWindowTitle(self.floatingContainersTitle())
        # reflect CurrentWidget's icon if configured to do so, otherwise display application icon as window icon
        _current_widget_icon = current_widget.icon()
        if EnumDockMgrConfigFlag.FloatingContainerHasWidgetIcon in DOCK_MANAGER_DEFAULT_CONFIG and not _current_widget_icon.isNull():
            self._this.setWindowIcon(_current_widget_icon)
        else:
            self._this.setWindowIcon(QtWidgets.QApplication.windowIcon())

    def handleEscapeKey(self):
        self.setState(EnumDragState.INACTIVE)
        self.dockManager.containerOverlay().hideOverlay()
        self.dockManager.dockAreaOverlay().hideOverlay()

    def floatingContainersTitle(self):
        return self.dockManager.floatingContainersTitle()

    def titleMouseReleaseEvent(self):
        self.setState(EnumDragState.INACTIVE)
        if self.dropContainer is None:
            logger.debug('title_mouse_release_event: no drop container?')
            return

        _dock_manager = self.dockManager
        _dock_area_overlay = _dock_manager.dockAreaOverlay()
        _container_overlay = _dock_manager.containerOverlay()
        _da_under_da = _dock_area_overlay.dropAreaUnderCursor()
        _da_under_c = _container_overlay.dropAreaUnderCursor()

        if _da_under_da != EnumDockWidgetArea.INVALID or _da_under_c != EnumDockWidgetArea.INVALID:
            # Resize the floating widget to the size of the highlighted drop area
            # rectangle
            _overlay = _container_overlay
            if not _overlay.dropOverlayRect().isValid():
                _overlay = _dock_area_overlay

            _rect = _overlay.dropOverlayRect()
            if not _rect.isValid():
                logger.debug('title_mouse_release_event: invalid rect '
                             'x %s y %s w %s h %s',
                             _rect.x(), _rect.y(),
                             _rect.width(), _rect.height())
            else:
                _frame_width = (self._this.frameSize().width() -
                                self._this.rect().width()) // 2
                _title_bar_height = int(self._this.frameSize().height() -
                                        self._this.rect().height() - _frame_width)

                _top_left = _overlay.mapToGlobal(_rect.topLeft())
                _top_left.setY(_top_left.y() + _title_bar_height)
                _geom = QtCore.QRect(_top_left,
                                     QtCore.QSize(_rect.width(), _rect.height() -
                                                  _title_bar_height))
                self._this.setGeometry(_geom)
                QtWidgets.QApplication.processEvents()
            self.dropContainer.dropFloatingWidget(self._this, QtGui.QCursor.pos())

        _container_overlay.hideOverlay()
        _dock_area_overlay.hideOverlay()

    def updateDropOverlays(self, global_pos: QtCore.QPoint):
        '''
        Update drop overlays

        Parameters
        ----------
        global_pos : QPoint
        '''
        if not self._this.isVisible() or not self.dockManager:
            return

        if LINUX:
            if getQApp().activeModalWidget():
                return
        _containers = self.dockManager.dockContainers()
        _top_container = None
        for container_widget in _containers:
            if not container_widget.isVisible():
                continue
            if self.dockContainer is container_widget:
                continue

            _mapped_pos = container_widget.mapFromGlobal(global_pos)
            if container_widget.rect().contains(_mapped_pos):
                if not _top_container or container_widget.isInFrontOf(_top_container):
                    _top_container = container_widget

        self.dropContainer = _top_container
        _container_overlay = self.dockManager.containerOverlay()
        _dock_area_overlay = self.dockManager.dockAreaOverlay()
        if not _top_container:
            logger.debug('update_drop_overlays: No top container')
            _container_overlay.hideOverlay()
            _dock_area_overlay.hideOverlay()
            return

        _visible_dock_areas = _top_container.visibleDockAreaCount()
        _container_overlay.setAllowedAreas(
            EnumDockWidgetArea.OUTER_DOCK_AREAS
            if _visible_dock_areas > 1
            else EnumDockWidgetArea.ALL_DOCK_AREAS
        )

        _container_area = _container_overlay.showOverlay(_top_container)
        _container_overlay.enableDropPreview(_container_area != EnumDockWidgetArea.INVALID)
        _dock_area = _top_container.dockAreaAt(global_pos)

        if _dock_area and _dock_area.isVisible() and _visible_dock_areas > 0:
            _dock_area_overlay.enableDropPreview(True)
            _dock_area_overlay.setAllowedAreas(
                EnumDockWidgetArea.NO_AREA
                if _visible_dock_areas == 1
                else EnumDockWidgetArea.ALL_DOCK_AREAS)
            _area = _dock_area_overlay.showOverlay(_dock_area)
            # A CenterDockWidgetArea for the dockAreaOverlay() indicates that
            # the mouse is in the title bar. If the ContainerArea is valid
            # then we ignore the dock area of the dockAreaOverlay() and disable
            # the drop preview
            if (_area == EnumDockWidgetArea.CENTER and
                    _container_area != EnumDockWidgetArea.INVALID):
                _dock_area_overlay.enableDropPreview(False)
                _container_overlay.enableDropPreview(True)
            else:
                _container_overlay.enableDropPreview(EnumDockWidgetArea.INVALID == _area)
        else:
            _dock_area_overlay.hideOverlay()

    def setWindowTitle(self, text: str):
        if LINUX:
            self.titleBar.setTitle(text)
        else:
            self._this.setWindowTitle(text)


if LINUX:
    FloatingWidgetBase = QtWidgets.QDockWidget
else:
    FloatingWidgetBase = QtWidgets.QWidget


class CFloatingDockContainer(FloatingWidgetBase, IFloatingWidget):
    MOUSE_PRESSED = False
    Z_ORDER_COUNTER = 0

    def __init__(self, *, dock_area: 'CDockAreaWidget' = None,
                 dock_widget: 'CDockWidget' = None,
                 dock_manager: 'CDockManager' = None):
        '''
        Parameters
        ----------
        dock_manager : DockManager

        dock_area : DockAreaWidget
            Create floating widget with the given dock area
        '''
        if dock_manager is None:
            if dock_area is not None:
                dock_manager = dock_area.dockManager()
            elif dock_widget is not None:
                dock_manager = dock_widget.dockManager()

        if dock_manager is None:
            raise ValueError('Must pass in either dock_area, dock_widget, or dock_manager')

        super().__init__(dock_manager)
        self._mgr = FloatingDockContainerMgr(self)
        self._mgr.dockManager = dock_manager
        _dock_container = CDockContainerWidget(dock_manager, self)
        self._mgr.dockContainer = _dock_container
        _dock_container.destroyed.connect(self._destroyed)
        _dock_container.sigDockAreasAdded.connect(self.onDockAreasAddedOrRemoved)
        _dock_container.sigDockAreasRemoved.connect(self.onDockAreasAddedOrRemoved)

        if LINUX:
            self._mgr.titleBar = CFloatingWidgetTitleBar(self)
            self.setWindowFlags(super().windowFlags() | QtCore.Qt.WindowType.Tool)
            self.setWidget(self._mgr.dockContainer)
            self.setFloating(True)
            self.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
            self.setTitleBarWidget(self._mgr.titleBar)
            self._mgr.titleBar.sigCloseRequested.connect(self.close)
        else:
            self.setWindowFlags(QtCore.Qt.WindowType.Window
                                | QtCore.Qt.WindowType.WindowMaximizeButtonHint
                                | QtCore.Qt.WindowType.WindowCloseButtonHint)
            _layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
            _layout.setContentsMargins(0, 0, 0, 0)
            _layout.setSpacing(0)
            self.setLayout(_layout)
            _layout.addWidget(_dock_container)

        dock_manager.registerFloatingWidget(self)

        # We install an event filter to detect mouse release events because we
        # do not receive mouse release event if the floating widget is behind
        # the drop overlay cross
        getQApp().installEventFilter(self)
        if dock_area is not None:
            _dock_container.addDockArea(dock_area)
            _top_dw = self.topLevelDockWidget()
            if _top_dw:
                _top_dw.emitTopLevelChanged(True)
            self._mgr.dockManager.notifyWidgetOrAreaRelocation(dock_area)
        elif dock_widget is not None:
            _dock_container.addDockWidget(
                EnumDockWidgetArea.CENTER, dock_widget)
            _top_dw = self.topLevelDockWidget()
            if _top_dw:
                _top_dw.emitTopLevelChanged(True)
            self._mgr.dockManager.notifyWidgetOrAreaRelocation(dock_area)
        if (dock_area or dock_widget) and LINUX:
            self._mgr.titleBar.enableCloseButton(self.isClosable())

    def __repr__(self):
        return f'<FloatingDockContainer container={self._mgr.dockContainer}>'

    def _destroyed(self):
        _dock_container = self._mgr.dockContainer
        self._mgr.dockContainer = None
        if _dock_container is not None:
            self._mgr.dockManager.removeDockContainer(_dock_container)
            self._mgr.dockManager.removeFloatingWidget(self)

        getQApp().removeEventFilter(self)

    def deleteLater(self):
        self._destroyed()
        super().deleteLater()

    def isClosable(self):
        return EnumDockWidgetFeature.CLOSEABLE in self._mgr.dockContainer.features()

    def hasTopLevelDockWidget(self):
        return self._mgr.dockContainer.hasTopLevelDockWidget()

    def topLevelDockWidget(self):
        return self._mgr.dockContainer.topLevelDockWidget()

    def onDockAreasAddedOrRemoved(self):
        logger.debug('FloatingDockContainer.onDockAreasAddedOrRemoved()')
        _top_level_dock_area = self._mgr.dockContainer.topLevelDockArea()
        if _top_level_dock_area is not None:
            self._mgr.singleDockArea = _top_level_dock_area
            _current_widget = self._mgr.singleDockArea.currentDockWidget()
            self._mgr.reflectCurrentWidget(_current_widget)
            self._mgr.singleDockArea.sigCurrentChanged.connect(self.onDockAreaCurrentChanged)
        else:
            if self._mgr.singleDockArea:
                self._mgr.singleDockArea.sigCurrentChanged.disconnect(self.onDockAreaCurrentChanged)
                self._mgr.singleDockArea = None

            self._mgr.setWindowTitle(self._mgr.floatingContainersTitle())
            self.setWindowIcon(QtWidgets.QApplication.windowIcon())

    def onDockAreaCurrentChanged(self, index: int):
        '''
        On dock area current changed

        Parameters
        ----------
        index : int
            Unused
        '''
        # pylint: disable=unused-argument
        _widget = self._mgr.singleDockArea.currentDockWidget()
        if _widget:
            self._mgr.reflectCurrentWidget(_widget)

    def finishDragging(self):
        '''
        Call this function if you explecitely want to signal that dragging has
        finished
        '''
        logger.debug('FloatingDockContainer.finishDragging')
        if LINUX:
            self.setWindowOpacity(1)
            self.activateWindow()
            if self._mgr.mouseEventHandler is not None:
                logger.debug('Mouse event handler releaseMouse')
                self._mgr.mouseEventHandler.releaseMouse()
                self._mgr.mouseEventHandler = None
        self._mgr.titleMouseReleaseEvent()

    def moveFloating(self):
        '''
        Moves the widget to a new position relative to the position given when
        startFloating() was called
        '''
        logger.debug('FloatingDockContainer.moveFloating')
        _border_size = (self.frameSize().width() - self.size().width()) / 2
        _move_to_pos = QtGui.QCursor.pos() - self._mgr.dragStartMousePosition - QtCore.QPoint(_border_size, 0)
        self.move(_move_to_pos)
        if self._mgr.draggingState == EnumDragState.MOUSE_PRESSED:
            self._mgr.setState(EnumDragState.FLOATING_WIDGET)
            self._mgr.updateDropOverlays(QtGui.QCursor.pos())
        elif self._mgr.draggingState == EnumDragState.FLOATING_WIDGET:
            self._mgr.updateDropOverlays(QtGui.QCursor.pos())
        # todo: mac os: QApplication::setActiveWindow(this);

    def restoreState(self, stream: CDockStateReader, testing: bool) -> bool:
        '''
        Restores the state from given stream. If Testing is true, the function
        only parses the data from the given stream but does not restore
        anything. You can use this check for faulty files before you start
        restoring the state

        Parameters
        ----------
        stream : QXmlStreamReader
        testing : bool

        Returns
        -------
        value : bool
        '''
        if not self._mgr.dockContainer.restoreState(stream, testing):
            return False

        self.onDockAreasAddedOrRemoved()
        if LINUX:
            if self._mgr.titleBar:
                self._mgr.titleBar.setMaximizedIcon(self.windowState() == QtCore.Qt.WindowState.WindowMaximized)
        return True

    def resizeEvent(self, event: QtGui.QResizeEvent):
        self._mgr.isResizing = True
        super().resizeEvent(event)

    def moveEvent(self, event: QtGui.QMoveEvent):
        super().moveEvent(event)
        if self._mgr.draggingState == EnumDragState.MOUSE_PRESSED:
            self._mgr.setState(EnumDragState.FLOATING_WIDGET)
            self._mgr.updateDropOverlays(QtGui.QCursor.pos())
        elif self._mgr.draggingState == EnumDragState.FLOATING_WIDGET:
            self._mgr.updateDropOverlays(QtGui.QCursor.pos())
            QtWidgets.QApplication.setActiveWindow(self)

    def updateWindowTitle(self):
        '''
        Call this function to update the window title
        '''
        # If this floating container will be hidden, then updating the window
        # tile is not required anymore
        if self._mgr.hiding:
            return
        _top_level_dock_area = self._mgr.dockContainer.topLevelDockArea()
        if _top_level_dock_area is not None:
            _current_widget = _top_level_dock_area.currentDockWidget()
            if _current_widget is not None:
                self._mgr.reflectCurrentWidget(_current_widget)
        else:
            self._mgr.setWindowTitle(self._mgr.floatingContainersTitle())
            self.setWindowIcon(QtWidgets.QApplication.windowIcon())

    def changeEvent(self, event: QtCore.QEvent):
        '''
        Changeevent

        Parameters
        ----------
        event : QEvent
        '''
        super().changeEvent(event)
        if (event.type() == QtCore.QEvent.Type.ActivationChange) and self.isActiveWindow():
            logger.debug('FloatingWidget.changeEvent QEvent.ActivationChange ')
            self.Z_ORDER_COUNTER += 1
            self._mgr.zOrderIndex = self.Z_ORDER_COUNTER

    def event(self, event: QtCore.QEvent) -> bool:
        '''
        Event

        Parameters
        ----------
        event : QEvent

        Returns
        -------
        value : bool
        '''
        _state = self._mgr.draggingState
        if _state == EnumDragState.INACTIVE:
            if event.type() == QtCore.QEvent.Type.NonClientAreaMouseButtonPress:
                logger.debug('CFloatingWidget::event Event::NonClientAreaMouseButtonPress')
                self._mgr.dragStartPos = self.pos()
                self._mgr.setState(EnumDragState.MOUSE_PRESSED)
        elif _state == EnumDragState.MOUSE_PRESSED:
            if event.type() == QtCore.QEvent.Type.NonClientAreaMouseButtonDblClick:
                logger.debug("FloatingWidget::event QEvent::NonClientAreaMouseButtonDblClick")
                self._mgr.setState(EnumDragState.INACTIVE)
            elif event.type() == QtCore.QEvent.Type.Resize:
                # If the first event after the mouse press is a resize event, then
                # the user resizes the window instead of dragging it around.
                # But there is one exception. If the window is maximized,
                # then dragging the window via title bar will cause the widget to
                # leave the maximized state. This in turn will trigger a resize event.
                # To know, if the resize event was triggered by user via moving a
                # corner of the window frame or if it was caused by a windows state
                # change, we check, if we are not in maximized state.
                if not self.isMaximized():
                    self._mgr.setState(EnumDragState.INACTIVE)
        elif _state == EnumDragState.FLOATING_WIDGET:
            if event.type() == QtCore.QEvent.Type.NonClientAreaMouseButtonRelease:
                logger.debug("FloatingWidget::event QEvent::NonClientAreaMouseButtonRelease")
                self._mgr.titleMouseReleaseEvent()

        # if event.type() == QtCore.QEvent.Type.WindowActivate:
        #     self.MOUSE_PRESSED = False
        # elif event.type() == QtCore.QEvent.Type.WindowDeactivate:
        #     self.MOUSE_PRESSED = True
        return super().event(event)

    def closeEvent(self, event: QtGui.QCloseEvent):
        '''
        Closeevent

        Parameters
        ----------
        event : QCloseEvent
        '''
        logger.debug('FloatingDockContainer closeEvent')
        self._mgr.setState(EnumDragState.INACTIVE)
        if not self.isClosable():
            event.ignore()
            return
        _has_open_dock_widgets = False
        for x in self._mgr.dockContainer.openedDockWidgets():
            if EnumDockWidgetFeature.DELETE_ON_CLOSE in x.features() or EnumDockWidgetFeature.CUSTOM_CLOSE_HANDLING in x.features():
                _closed = x.closeDockWidgetInternal()
                if not _closed:
                    _has_open_dock_widgets = True
            else:
                x.toggleView(False)
        if _has_open_dock_widgets:
            return
        # In Qt version after 5.9.2 there seems to be a bug that causes the
        # QWidget.event() function to not receive any NonClientArea mouse
        # events anymore after a close/show cycle. The bug is reported here:
        # https://bugreports.qt.io/browse/QTBUG-73295
        # The following code is a workaround for Qt versions > 5.9.2 that seems
        # to work
        # Starting from Qt version 5.12.2 this seems to work again. But
        # now the QEvent.NonClientAreaMouseButtonPress function returns always
        # Qt.RightButton even if the left button was pressed
        self.hide()

    def hideEvent(self, event: QtGui.QHideEvent):
        '''
        Hideevent

        Parameters
        ----------
        event : QHideEvent
        '''
        super().hideEvent(event)
        if event.spontaneous():
            return
        if self._mgr.dockManager.isRestoringState():
            # Prevent toogleView() events during restore state
            return
        if self._mgr.autoHideChildren:
            self._mgr.hiding = True
            for dock_area in self._mgr.dockContainer.openedDockAreas():
                for dock_widget in dock_area.openedDockWidgets():
                    dock_widget.toggleView(False)
            self._mgr.hiding = False

    def hideAndDeleteLater(self):
        # Widget has been redocked, so it must be hidden right way (see
        # but AutoHideChildren must be set to false because "this" still contains
        # dock widgets that shall not be toggled hidden.
        self._mgr.autoHideChildren = False
        self.hide()
        self.deleteLater()

    def show(self):
        # Prevent this window from showing in the taskbar and pager (alt+tab)
        # xcb_add_prop(True, self.winId(), "_NET_WM_STATE", "_NET_WM_STATE_SKIP_TASKBAR")
        # xcb_add_prop(True, self.winId(), "_NET_WM_STATE", "_NET_WM_STATE_SKIP_PAGER")
        super().show()

    def showEvent(self, event: QtGui.QShowEvent):
        super().showEvent(event)
        if LINUX:
            if EnumDockMgrConfigFlag.FocusHighlighting in DOCK_MANAGER_DEFAULT_CONFIG:
                self.window().activateWindow()

    def showNormal(self, fix_geometry=False):
        if self.windowState() == QtCore.Qt.WindowState.WindowMaximized:
            _old_normal = self.normalGeometry()
            super().showNormal()
            if fix_geometry:
                self.setGeometry(_old_normal)
        if self._mgr.titleBar:
            self._mgr.titleBar.setMaximizedIcon(False)

    def showMaximized(self):
        super().showMaximized()
        if self._mgr.titleBar:
            self._mgr.titleBar.setMaximizedIcon(True)

    def isMaximized(self):
        return self.windowState() == QtCore.Qt.WindowState.WindowMaximized

    def startFloating(self, drag_start_mouse_pos: QtCore.QPoint,
                      size: QtCore.QSize,
                      drag_state: EnumDragState, widget: QtWidgets.QWidget):
        if LINUX:
            if not self.isMaximized():
                self.resize(size)
                self._mgr.dragStartMousePosition = drag_start_mouse_pos
            self._mgr.setState(drag_state)
            if EnumDragState.FLOATING_WIDGET == drag_state:
                self._mgr.mouseEventHandler = widget
                if widget is not None:
                    self._mgr.mouseEventHandler.grabMouse()
            if not self.isMaximized():
                self.moveFloating()
            self.show()
        else:
            self.resize(size)
            self._mgr.dragStartMousePosition = drag_start_mouse_pos
            self._mgr.setState(drag_state)
            self.moveFloating()
            self.show()

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        '''
        Eventfilter

        Parameters
        ----------
        watched : QObject
            Unused
        event : QEvent

        Returns
        -------
        value : bool
        '''
        # pylint: disable=unused-argument
        if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            logger.debug('MouseButtonRelease')
            if self._mgr.draggingState == EnumDragState.FLOATING_WIDGET:
                getQApp().removeEventFilter(self)
                logger.debug('FloatingWidget.eventFilter QEvent.MouseButtonRelease')
                self.finishDragging()
                self._mgr.titleMouseReleaseEvent()

        return False

    # def nativeEvent(self, event_type, message):
    #     super().nativeEvent(event_type, message)
    #     print('----->nativeEvent:',event_type, message)
    #     return False

    def dockContainer(self) -> 'CDockContainerWidget':
        '''
        Access function for the internal dock container

        Returns
        -------
        value : DockContainerWidget
        '''
        return self._mgr.dockContainer

    def hasNativeTitleBar(self):
        return self._mgr.titleBar is None

    def dockWidgets(self) -> list:
        '''
        This function returns a list of all dock widget in this floating
        widget. This is a simple convenience function that simply calls the
        dockWidgets() function of the internal container widget.

        Returns
        -------
        value : list
        '''
        return self._mgr.dockContainer.dockWidgets()
