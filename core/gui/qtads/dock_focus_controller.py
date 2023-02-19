# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : dock_focus_controller.py
# ------------------------------------------------------------------------------
#
# File          : dock_focus_controller.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import typing, logging
from core.gui.qtimp import QtCore, QtGui, QtWidgets
from .define import EnumDockWidgetFeature
from .util import LINUX, getQApp, repolishStyle, EnumRepolishChildOptions, findParent
from .dock_widget_tab import CDockWidgetTab

from .dock_widget import CDockWidget
from .dock_area_widget import CDockAreaWidget

if typing.TYPE_CHECKING:
    from .dock_manager import CDockManager
    from .floating_dock_container import CFloatingDockContainer

logger = logging.getLogger(__name__)
_FocusedDockWidgetProperty = "FocusedDockWidget"


def updateDockWidgetFocusStyle(dock_widget: 'CDockWidget', focused: bool):
    dock_widget.setProperty('focused', focused)
    dock_widget.tabWidget().setProperty('focused', focused)
    dock_widget.tabWidget().updateStyle()
    repolishStyle(dock_widget)


def updateDockAreaFocusStyle(dock_area, focused: bool):
    dock_area.setProperty('focused', focused)
    repolishStyle(dock_area)
    repolishStyle(dock_area.titleBar())


if LINUX:
    from .linux.floating_widget_title_bar import CFloatingWidgetTitleBar


    def updateFloatingWidgetFocusStyle(floating_widget: CFloatingDockContainer, focused: bool):
        if floating_widget.hasNativeTitleBar():
            return
        _title_bar = floating_widget.titleBarWidget()
        if isinstance(_title_bar, CFloatingWidgetTitleBar):
            return
        _title_bar.setProperty('focused', focused)
        _title_bar.updateStyle()


class DockFocusControllerMgr:
    _this: 'CDockFocusController'
    focusedDockWidget: 'CDockWidget'
    focusedArea: 'CDockAreaWidget'
    oldFocusedDockWidget: 'CDockWidget'
    if LINUX:
        floatingWidget: 'CFloatingDockContainer'
    dockManager: 'CDockManager'
    forceFocusChangedSignal: bool

    def __init__(self, _this: 'CDockFocusController'):
        self._this = _this
        self.focusedDockWidget = None
        self.focusedArea = None
        self.oldFocusedDockWidget = None
        self.dockManager = None
        self.forceFocusChangedSignal = False

    def _onFocusAreaDestroyed(self, evt):
        self.focusedArea = None

    def updateDockWidgetFocus(self, dock_widget: 'CDockWidget'):
        if EnumDockWidgetFeature.FOCUSABLE not in dock_widget.features():
            return
        _window = None
        _dock_container = dock_widget.dockContainer()
        if _dock_container is not None:
            _window = _dock_container.window().windowHandle()
        if _window is not None:
            _window.setProperty(_FocusedDockWidgetProperty, dock_widget)
        _new_focused_dock_area = None
        if self.focusedDockWidget:
            updateDockWidgetFocusStyle(self.focusedDockWidget, False)
        _old = self.focusedDockWidget
        self.focusedDockWidget = dock_widget
        updateDockWidgetFocusStyle(self.focusedDockWidget, True)
        _new_focused_dock_area = self.focusedDockWidget.dockAreaWidget()
        if _new_focused_dock_area is not None and self.focusedArea is not _new_focused_dock_area:
            if self.focusedArea is not None:
                self.focusedArea.sigViewToggled.disconnect(self._this.onFocusedDockAreaViewToggled)
                updateDockAreaFocusStyle(self.focusedArea, False)
            self.focusedArea = _new_focused_dock_area
            updateDockAreaFocusStyle(self.focusedArea, True)
            self.focusedArea.sigViewToggled.connect(self._this.onFocusedDockAreaViewToggled)
            # modified: if focusedArea is gone should this reference updated
            self.focusedArea.destroyed.connect(self._onFocusAreaDestroyed)
        _new_floating_widget = None
        _dock_container = self.focusedDockWidget.dockContainer()
        if _dock_container is not None:
            _new_floating_widget = _dock_container.floatingWidget()
        if _new_floating_widget is not None:
            _new_floating_widget.setProperty(_FocusedDockWidgetProperty, dock_widget)
        if LINUX:
            # This code is required for styling the floating widget titlebar for linux
            # depending on the current focus state
            if self.floatingWidget is not _new_floating_widget:
                if self.floatingWidget is not None:
                    updateFloatingWidgetFocusStyle(self.floatingWidget, False)
                self.floatingWidget = _new_floating_widget
                if self.floatingWidget is not None:
                    updateFloatingWidgetFocusStyle(self.floatingWidget, True)
        if _old is dock_widget and not self.forceFocusChangedSignal:
            return
        self.forceFocusChangedSignal = False
        if dock_widget.isVisible():
            self.dockManager.sigFocusedDockWidgetChanged.emit(_old, dock_widget)
        else:
            self.oldFocusedDockWidget = _old
            dock_widget.sigVisibilityChanged.connect(self._this.onDockWidgetVisibilityChanged)


class CDockFocusController(QtCore.QObject):
    def __init__(self, dock_manager: 'CDockManager'):
        super().__init__()
        self._mgr = DockFocusControllerMgr(self)
        self._mgr.dockManager = dock_manager
        getQApp().focusChanged.connect(self.onApplicationFocusChanged)
        getQApp().focusWindowChanged.connect(self.onFocusWindowChanged)
        self._mgr.dockManager.sigStateRestored.connect(self.onStateRestored)

    def onFocusWindowChanged(self, focus_win: QtGui.QWindow):
        if focus_win is None:
            return
        _v_dock_widget = focus_win.property(_FocusedDockWidgetProperty)
        if _v_dock_widget is None:
            return
        logger.debug('CDockFocusController:onFocusWindowChanged read instance from property')
        self._mgr.updateDockWidgetFocus(_v_dock_widget)

    def onFocusedDockAreaViewToggled(self, open_: bool):
        if self._mgr.dockManager.isRestoringState():
            return
        _sender = self.sender()
        if open_ or not isinstance(_sender, CDockAreaWidget):
            return
        _container = _sender.dockContainer()
        _opened_dock_areas = _container.openedDockAreas()
        if not _opened_dock_areas:
            return
        self._mgr.updateDockWidgetFocus(_opened_dock_areas[0].currentDockWidget())

    def onApplicationFocusChanged(self, focused_old: QtWidgets.QWidget, focused_now: QtWidgets.QWidget):
        if self._mgr.dockManager.isRestoringState():
            return
        logger.debug('CDockFocusController::onApplicationFocusChanged old:{}, new:{}'.format(focused_old, focused_now))
        if focused_now is None:
            return
        _dock_widget = None
        if not isinstance(focused_now, CDockWidget):
            _dock_widget = findParent(CDockWidget, focused_now)
        if LINUX:
            if _dock_widget is None:
                return
        elif _dock_widget is None or _dock_widget.tabWidget().isHidden():
            return
        self._mgr.updateDockWidgetFocus(_dock_widget)

    def setDockWidgetTabFocused(self, tab: CDockWidgetTab):
        _dock_widget = tab.dockWidget()
        if _dock_widget is not None:
            self._mgr.updateDockWidgetFocus(_dock_widget)

    def clearDockWidgetFocus(self, dock_widget: 'CDockWidget'):
        dock_widget.clearFocus()
        updateDockWidgetFocusStyle(dock_widget, False)

    def setDockWidgetFocused(self, dock_widget: 'CDockWidget'):
        self._mgr.updateDockWidgetFocus(dock_widget)

    def onDockWidgetVisibilityChanged(self, visible):
        _sender = self.sender()
        if isinstance(_sender, CDockWidget):
            _sender.sigVisibilityChanged.disconnect(self.onDockWidgetVisibilityChanged)
        if _sender is not None and visible:
            self._mgr.dockManager.sigFocusedDockWidgetChanged.emit(self._mgr.oldFocusedDockWidget, _sender)

    def notifyWidgetOrAreaRelocation(self, dropped_widget: QtWidgets.QWidget):
        if self._mgr.dockManager.isRestoringState():
            return
        if dropped_widget is None:
            return
        if isinstance(dropped_widget, CDockAreaWidget):
            dropped_widget = dropped_widget.currentDockWidget()
        self._mgr.forceFocusChangedSignal = True
        self._mgr.dockManager.setDockWidgetFocused(dropped_widget)

    def notifyFloatingWidgetDrop(self, floating_widget: 'CFloatingDockContainer'):
        if floating_widget is None or self._mgr.dockManager.isRestoringState():
            return
        _v_dock_widget = floating_widget.property(_FocusedDockWidgetProperty)
        if _v_dock_widget is None:
            return
        logger.debug('--->notifyFloatingWidgetDrop construct _dock_widget')
        _dock_widget = _v_dock_widget
        if _dock_widget is not None:
            _dock_widget.dockAreaWidget().setCurrentDockWidget(_dock_widget)
            self._mgr.dockManager.setDockWidgetFocused(_dock_widget)

    def onStateRestored(self):
        if self._mgr.focusedDockWidget is not None:
            updateDockWidgetFocusStyle(self._mgr.focusedDockWidget, False)

    def focusedDockWidget(self):
        return self._mgr.focusedDockWidget
