import logging, typing
from PySide6 import QtCore, QtGui, QtWidgets
from .define import (EnumSideBarLocation,
                     EnumDockWidgetArea,
                     DOCK_MANAGER_DEFAULT_CONFIG,
                     EnumDockMgrConfigFlag,
                     EnumRepolishChildOptions)
from .util import (findParent,
                   qApp,
                   repolishStyle,
                   evtFloatingWidgetDragStartEvent,
                   evtDockedWidgetDragStartEvent)
from .resize_handle import CResizeHandle
from .auto_hide_tab import CAutoHideTab
from .dock_components_factory import DEFAULT_COMPONENT_FACTORY

if typing.TYPE_CHECKING:
    from .dock_widget import CDockWidget
    from .dock_area_widget import CDockAreaWidget
    from .dock_container_widget import CDockContainerWidget


def is_horizontal_area(loc: EnumSideBarLocation):
    if loc in [EnumSideBarLocation.RIGHT, EnumSideBarLocation.LEFT]:
        return False
    return True


def get_edge_from_side_bar_area(loc: EnumSideBarLocation):
    if loc == EnumSideBarLocation.TOP:
        return QtCore.Qt.Edge.BottomEdge
    elif loc == EnumSideBarLocation.BOTTOM:
        return QtCore.Qt.Edge.TopEdge
    elif loc == EnumSideBarLocation.LEFT:
        return QtCore.Qt.Edge.RightEdge
    elif loc == EnumSideBarLocation.RIGHT:
        return QtCore.Qt.Edge.LeftEdge
    return QtCore.Qt.Edge.LeftEdge


def resize_handle_layout_position(loc: EnumSideBarLocation):
    if loc in [EnumSideBarLocation.TOP, EnumSideBarLocation.LEFT]:
        return 1
    return 0


class AutoHideDockContainerMgr:
    _this: 'CAutoHideDockContainer'
    dockArea: 'CDockAreaWidget'
    dockWidget: 'CDockWidget'
    sideTabBarArea: EnumSideBarLocation
    layout: QtWidgets.QBoxLayout
    resizeHandle: CResizeHandle
    size: QtCore.QSize
    sideTab: CAutoHideTab
    RESIZE_MARGIN = 30

    def __init__(self, _this):
        self._this = _this
        self.dockArea = None
        self.dockWidget = None
        self.sideTabBarArea = EnumSideBarLocation.NONE
        self.layout = None
        self.resizeHandle = None
        self.size = QtCore.QSize()
        self.sideTab = None

    @staticmethod
    def getDockWidgetArea(loc: EnumSideBarLocation):
        if loc == EnumSideBarLocation.LEFT:
            return EnumDockWidgetArea.LEFT
        elif loc == EnumSideBarLocation.RIGHT:
            return EnumDockWidgetArea.RIGHT
        elif loc == EnumSideBarLocation.TOP:
            return EnumDockWidgetArea.TOP
        elif loc == EnumSideBarLocation.BOTTOM:
            return EnumDockWidgetArea.BOTTOM
        else:
            return EnumDockWidgetArea.NO_AREA

    def updateResizeHandleSizeLimitMax(self):
        _dc = self._this.dockContainer()
        if _dc is None:
            return
        _rect = _dc.contentRect()
        if self.resizeHandle.orientation() == QtCore.Qt.Orientation.Horizontal:
            _max_resize_handle_size = _rect.width()
        else:
            _max_resize_handle_size = _rect.height()
        self.resizeHandle.setMaxResizeSize(_max_resize_handle_size - self.RESIZE_MARGIN)

    def isHorizontal(self):
        return is_horizontal_area(self.sideTabBarArea)

    def forwardEventToDockContainer(self, event: QtCore.QEvent):
        _dc = self._this.dockContainer()
        if _dc is not None:
            _dc.handleAutoHideWidgetEvent(event, self._this)


class CAutoHideDockContainer(QtWidgets.QFrame):
    def __init__(self, dock_widget: 'CDockWidget', area: EnumSideBarLocation,
                 parent: 'CDockContainerWidget'):
        super().__init__(parent)
        self._mgr = AutoHideDockContainerMgr(self)
        self.hide()
        self._mgr.sideTabBarArea = area
        self._mgr.sideTab = DEFAULT_COMPONENT_FACTORY.createDockWidgetSideTab()
        self._mgr.sideTab.pressed.connect(self.toggleCollapseState)
        self._mgr.dockArea = CDockAreaWidget(dock_widget.dockManager(), parent)
        self._mgr.dockArea.setObjectName("autoHideDockArea")
        self._mgr.dockArea.setAutoHideDockContainer(self)

        self.setObjectName("autoHideDockContainer")
        _ld = QtWidgets.QBoxLayout.Direction.TopToBottom if is_horizontal_area(area) else QtWidgets.QBoxLayout.Direction.LeftToRight
        self._mgr.layout = QtWidgets.QBoxLayout(_ld)
        self._mgr.layout.setContentsMargins(0, 0, 0, 0)
        self._mgr.layout.setSpacing(0)
        self.setLayout(self._mgr.layout)
        self.ResizeHandle = CResizeHandle(get_edge_from_side_bar_area(area), self)
        self.ResizeHandle.setMinResizeSize(64)

        _opaqueResize = EnumDockMgrConfigFlag.OpaqueSplitterResize in DOCK_MANAGER_DEFAULT_CONFIG
        self._mgr.resizeHandle.setOpaqueResize(_opaqueResize)
        self._mgr.Size = self._mgr.dockArea.size()

        self.addDockWidget(dock_widget)
        self.parent.registerAutoHideWidget(self)

        # The dock area should not be added to the layout before it contains the
        # dock widget. If you add it to the layout before it contains the dock widget
        # then you will likely see this warning for OpenGL widgets or QAxWidgets:
        # setGeometry: Unable to set geometry XxY+Width+Height on QWidgetWindow/'WidgetClassWindow

        self._mgr.layout.addWidget(self._mgr.dockArea)
        self._mgr.layout.insertWidget(resize_handle_layout_position(area), self._mgr.resizeHandle)

    def destroy(self, destroyWindow: bool = ..., destroySubWindows: bool = ...) -> None:
        logging.debug('~CAutoHideDockContainer')
        qApp.removeEventFilter(self)
        if self.dockContainer():
            self.dockContainer().removeAutoHideWidget(self)
        if self._mgr.sideTab:
            self._mgr.sideTab = None

    def sideTab(self):
        if self._mgr.sideTab:
            return self._mgr.sideTab.sideBar()
        else:
            _container = self.dockContainer()
            if _container is not None:
                return _container.sideTabBar(self._mgr.sideTabBarArea)
            else:
                return None

    def dockContainer(self) -> 'CDockContainerWidget':
        return findParent(CDockContainerWidget, self)

    def autoHideTab(self):
        return self._mgr.sideTab

    def dockWidget(self):
        return self._mgr.dockWidget

    def sideBarLocation(self):
        return self._mgr.sideTabBarArea

    def sideBar(self):
        if self._mgr.sideTab:
            return self._mgr.sideTab.sideBar()
        else:
            _dc = self.dockContainer()
            return _dc.sideTabBar(self._mgr.sideTabBarArea) if _dc is not None else None

    def dockAreaWidget(self):
        return self._mgr.dockArea

    def updateSize(self):
        _dock_container_parent = self.dockContainer()
        if _dock_container_parent is None:
            return
        _rect = _dock_container_parent.contentRect()
        _sb_loc = self.sideBarLocation()
        if _sb_loc == EnumSideBarLocation.TOP:
            self.resize(_rect.width(), min(_rect.height() - self._mgr.RESIZE_MARGIN, self._mgr.size.height()))
            self.move(_rect.topLeft())
        elif _sb_loc == EnumSideBarLocation.LEFT:
            self.resize(min(self._mgr.size.width(), _rect.width() - self._mgr.RESIZE_MARGIN), _rect.height())
            self.move(_rect.topLeft())
        elif _sb_loc == EnumSideBarLocation.RIGHT:
            self.resize(min(self._mgr.size.width(), _rect.width() - self._mgr.RESIZE_MARGIN), _rect.height())
            _p = _rect.topRight().rx()
            _p -= (self.width() - 1)
            self.move(_p)
        elif _sb_loc == EnumSideBarLocation.RIGHT:
            self.resize(_rect.width(), min(_rect.height() - self._mgr.RESIZE_MARGIN, self._mgr.size.height()))
            _p = _rect.bottomLeft().rx()
            _p -= (self.height() - 1)
            self.move(_p)

    def addDockWidget(self, dock_widget: 'CDockWidget'):
        if self._mgr.dockWidget:
            self._mgr.dockArea.removeDockWidget(self._mgr.dockWidget)
        self._mgr.dockWidget = dock_widget
        self._mgr.sideTab.setDockWidget(dock_widget)
        _old_dock_area = dock_widget.dockAreaWidget()
        _is_restoring_state = dock_widget.dockManager().isRestoringState()
        if _old_dock_area and not _is_restoring_state:
            # The initial size should be a little bit bigger than the original dock
            # area size to prevent that the resize handle of this auto hid dock area
            # is near of the splitter of the old dock area.
            self._mgr.size = _old_dock_area.size() + QtCore.QSize(16, 16)
            _old_dock_area.removeDockWidget(dock_widget)
        self._mgr.dockArea.addDockWidget(dock_widget)
        self.updateSize()

    def setSideBarLocation(self, location: EnumSideBarLocation):
        if self._mgr.sideTabBarArea == location:
            return
        self._mgr.sideTabBarArea = location
        self._mgr.layout.removeWidget(self._mgr.resizeHandle)
        if is_horizontal_area(location):
            self._mgr.layout.setDirection(QtWidgets.QBoxLayout.Direction.TopToBottom)
        else:
            self._mgr.layout.setDirection(QtWidgets.QBoxLayout.Direction.LeftToRight)
        self._mgr.layout.insertWidget(resize_handle_layout_position(location), self._mgr.resizeHandle)
        self._mgr.resizeHandle.setHandlePosition(get_edge_from_side_bar_area(location))
        repolishStyle(self, EnumRepolishChildOptions.RepolishDirectChildren)

    def moveContentsToParent(self):
        self.cleanupAndDelete()
        # If we unpin the auto hide dock widget, then we insert it into the same
        # location like it had as a auto hide widget.  This brings the least surprise
        # to the user and he does not have to search where the widget was inserted.
        self._mgr.dockWidget.setDockArea(None)
        _dc = self.dockContainer()
        _dc.addDockWidget(self._mgr.getDockWidgetArea(self._mgr.sideTabBarArea), self._mgr.dockWidget)

    def cleanupAndDelete(self):
        _dw = self._mgr.dockWidget
        if _dw:
            self._mgr.sideTab.removeFromSideBar()
            self._mgr.sideTab.setParent(None)
            self._mgr.sideTab.hide()
        self.hide()
        self.deleteLater()

    def saveState(self, xml_stream: QtCore.QXmlStreamWriter):
        xml_stream.writeStartElement('Widget')
        xml_stream.writeAttribute('Name', self._mgr.dockWidget.objectName())
        xml_stream.writeAttribute('Closed', str(self._mgr.dockWidget.isClosed()))
        xml_stream.writeAttribute('Size', str(self._mgr.size.height() if self._mgr.isHorizontal() else self._mgr.size.width()))

    def toggleView(self, enable):
        if enable:
            if self._mgr.sideTab:
                self._mgr.sideTab.show()
        else:
            if self._mgr.sideTab:
                self._mgr.sideTab.hide()
            self.hide()
            qApp.removeEventFilter(self)

    def collapseView(self, enable):
        if enable:
            self.hide()
            qApp.removeEventFilter(self)
        else:
            self.updateSize()
            self._mgr.updateResizeHandleSizeLimitMax()
            self.raise_()
            self.show()
            self._mgr.dockWidget.dockManager().setDockWidgetFocused(self._mgr.dockWidget)
            qApp.installEventFilter(self)
        logging.debug('CAutoHideDockContainer::collapseView enable=%s' % enable)
        self._mgr.sideTab.updateStyle()

    def toggleCollapseState(self):
        self.collapseView(self.isVisible())

    def setSize(self, size: int):
        if self._mgr.isHorizontal():
            self._mgr.size.setHeight(size)
        else:
            self._mgr.size.setWidth(size)
        self.updateSize()

    def objectIsAncestorOf(self, descendant: QtCore.QObject, ancestor: QtCore.QObject):
        if not ancestor:
            return False
        while descendant:
            if descendant == ancestor:
                return True
            descendant = descendant.parent()
        return False

    def isObjectOrAncestor(self, descendant: QtCore.QObject, ancestor: QtCore.QObject):
        if ancestor and (ancestor == descendant):
            return True
        else:
            return self.objectIsAncestorOf(descendant, ancestor)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.Resize:
            if not self._mgr.resizeHandle.isResizing():
                self.updateSize()
        elif event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if not watched:
                return super().eventFilter(watched, event)

            # Now check, if the user clicked into the side tab and ignore this event,
            # because the side tab click handler will call collapseView(). If we
            # do not ignore this here, then we will collapse the container and the side tab
            # click handler will uncollapse it

            if watched == self._mgr.sideTab:
                return super().eventFilter(watched, event)

            # Now we check, if the user clicked inside of this auto hide container.
            # If the click is inside of this auto hide container, then we can
            # ignore the event, because the auto hide overlay should not get collapsed if
            # user works in it

            if self.isObjectOrAncestor(watched, self):
                return super().eventFilter(watched, event)
            # // Ignore the mouse click if it is not inside of this container
            if not self.isObjectOrAncestor(watched, self.dockContainer()):
                return super().eventFilter(watched, event)
            # user clicked into container - collapse the auto hide widget
            self.collapseView(True)
        elif event.type() == evtFloatingWidgetDragStartEvent:
            # If we are dragging our own floating widget, the we do not need to
            # collapse the view
            _float_w = self.dockContainer().floatingWidget()
            if _float_w != watched:
                self.collapseView(True)
        elif event.type() == evtDockedWidgetDragStartEvent:
            self.collapseView(True)
        return super().eventFilter(watched, event)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._mgr.resizeHandle.isResizing():
            self._mgr.size = self.size()
            self._mgr.updateResizeHandleSizeLimitMax()

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        _pos = self.mapFromGlobal(QtGui.QCursor.pos())
        if not self.rect().contains(_pos):
            self._mgr.forwardEventToDockContainer(event)
        super().leaveEvent(event)

    def event(self, e: QtCore.QEvent) -> bool:
        if e.type() in [QtCore.QEvent.Type.Enter, QtCore.QEvent.Type.Hide]:
            self._mgr.forwardEventToDockContainer(e)
        elif e.type() == QtCore.QEvent.Type.MouseButtonPress:
            return True
        return super().event(e)
