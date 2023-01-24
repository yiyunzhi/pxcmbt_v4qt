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
from typing import TYPE_CHECKING
from PySide6 import QtGui, QtCore, QtWidgets
from .push_button import CPushButton, EnumButtonOrientation
from .define import (EnumSideBarLocation, EnumAutoHideFlag, AUTO_HIDE_DEFAULT_CONFIG)
from .util import repolishStyle, EnumRepolishChildOptions

if TYPE_CHECKING:
    from .auto_hide_side_bar import CAutoHideSideBar
    from .dock_widget import CDockWidget


class AutoHideTabMgr:
    _this: 'CAutoHideTab'
    dockWidget: 'CDockWidget'
    sideBar: 'CAutoHideSideBar'
    orientation: QtCore.Qt.Orientation
    timerSinceHoverMousePress: QtCore.QElapsedTimer

    def __init__(self, _this: 'CAutoHideTab'):
        self._this = _this
        self.dockWidget = None
        self.sideBar = None
        self.orientation = QtCore.Qt.Orientation.Vertical
        self.timerSinceHoverMousePress = QtCore.QElapsedTimer()

    def updateOrientation(self):
        _icon_only = EnumAutoHideFlag.AutoHideSideBarsIconOnly in AUTO_HIDE_DEFAULT_CONFIG
        if _icon_only and not self._this.icon().isNull():
            self._this.setText('')
            self._this.setOrientation(QtCore.Qt.Orientation.Horizontal)
        else:
            _area = self.sideBar.sideBarLocation()
            _orientation = QtCore.Qt.Orientation.Horizontal if _area in [EnumSideBarLocation.BOTTOM,
                                                                         EnumSideBarLocation.TOP] else QtCore.Qt.Orientation.Vertical
            self._this.setOrientation(_orientation)

    def dockContainer(self):
        return self.dockWidget.dockContainer() if self.dockWidget is not None else None

    def forwardEventToDockContainer(self, event: QtCore.QEvent):
        _dc = self.dockContainer()
        if _dc is not None:
            _dc.handleAutoHideWidgetEvent(event, self._this)


class CAutoHideTab(CPushButton):
    def __init__(self, parent: QtWidgets.QWidget):
        CPushButton.__init__(self, parent)
        self._mgr = AutoHideTabMgr(self)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoMousePropagation)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def setSideBar(self, side_tab_bar: 'CAutoHideSideBar'):
        self._mgr.sideBar = side_tab_bar
        if self._mgr.sideBar:
            self._mgr.updateOrientation()

    def removeFromSideBar(self):
        if self._mgr.sideBar is None:
            return
        self._mgr.sideBar.removeTab(self)
        self.setSideBar(None)

    def updateStyle(self):
        repolishStyle(self, EnumRepolishChildOptions.RepolishDirectChildren)
        self.update()

    def sideBarLocation(self):
        if self._mgr.sideBar is not None:
            return self._mgr.sideBar.sideBarLocation()
        return EnumSideBarLocation.LEFT

    def setOrientation(self, orientation: QtCore.Qt.Orientation):
        self._mgr.orientation = orientation
        if orientation == QtCore.Qt.Orientation.Horizontal:
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        else:
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        _orientation = EnumButtonOrientation.Horizontal if orientation == QtCore.Qt.Orientation.Horizontal else EnumButtonOrientation.VerticalTopToBottom
        self.setButtonOrientation(_orientation)
        self.updateStyle()

    def orientation(self):
        return self._mgr.orientation

    def isActiveTab(self):
        if self._mgr.dockWidget is not None and self._mgr.dockWidget.autoHideDockContainer() is not None:
            return self._mgr.dockWidget.autoHideDockContainer().isVisible()
        return False

    def dockWidget(self) -> 'CDockWidget':
        return self._mgr.dockWidget

    def setDockWidget(self, widget: 'CDockWidget'):
        if widget is None:
            return
        self._mgr.dockWidget = widget
        self.setText(widget.windowTitle())
        if self._mgr.dockWidget.icon():
            self.setIcon(self._mgr.dockWidget.icon())
        self.setToolTip(widget.windowTitle())

    def iconOnly(self):
        return EnumAutoHideFlag.AutoHideSideBarsIconOnly in AUTO_HIDE_DEFAULT_CONFIG

    def sideBar(self) -> 'CAutoHideSideBar':
        return self._mgr.sideBar

    def event(self, event: QtCore.QEvent):
        if EnumAutoHideFlag.AutoHideShowOnMouseOver not in AUTO_HIDE_DEFAULT_CONFIG:
            return super().event(event)
        if event.type() in [QtCore.QEvent.Type.Enter, QtCore.QEvent.Type.Leave]:
            self._mgr.forwardEventToDockContainer(event)
        elif event.type() == QtCore.QEvent.Type.MouseButtonPress:
            # If AutoHideShowOnMouseOver is active, then the showing is triggered
            # by a MousePressEvent sent to this tab. To prevent accidental hiding
            # of the tab by a mouse click, we wait at least 500 ms before we accept
            # the mouse click
            if not event.spontaneous():
                self._mgr.timerSinceHoverMousePress.restart()
                self._mgr.forwardEventToDockContainer(event)
            elif self._mgr.timerSinceHoverMousePress.hasExpired(500):
                self._mgr.forwardEventToDockContainer(event)
        return super().event(event)

    eSideBarLocation = QtCore.Property(int, lambda x: x.sideBarLocation().value)
    pIconOnly = QtCore.Property(bool, iconOnly)
    pActivTab = QtCore.Property(bool, isActiveTab)
