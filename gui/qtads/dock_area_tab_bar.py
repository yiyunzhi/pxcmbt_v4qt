from typing import TYPE_CHECKING, Optional
import logging
from PySide6 import QtCore, QtGui, QtWidgets

from .util import startDragDistance, eventFilterDecorator
from .define import EnumDragState, EnumDockWidgetArea, EnumDockWidgetFeature
from .dock_widget_tab import CDockWidgetTab


if TYPE_CHECKING:
    from .dock_area_widget import CDockAreaWidget

logger = logging.getLogger(__name__)


class DockAreaTabBarMgr:
    _this: 'CDockAreaTabBar'
    dockArea: 'CDockAreaWidget'
    tabsContainerWidget: QtWidgets.QWidget
    tabsLayout: QtWidgets.QBoxLayout
    currentIndex: int

    def __init__(self, _this: 'CDockAreaTabBar'):
        '''
        Private data for DockAreaTabBar

        Parameters
        ----------
        _this : CDockAreaTabBar
        '''
        self._this = _this
        self.dockArea = None
        self.tabsContainerWidget = None
        self.tabsLayout = None
        self.currentIndex = -1

    def firstTab(self):
        return self._this.tab(0)

    def lastTab(self):
        return self._this.tab(self._this.count() - 1)

    def updateTabs(self):
        '''
        Update tabs after current index changed or when tabs are removed. The
        function reassigns the stylesheet to update the tabs
        '''
        # Set active TAB and update all other tabs to be inactive
        for i in range(self._this.count()):
            _tab_widget = self._this.tab(i)
            if not _tab_widget:
                continue

            if i == self.currentIndex:
                _tab_widget.show()
                _tab_widget.setActiveTab(True)
                self._this.ensureWidgetVisible(_tab_widget)
            else:
                _tab_widget.setActiveTab(False)


class CDockAreaTabBar(QtWidgets.QScrollArea):
    # This signal is emitted when the tab bar's current tab is about to be
    # changed. The new current has the given index, or -1 if there isn't a new
    # one.
    sigCurrentChanging = QtCore.Signal(int)

    # This signal is emitted when the tab bar's current tab changes. The new
    # current has the given index, or -1 if there isn't a new one
    sigCurrentChanged = QtCore.Signal(int)

    # This signal is emitted when user clicks on a tab
    sigTabBarClicked = QtCore.Signal(int)

    # This signal is emitted when the close button on a tab is clicked. The
    # index is the index that should be closed.
    sigTabCloseRequested = QtCore.Signal(int)

    # This signal is emitted if a tab has been closed
    sigTabClosed = QtCore.Signal(int)

    # This signal is emitted if a tab has been opened. A tab is opened if it
    # has been made visible
    sigTabOpened = QtCore.Signal(int)

    # This signal is emitted when the tab has moved the tab at index position
    sigTabMoved = QtCore.Signal(int, int)

    # This signal is emitted, just before the tab with the given index is
    # removed
    sigRemovingTab = QtCore.Signal(int)

    # This signal is emitted if a tab has been inserted
    sigTabInserted = QtCore.Signal(int)
    sigElidedChanged = QtCore.Signal(bool)

    def __init__(self, parent: 'CDockAreaWidget'):
        '''
        Default Constructor

        Parameters
        ----------
        parent : DockAreaWidget
        '''
        super().__init__(parent)

        self._mgr = DockAreaTabBarMgr(self)
        self._mgr.dockArea = parent

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Ignored)
        self.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._mgr.tabsContainerWidget = QtWidgets.QWidget()
        self._mgr.tabsContainerWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        self._mgr.tabsContainerWidget.setObjectName("tabsContainerWidget")

        self._mgr.tabsLayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.LeftToRight)
        self._mgr.tabsLayout.setContentsMargins(0, 0, 0, 0)
        self._mgr.tabsLayout.setSpacing(0)
        self._mgr.tabsLayout.addStretch(1)
        self._mgr.tabsContainerWidget.setLayout(self._mgr.tabsLayout)

        self.setWidget(self._mgr.tabsContainerWidget)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def onTabClicked(self):
        _tab = self.sender()
        if not _tab or not isinstance(_tab, CDockWidgetTab):
            return

        _index = self._mgr.tabsLayout.indexOf(_tab)
        if _index < 0:
            return

        self.setCurrentIndex(_index)
        self.sigTabBarClicked.emit(_index)

    def onTabCloseRequested(self):
        _tab = self.sender()
        _index = self._mgr.tabsLayout.indexOf(_tab)
        self.closeTab(_index)

    def onCloseOtherTabsRequested(self):
        _sender = self.sender()

        for i in range(self.count()):
            _tab = self.tab(i)
            if _tab.isClosable() and not _tab.isHidden() and _tab != _sender:
                # If the dock widget is deleted with the closeTab() call, its tab
                # it will no longer be in the layout, and thus the index needs to
                # be updated to not skip any tabs
                _offset = 1 if EnumDockWidgetFeature.DELETE_ON_CLOSE in _tab.dockWidget().features() else 0
                self.closeTab(i)
                # If the the dock widget blocks closing, i.e. if the flag
                # CustomCloseHandling is set, and the dock widget is still open,
                # then we do not need to correct the index
                if _tab.dockWidget().isClosed():
                    i -= _offset

    def onTabWidgetMoved(self, global_pos: QtCore.QPoint):
        '''
        On tab widget moved

        Parameters
        ----------
        global_pos : QPoint
        '''
        _moving_tab = self.sender()
        if not _moving_tab or not isinstance(_moving_tab, CDockWidgetTab):
            return

        _from_index = self._mgr.tabsLayout.indexOf(_moving_tab)
        _mouse_pos = self.mapFromGlobal(global_pos)
        _mouse_pos.setX(max(self._mgr.firstTab().geometry().left(), _mouse_pos.x()))
        _mouse_pos.setY(min(self._mgr.lastTab().geometry().right(), _mouse_pos.x()))
        _to_index = -1

        # Find tab under mouse
        for i in range(self.count()):
            _drop_tab = self.tab(i)
            if (_drop_tab == _moving_tab or not _drop_tab.isVisibleTo(self) or
                    not _drop_tab.geometry().contains(_mouse_pos)):
                continue

            _to_index = self._mgr.tabsLayout.indexOf(_drop_tab)
            if _to_index == _from_index:
                _to_index = -1
            break

        # Now check if the mouse is behind the last tab
        if _to_index > -1:
            self._mgr.tabsLayout.removeWidget(_moving_tab)
            self._mgr.tabsLayout.insertWidget(_to_index, _moving_tab)
            logger.debug('tabMoved from %s to %s', _from_index, _to_index)
            self.sigTabMoved.emit(_from_index, _to_index)
            self.setCurrentIndex(_to_index)
        else:
            self._mgr.tabsLayout.update()

    def wheelEvent(self, event: QtGui.QWheelEvent):
        '''
        Wheelevent

        Parameters
        ----------
        event : QWheelEvent
        '''
        event.accept()
        _direction = event.angleDelta().y()
        _horizontal_bar = self.horizontalScrollBar()
        _delta = (20 if _direction < 0 else -20)
        _horizontal_bar.setValue(self.horizontalScrollBar().value() + _delta)

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        '''
        Stores mouse position to detect dragging

        Parameters
        ----------
        ev : QMouseEvent
        '''
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            ev.accept()
            self._mgr.drag_start_mouse_pos = ev.pos()
            return

        super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent):
        '''
        Stores mouse position to detect dragging

        Parameters
        ----------
        ev : QMouseEvent
        '''
        if ev.button() != QtCore.Qt.MouseButton.LeftButton:
            return super().mouseReleaseEvent(ev)

        logger.debug('DockAreaTabBar.mouseReleaseEvent')
        ev.accept()
        self._mgr.floating_widget = None
        self._mgr.drag_start_mouse_pos = QtCore.QPoint()

    def minimumSizeHint(self):
        _size = self.sizeHint()
        _size.setWidth(10)
        return _size

    def sizeHint(self) -> QtCore.QSize:
        return self._mgr.tabsContainerWidget.sizeHint()

    def insertTab(self, index: int, tab: 'CDockWidgetTab'):
        '''
        Inserts the given dock widget tab at the given position. Inserting a
        new tab at an index less than or equal to the current index will
        increment the current index, but keep the current tab.

        Parameters
        ----------
        index : int
        tab : DockWidgetTab
        '''
        self._mgr.tabsLayout.insertWidget(index, tab)
        tab.sigClicked.connect(self.onTabClicked)
        tab.sigCloseRequested.connect(self.onTabCloseRequested)
        tab.sigCloseOtherTabsRequested.connect(self.onCloseOtherTabsRequested)
        tab.sigMoved.connect(self.onTabWidgetMoved)
        tab.sigElidedChanged.connect(self.sigElidedChanged)
        tab.installEventFilter(self)
        self.sigTabInserted.emit(index)
        if index <= self._mgr.currentIndex:
            self.setCurrentIndex(self._mgr.currentIndex + 1)
        elif self._mgr.currentIndex == -1:
            self.setCurrentIndex(index)
        self.updateGeometry()

    def removeTab(self, tab: 'CDockWidgetTab'):
        '''
        Removes the given DockWidgetTab from the tabbar

        Parameters
        ----------
        tab : DockWidgetTab
        '''
        if not self.count():
            return

        logger.debug('DockAreaTabBar.removeTab')
        _new_current_index = self.currentIndex()
        _remove_index = self._mgr.tabsLayout.indexOf(tab)
        if self.count() == 1:
            _new_current_index = -1

        if _new_current_index > _remove_index:
            _new_current_index -= 1
        elif _new_current_index == _remove_index:
            _new_current_index = -1

            # First we walk to the right to search for the next visible tab
            for i in range(_remove_index + 1, self.count()):
                if self.tab(i).isVisibleTo(self):
                    _new_current_index = i - 1
                    break

            # If there is no visible tab right to this tab then we walk to
            # the left to find a visible tab
            if _new_current_index < 0:
                for i in range(_remove_index - 1, -1, -1):
                    if self.tab(i).isVisibleTo(self):
                        _new_current_index = i
                        break

        self.sigRemovingTab.emit(_remove_index)
        self._mgr.tabsLayout.removeWidget(tab)
        tab.disconnect(self)
        tab.removeEventFilter(self)
        logger.debug('NewCurrentIndex %s', _new_current_index)

        if _new_current_index != self._mgr.currentIndex:
            self.setCurrentIndex(_new_current_index)
        else:
            self._mgr.updateTabs()
        self.updateGeometry()

    def count(self) -> int:
        '''
        Returns the number of tabs in this tabbar

        Returns
        -------
        value : int
        '''
        # The tab bar contains a stretch item as last item
        return self._mgr.tabsLayout.count() - 1

    def currentIndex(self) -> int:
        '''
        Returns the current index or -1 if no tab is selected

        Returns
        -------
        value : int
        '''
        return self._mgr.currentIndex

    def currentTab(self) -> Optional['CDockWidgetTab']:
        '''
        Returns the current tab or a nullptr if no tab is selected.

        Returns
        -------
        value : DockWidgetTab
        '''
        if self._mgr.currentIndex < 0:
            return None
        return self._mgr.tabsLayout.itemAt(self._mgr.currentIndex).widget()

    def tab(self, index: int) -> Optional['CDockWidgetTab']:
        '''
        Returns the tab with the given index

        Parameters
        ----------
        index : int

        Returns
        -------
        value : DockWidgetTab
        '''
        if index >= self.count() or index < 0:
            return None

        return self._mgr.tabsLayout.itemAt(index).widget()

    @eventFilterDecorator
    def eventFilter(self, tab: QtCore.QObject, event: QtCore.QEvent) -> bool:
        '''
        Filters the tab widget events

        Parameters
        ----------
        tab : QObject
        event : QEvent

        Returns
        -------
        value : bool
        '''
        _result = super().eventFilter(tab, event)
        if isinstance(tab, CDockWidgetTab):
            if event.type() == QtCore.QEvent.Type.Hide:
                self.sigTabClosed.emit(self._mgr.tabsLayout.indexOf(tab))
                self.updateGeometry()
            elif event.type() == QtCore.QEvent.Type.Show:
                self.sigTabOpened.emit(self._mgr.tabsLayout.indexOf(tab))
                self.updateGeometry()
            elif event.type() == QtCore.QEvent.Type.LayoutRequest:
                self.updateGeometry()

        return _result

    def isTabOpen(self, index: int) -> bool:
        '''
        This function returns true if the tab is open, that means if it is
        visible to the user. If the function returns false, the tab is closed

        Parameters
        ----------
        index : int

        Returns
        -------
        value : bool
        '''
        if index < 0 or index >= self.count():
            return False

        return not self.tab(index).isHidden()

    def setCurrentIndex(self, index: int):
        '''
        This property sets the index of the tab bar's visible tab

        Parameters
        ----------
        index : int
        '''
        if index == self._mgr.currentIndex:
            return
        if index < -1 or index > (self.count() - 1):
            logger.warning('Invalid index %s', index)
            return

        self.sigCurrentChanging.emit(index)
        self._mgr.currentIndex = index
        self._mgr.updateTabs()
        self.sigCurrentChanged.emit(index)

    def closeTab(self, index: int):
        '''
        This function will close the tab given in Index param. Closing a tab
        means, the tab will be hidden, it will not be removed

        Parameters
        ----------
        index : int
        '''
        if index < 0 or index >= self.count():
            return

        _tab = self.tab(index)
        if _tab.isHidden():
            return

        self.sigTabCloseRequested.emit(index)
