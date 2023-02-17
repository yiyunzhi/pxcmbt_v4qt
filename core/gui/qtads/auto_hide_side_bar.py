# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : auto_hide_dock_container.py
# ------------------------------------------------------------------------------
#
# File          : auto_hide_dock_container.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import logging, typing
from PySide6 import QtCore, QtGui, QtWidgets
from .define import (EnumSideBarLocation, EnumDockWidgetArea)
from .util import findParent, findChild, findChildren
from .auto_hide_tab import CAutoHideTab
from .auto_hide_dock_container import CAutoHideDockContainer

if typing.TYPE_CHECKING:
    from .dock_container_widget import CDockContainerWidget
    from .dock_widget import CDockWidget

logger = logging.getLogger(__name__)


class CTabsWidget(QtWidgets.QWidget):
    def __init__(self, event_handler, parent=None):
        super().__init__(parent)
        self.eventHandler = event_handler

    def minimumSizeHint(self) -> QtCore.QSize:
        return super().sizeHint()

    def event(self, event: QtCore.QEvent) -> bool:
        self.eventHandler.handleViewportEvent(event)
        return super().event(event)


class AutoHideSideBarMgr:
    _this: 'CAutoHideSideBar'
    containerWidget: 'CDockContainerWidget'
    tabsContainerWidget: CTabsWidget
    tabsLayout: QtWidgets.QBoxLayout
    orientation: QtCore.Qt.Orientation
    sideTabArea: EnumSideBarLocation

    def __init__(self, _this):
        self._this = _this
        self.containerWidget = None
        self.tabsContainerWidget = None
        self.tabsLayout = None
        self.orientation = None
        self.sideTabArea = EnumSideBarLocation.LEFT

    def isHorizontal(self):
        return self.orientation == QtCore.Qt.Orientation.Horizontal

    def handleViewportEvent(self, e: QtCore.QEvent):
        if e.type() == QtCore.QEvent.Type.ChildRemoved:
            if self.tabsLayout.isEmpty():
                self._this.hide()
        elif e.type() == QtCore.QEvent.Type.Resize:
            if self._this.tabCount():
                _tab = self._this.tabAt(0)
                _size = e.size().height() if self.isHorizontal() else e.size().width()
                _tab_size = _tab.size().height() if self.isHorizontal() else _tab.size().width()
                # If the size of the side bar is less than the size of the first tab
                # then there are no visible tabs in this side bar. This check will
                # fail if someone will force a very big border via CSS!!
                if _size < _tab_size:
                    self._this.hide()
            else:
                self._this.hide()


class CAutoHideSideBar(QtWidgets.QScrollArea):
    def __init__(self, parent: 'CDockContainerWidget', location: EnumSideBarLocation):
        super().__init__(parent)
        self._mgr = AutoHideSideBarMgr(self)
        self._mgr.sideTabArea = location
        self._mgr.containerWidget = parent
        self._mgr.orientation = QtCore.Qt.Orientation.Horizontal if location in [EnumSideBarLocation.TOP,
                                                                                 EnumSideBarLocation.BOTTOM] else QtCore.Qt.Orientation.Vertical
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        self.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._mgr.tabsContainerWidget = CTabsWidget(self._mgr)
        self._mgr.tabsContainerWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        self._mgr.tabsContainerWidget.setObjectName('sideTabsContainerWidget')

        _l_dir = QtWidgets.QBoxLayout.Direction.TopToBottom if QtCore.Qt.Orientation.Vertical == self._mgr.orientation else QtWidgets.QBoxLayout.Direction.LeftToRight
        self._mgr.tabsLayout = QtWidgets.QBoxLayout(_l_dir)
        self._mgr.tabsLayout.setContentsMargins(0, 0, 0, 0)
        self._mgr.tabsLayout.setSpacing(12)
        self._mgr.tabsLayout.addStretch(1)

        self._mgr.tabsContainerWidget.setLayout(self._mgr.tabsLayout)
        self.setWidget(self._mgr.tabsContainerWidget)

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        if self._mgr.isHorizontal():
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        else:
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        self.hide()

    # def destroy(self, destroyWindow: bool = ..., destroySubWindows: bool = ...) -> None:
    #     logger.debug('CAutoHideSideBar destroy')
    #     _tabs = findChildren(self, CAutoHideTab, options=QtCore.Qt.FindChildOption.FindDirectChildrenOnly)
    #     for x in _tabs:
    #         x.setParent(None)
    #     self._mgr = None
    #     super().destroy(destroyWindow, destroySubWindows)

    def insertTab(self, index: int, side_tab: CAutoHideTab):
        side_tab.setSideBar(self)
        side_tab.installEventFilter(self)
        if index < 0:
            self._mgr.tabsLayout.insertWidget(self._mgr.tabsLayout.count() - 1, side_tab)
        else:
            self._mgr.tabsLayout.insertWidget(index, side_tab)
        self.show()

    def insertDockWidget(self, index: int, dock_widget: 'CDockWidget'):
        _auto_hide_container = CAutoHideDockContainer(dock_widget, self._mgr.sideTabArea, self._mgr.containerWidget)
        dock_widget.dockManager().dockFocusController().clearDockWidgetFocus(dock_widget)
        _tab = _auto_hide_container.autoHideTab()
        dock_widget.setSideTabWidget(_tab)
        self.insertTab(index, _tab)
        return _auto_hide_container

    def removeAutoHideWidget(self, auto_hide_widget: CAutoHideDockContainer):
        auto_hide_widget.autoHideTab().removeFromSideBar()
        _dock_container = auto_hide_widget.dockContainer()
        if _dock_container:
            _dock_container.removeAutoHideWidget(auto_hide_widget)
        auto_hide_widget.setParent(None)

    def addAutoHideWidget(self, auto_hide_widget: CAutoHideDockContainer):
        _side_bar = auto_hide_widget.autoHideTab().sideBar()
        if _side_bar is self:
            return
        if _side_bar is not None:
            _side_bar.removeAutoHideWidget(auto_hide_widget)
        auto_hide_widget.setParent(self._mgr.containerWidget)
        auto_hide_widget.setSideBarLocation(self._mgr.sideTabArea)
        self._mgr.containerWidget.registerAutoHideWidget(auto_hide_widget)
        self.insertTab(-1, auto_hide_widget.autoHideTab())

    def removeTab(self, side_tab: CAutoHideTab):
        side_tab.removeEventFilter(self)
        self._mgr.tabsLayout.removeWidget(side_tab)
        if self._mgr.tabsLayout.isEmpty():
            self.hide()

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent):
        if event.type() != QtCore.QEvent.Type.ShowToParent:
            return False
        # As soon as on tab is shown, we need to show the side tab bar
        if isinstance(watched, CAutoHideTab):
            self.show()
        return False

    def orientation(self):
        return self._mgr.orientation

    def tabAt(self, index):
        _w = self._mgr.tabsLayout.itemAt(index).widget()
        return _w if isinstance(_w, CAutoHideTab) else None

    def tabCount(self):
        return self._mgr.tabsLayout.count() - 1

    def sideBarLocation(self):
        return self._mgr.sideTabArea

    def saveState(self, s: QtCore.QXmlStreamWriter):
        if not self.tabCount():
            return
        s.writeStartElement('SideBar')
        s.writeAttribute('Area', str(self.sideBarLocation().value))
        s.writeAttribute('Tabs', str(self.tabCount()))
        for i in range(self.tabCount()):
            _tab = self.tabAt(i)
            if _tab is None:
                continue
            _tab.dockWidget().autoHideDockContainer().saveState(s)
        s.writeEndElement()

    def minimumSizeHint(self) -> QtCore.QSize:
        _size = self.sizeHint()
        _size.setWidth(10)
        return _size

    def sizeHint(self) -> QtCore.QSize:
        return self._mgr.tabsContainerWidget.sizeHint()

    def spacing(self):
        return self._mgr.tabsLayout.spacing()

    def setSpacing(self, spacing: int):
        self._mgr.tabsLayout.setSpacing(spacing)

    def dockContainer(self):
        return self._mgr.containerWidget

    eSideBarLocation = QtCore.Property(int, lambda x: x.sideBarLocation().value)