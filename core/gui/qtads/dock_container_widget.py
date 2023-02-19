import logging
import typing
from typing import TYPE_CHECKING, List, Dict, Tuple, Optional
from core.gui.qtimp import QtCore, QtGui, QtWidgets

from .util import (findParent, hideEmptyParentSplitters, getQApp, globalGeometry,
                   emitTopLevelEventForWidget, findChild, findChildren)
from .define import (EnumDockWidgetArea, EnumDropMode, EnumDockWidgetFeature, EnumTitleBarButton,
                     EnumDockMgrConfigFlag, DOCK_MANAGER_DEFAULT_CONFIG, AUTO_HIDE_DEFAULT_CONFIG, EnumAutoHideFlag,
                     EnumDockFlags, CDockInsertParam, EnumDockMgrConfigFlag, EnumBitwiseOP, EnumSideBarLocation)
from .auto_hide_tab import CAutoHideTab
from .dock_splitter import CDockSplitter
from .dock_area_widget import CDockAreaWidget
from .auto_hide_dock_container import CAutoHideDockContainer
from .auto_hide_side_bar import CAutoHideSideBar
from .dock_state_reader import CDockStateReader

if TYPE_CHECKING:
    from .dock_manager import CDockManager
    from .dock_widget import CDockWidget
    from .floating_dock_container import CFloatingDockContainer

logger = logging.getLogger(__name__)


def dockAreaInsertParameters(area: EnumDockWidgetArea) -> CDockInsertParam:
    '''
    Returns the insertion parameters for the given dock area

    Parameters
    ----------
    area : DockWidgetArea

    Returns
    -------
    value : DockInsertParam
    '''
    if area == EnumDockWidgetArea.TOP:
        return CDockInsertParam(QtCore.Qt.Orientation.Vertical, False)
    if area == EnumDockWidgetArea.RIGHT:
        return CDockInsertParam(QtCore.Qt.Orientation.Horizontal, True)
    if area in (EnumDockWidgetArea.CENTER,
                EnumDockWidgetArea.BOTTOM):
        return CDockInsertParam(QtCore.Qt.Orientation.Vertical, True)
    if area == EnumDockWidgetArea.LEFT:
        return CDockInsertParam(QtCore.Qt.Orientation.Horizontal, False)

    return CDockInsertParam(QtCore.Qt.Orientation.Vertical, False)


def insertWidgetIntoSplitter(splitter: QtWidgets.QSplitter,
                             widget: QtWidgets.QWidget,
                             append_: bool):
    '''
    Helper function to ease insertion of dock area into splitter

    Parameters
    ----------
    splitter : QSplitter
    widget : QWidget
    append_ : bool
    '''
    if append_:
        splitter.addWidget(widget)
    else:
        splitter.insertWidget(0, widget)


def replace_splitter_widget(splitter: QtWidgets.QSplitter,
                            from_: QtWidgets.QWidget, to: QtWidgets.QWidget):
    '''
    Replace the from widget in the given splitter with the To widget

    Parameters
    ----------
    splitter : QSplitter
    from_ : QWidget
    to : QWidget
    '''
    index = splitter.indexOf(from_)
    from_.setParent(None)
    logger.debug('replace splitter widget %d %s -> %s', index, from_, to)
    splitter.insertWidget(index, to)


def areaIdToIndex(area: EnumDockWidgetArea):
    if EnumDockWidgetArea.LEFT == area:
        return 0
    elif EnumDockWidgetArea.RIGHT == area:
        return 1
    elif EnumDockWidgetArea.TOP == area:
        return 2
    elif EnumDockWidgetArea.BOTTOM == area:
        return 3
    else:
        return 4


class DockContainerWidgetMgr:
    _this: 'CDockContainerWidget'
    dockManager: 'CDockManager'
    zOrderIndex: int
    dockAreas: List[CDockAreaWidget]
    autoHideWidgets: List[CAutoHideDockContainer]
    sideTabBarWidgets: Dict[EnumSideBarLocation, CAutoHideSideBar]
    layout: QtWidgets.QGridLayout
    rootSplitter: CDockSplitter
    isFloating: bool
    lastAddedAreaCache: Dict[EnumDockWidgetArea, CDockAreaWidget]
    visibleDockAreaCount_: int
    topLevelDockArea: CDockAreaWidget
    delayedAutoHideTimer: QtCore.QTimer
    delayedAutoHideTab: CAutoHideTab
    delayedAutoHideShow: bool

    def __init__(self, _this):
        '''
        Private data constructor

        Parameters
        ----------
        _this : DockContainerWidget
        '''
        self._this = _this
        self.dockManager = None
        self.zOrderIndex = 0
        self.dockAreas = []
        self.autoHideWidgets = []
        self.sideTabBarWidgets = dict()
        self.layout = None
        self.rootSplitter = None
        self.isFloating = False
        self.lastAddedAreaCache = {}
        self.visibleDockAreaCount_ = -1
        self.topLevelDockArea = None
        self.delayedAutoHideTimer = QtCore.QTimer()
        self.delayedAutoHideTimer.setSingleShot(True)
        self.delayedAutoHideTimer.setInterval(500)
        self.delayedAutoHideTimer.timeout.connect(self.onTimeOut)
        self.delayedAutoHideTab = None
        self.delayedAutoHideShow = False

    def onTimeOut(self):
        _gp = self.delayedAutoHideTab.mapToGlobal(QtCore.QPoint(0, 0))
        getQApp().sendEvent(self.delayedAutoHideTab, QtGui.QMoveEvent(QtCore.QEvent.Type.MouseButtonPress,
                                                                      QtCore.QPoint(0, 0), _gp, QtCore.Qt.MouseButton.LeftButton,
                                                                      [QtCore.Qt.MouseButton.LeftButton], QtGui.Qt.KeyboardModifier.NoModifier))

    def getDropMode(self, target_pos: QtCore.QPoint):
        _dock_area = self._this.dockAreaAt(target_pos)
        _drop_area = EnumDockWidgetArea.INVALID
        _c_drop_area = self.dockManager.containerOverlay().dropAreaUnderCursor()
        if _dock_area is not None:
            _drop_overlay = self.dockManager.dockAreaOverlay()
            _drop_area = _drop_overlay.showOverlay(_dock_area)
            if _c_drop_area != EnumDockWidgetArea.INVALID and _c_drop_area != _drop_area:
                _drop_area = EnumDockWidgetArea.INVALID
            if _drop_area != EnumDockWidgetArea.INVALID:
                logger.debug('Dock Area Drop Content:%s' % _drop_area)
                return EnumDropMode.DropModeIntoArea
        if EnumDockWidgetArea.INVALID == _drop_area:
            _drop_area = _c_drop_area
            logger.debug('Container Drop Content:%s' % _drop_area)
            if _drop_area != EnumDockWidgetArea.INVALID:
                return EnumDropMode.DropModeIntoContainer
        return EnumDropMode.DropModeInvalid

    def initVisibleDockAreaCount(self):
        if self.visibleDockAreaCount_ > -1:
            return
        self.visibleDockAreaCount_ = 0
        for x in self.dockAreas:
            if x.isHidden():
                self.visibleDockAreaCount_ += 1

    # def dock_widget_into_container(self, area: EnumDockWidgetArea,
    #                                dockwidget: 'DockWidget') -> CDockAreaWidget:
    #     '''
    #     Adds dock widget to container and returns the dock area that contains
    #     the inserted dock widget
    #
    #     Parameters
    #     ----------
    #     area : DockWidgetArea
    #     dockwidget : DockWidget
    #
    #     Returns
    #     -------
    #     value : DockAreaWidget
    #     '''
    #     new_dock_area = CDockAreaWidget(self.dock_manager, self.public)
    #     new_dock_area.add_dock_widget(dockwidget)
    #     self.add_dock_area(new_dock_area, area)
    #     new_dock_area.update_title_bar_visibility()
    #     self.last_added_area_cache[area] = new_dock_area
    #     return new_dock_area

    # def dock_widget_into_dock_area(self, area: EnumDockWidgetArea,
    #                                dock_widget: 'CDockWidget',
    #                                target_dock_area: CDockAreaWidget) -> CDockAreaWidget:
    #     '''
    #     Adds dock widget to a existing DockWidgetArea
    #
    #     Parameters
    #     ----------
    #     area : DockWidgetArea
    #     dockwidget : DockWidget
    #     target_dock_area : DockAreaWidget
    #
    #     Returns
    #     -------
    #     value : DockAreaWidget
    #     '''
    #     if area == EnumDockWidgetArea.CENTER:
    #         target_dock_area.addDockWidget(dock_widget)
    #         return target_dock_area
    #
    #     new_dock_area = CDockAreaWidget(self.dockManager, self._this)
    #     new_dock_area.addDockWidget(dock_widget)
    #
    #     insert_param = dock_area_insert_parameters(area)
    #     target_area_splitter = find_parent(QSplitter, target_dock_area)
    #     index = target_area_splitter.indexOf(target_dock_area)
    #     if target_area_splitter.orientation() == insert_param.orientation:
    #         logger.debug('TargetAreaSplitter.orientation() == insert_orientation')
    #         target_area_splitter.insertWidget(index + insert_param.insert_offset, new_dock_area)
    #     else:
    #         logger.debug('TargetAreaSplitter.orientation() != insert_orientation')
    #         new_splitter = self.new_splitter(insert_param.orientation)
    #         new_splitter.addWidget(target_dock_area)
    #         insert_widget_into_splitter(new_splitter, new_dock_area,
    #                                     insert_param.append)
    #         target_area_splitter.insertWidget(index, new_splitter)
    #
    #     self.append_dock_areas(new_dock_area)
    #     self.emit_dock_areas_added()
    #     return new_dock_area

    def addDockArea(self, new_dock_area: CDockAreaWidget, area: EnumDockWidgetArea):
        '''
        Add dock area to this container

        Parameters
        ----------
        new_dock_area : DockAreaWidget
        area : DockWidgetArea
        '''
        _insert_param = dockAreaInsertParameters(area)

        # As long as we have only one dock area in the splitter we can adjust
        # its orientation
        if len(self.dockAreas) <= 1:
            self.rootSplitter.setOrientation(_insert_param.orientation)

        _splitter = self.rootSplitter
        if _splitter.orientation() == _insert_param.orientation:
            insertWidgetIntoSplitter(_splitter, new_dock_area, _insert_param.append)
            self.updateSplitterHandles(_splitter)
            if _splitter.isHidden():
                _splitter.show()
        else:
            _new_splitter = self.newSplitter(_insert_param.orientation)
            if _insert_param.append:
                self.layout.replaceWidget(_splitter, _new_splitter)
                _new_splitter.addWidget(_splitter)
                _new_splitter.addWidget(new_dock_area)
                self.updateSplitterHandles(_new_splitter)
            else:
                _new_splitter.addWidget(new_dock_area)
                self.layout.replaceWidget(_splitter, _new_splitter)
                _new_splitter.addWidget(_splitter)
                self.updateSplitterHandles(_new_splitter)

            self.rootSplitter = _new_splitter

        self.addDockAreasToList([new_dock_area])

    def dropIntoContainer(self,
                          floating_widget: 'CFloatingDockContainer',
                          area: EnumDockWidgetArea):
        '''
        Drop floating widget into container

        Parameters
        ----------
        floating_widget : FloatingDockContainer
        area : DockWidgetArea
        '''
        _insert_param = dockAreaInsertParameters(area)
        _floating_dock_container = floating_widget.dockContainer()

        _new_dock_areas = _floating_dock_container.findChildren(CDockAreaWidget, '', QtCore.Qt.FindChildOption.FindChildrenRecursively)
        _splitter = self.rootSplitter
        if len(self.dockAreas) <= 1:
            _splitter.setOrientation(_insert_param.orientation)
        elif _splitter.orientation() != _insert_param.orientation:
            _new_splitter = self.newSplitter(_insert_param.orientation)
            _layout_item = self.layout.replaceWidget(_splitter, _new_splitter)
            _new_splitter.addWidget(_splitter)
            self.updateSplitterHandles(_new_splitter)
            _splitter = _new_splitter
            del _layout_item
        # now we can insert the floating widget content into this container
        _f_splitter = _floating_dock_container.rootSplitter()
        if _f_splitter.count() == 1:
            insertWidgetIntoSplitter(_splitter, _f_splitter.widget(0), _insert_param.append)
            self.updateSplitterHandles(_splitter)
        elif _f_splitter.orientation() == _insert_param.orientation:
            _insert_idx = _splitter.count() if _insert_param.append else 0
            while _splitter.count():
                _insert_idx += 1
                _splitter.insertWidget(_insert_idx, _f_splitter.widget(0))
                self.updateSplitterHandles(_splitter)
        else:
            insertWidgetIntoSplitter(_splitter, _f_splitter, _insert_param.append)

        self.rootSplitter = _splitter
        self.addDockAreasToList(_new_dock_areas)
        """
        If we dropped the floating widget into the main dock container that does
        not contain any dock widgets, then splitter is invisible and we need to
        show it to display the docked widgets
        """
        if not _splitter.isVisible():
            _splitter.show()
        self._this.dumpLayout()

    def dropIntoSection(self, floating_widget: 'CFloatingDockContainer',
                        target_area: CDockAreaWidget, area: EnumDockWidgetArea):
        '''
        Drop floating widget into dock area

        Parameters
        ----------
        floating_widget : FloatingDockContainer
        target_area : DockAreaWidget
        area : DockWidgetArea
        '''
        # Dropping into center means all dock widgets in the dropped floating
        # widget will become tabs of the drop area
        if area == EnumDockWidgetArea.CENTER:
            self.dropIntoCenterOfSection(floating_widget, target_area)
            return
        _floating_container = floating_widget.dockContainer()
        _insert_param = dockAreaInsertParameters(area)

        # noinspection PyArgumentList
        _new_dock_areas = findChildren(_floating_container, CDockAreaWidget, '', QtCore.Qt.FindChildOption.FindChildrenRecursively)
        _target_area_splitter = findParent(QtWidgets.QSplitter, target_area)

        if not _target_area_splitter:
            _splitter = self.newSplitter(_insert_param.orientation())
            self.layout.replaceWidget(target_area, _splitter)
            _splitter.addWidget(target_area)
            self.updateSplitterHandles(_splitter)
            _target_area_splitter = _splitter

        _area_index = _target_area_splitter.indexOf(target_area)
        _floating_splitter = _floating_container.rootSplitter()
        if _target_area_splitter.orientation() == _insert_param.orientation:
            _sizes = _target_area_splitter.sizes()
            _target_area_size = (target_area.width()
                                 if _insert_param.orientation == QtCore.Qt.Orientation.Horizontal
                                 else target_area.height()
                                 )
            _adjust_splitter_sizes = True
            if (_floating_splitter.orientation() != _insert_param.orientation
                    and _floating_splitter.count() > 1):
                _target_area_splitter.insertWidget(_area_index + _insert_param.insert_offset,_floating_splitter)
                self.updateSplitterHandles(_target_area_splitter)
            else:
                _adjust_splitter_sizes = (_floating_splitter.count() == 1)
                _insert_index = _area_index + _insert_param.insert_offset
                while _floating_splitter.count():
                    _insert_index+=1
                    _target_area_splitter.insertWidget(_insert_index,_floating_splitter.widget(0))
                    self.updateSplitterHandles(_target_area_splitter)

            if _adjust_splitter_sizes:
                _size = (_target_area_size - _target_area_splitter.handleWidth()) / 2
                _sizes[_area_index] = _size
                _sizes.insert(_area_index, _size)
                _target_area_splitter.setSizes(_sizes)

        else:
            _new_splitter = self.newSplitter(_insert_param.orientation)
            _target_area_size = (target_area.width()
                                 if _insert_param.orientation == QtCore.Qt.Orientation.Horizontal
                                 else target_area.height()
                                 )
            _adjust_splitter_sizes = True
            if (_floating_splitter.orientation() != _insert_param.orientation) and _floating_splitter.count() > 1:
                _new_splitter.addWidget(_floating_splitter)
                self.updateSplitterHandles(_new_splitter)
            else:
                _adjust_splitter_sizes = (_floating_splitter.count() == 1)
                while _floating_splitter.count():
                    _new_splitter.addWidget(_floating_splitter.widget(0))
                    self.updateSplitterHandles(_new_splitter)

            # Save the sizes before insertion and restore it later to prevent
            # shrinking of existing area
            _sizes = _target_area_splitter.sizes()
            insertWidgetIntoSplitter(_new_splitter, target_area, not _insert_param.append)
            if _adjust_splitter_sizes:
                _size = _target_area_size / 2
                _new_splitter.setSizes((_size, _size))

            _target_area_splitter.insertWidget(_area_index, _new_splitter)
            _target_area_splitter.setSizes(_sizes)
            self.updateSplitterHandles(_target_area_splitter)

        logger.debug('Deleting floating_widget %s', floating_widget)
        self.addDockAreasToList(_new_dock_areas)
        self._this.dumpLayout()

    def moveToContainer(self, widget: QtWidgets.QWidget, area: EnumDockWidgetArea):
        from . import CDockWidget
        if isinstance(widget, CDockWidget):
            _new_dock_area = CDockAreaWidget(self.dockManager, self._this)
            _old_dock_area = widget.dockAreaWidget()
            if _old_dock_area is not None:
                _old_dock_area.removeDockWidget(widget)
            _new_dock_area.addDockWidget(widget)
        else:
            """
            We check, if we insert the dropped widget into the same place that
            it already has and do nothing, if it is the same place. It would
		    also work without this check, but it looks nicer with the check
		    because there will be no layout updates
            """
            _splitter = findParent(CDockSplitter, widget)
            _insert_param = dockAreaInsertParameters(area)
            if _splitter is self.rootSplitter and _insert_param.orientation == _splitter.orientation():
                if _insert_param.append and _splitter.lastWidget() is widget:
                    return
                elif not _insert_param.append and _splitter.firstWidget() is widget:
                    return
            widget.dockContainer().removeDockArea(widget)
            _new_dock_area = widget
        self.addDockArea(_new_dock_area, area)
        self.lastAddedAreaCache[areaIdToIndex(area)] = _new_dock_area

    def moveIntoCenterOfSection(self, widget: QtWidgets.QWidget, target_area: CDockAreaWidget):
        from . import CDockWidget
        if isinstance(widget, CDockWidget):
            _old_da = widget.dockAreaWidget()
            if _old_da is None:
                logger.error('no dockAreaWidget found')
                return
            if _old_da is target_area:
                return
            if _old_da is not None:
                _old_da.removeDockWidget(widget)
            target_area.insertDockWidget(0, widget, True)
        else:
            _new_dws = widget.dockWidgets()
            if not _new_dws:
                return
            _new_idx = widget.currentIndex()
            for i, x in enumerate(_new_dws):
                target_area.insertDockWidget(i, x, False)
            target_area.setCurrentIndex(_new_idx)
            widget.dockContainer().removeDockArea(widget)
            widget.deleteLater()
        target_area.updateTitleBarVisibility()

    def moveToNewSection(self, widget: QtWidgets.QWidget, target_area: CDockAreaWidget, area: EnumDockWidgetArea):
        if EnumDockWidgetArea.CENTER == area:
            self.moveIntoCenterOfSection(widget, target_area)
            return
        from . import CDockWidget
        if isinstance(widget, CDockWidget):
            _new_dock_area = CDockAreaWidget(self.dockManager, self._this)
            _old_dock_area = widget.dockAreaWidget()
            if _old_dock_area is not None:
                _old_dock_area.removeDockWidget(widget)
            _new_dock_area.addDockWidget(widget)
        else:
            widget.dockContainer().removeDockArea(widget)
            _new_dock_area = widget
        _insert_param = dockAreaInsertParameters(area)
        _target_area_splitter = findParent(QtWidgets.QSplitter, target_area)
        _area_idx = _target_area_splitter.indexOf(target_area)
        _sizes = _target_area_splitter.sizes()
        if _target_area_splitter.orientation() == _insert_param.orientation:
            _target_area_size = target_area.width() if _insert_param.orientation == QtCore.Qt.Orientation.Horizontal else target_area.height()
            _target_area_splitter.insertWidget(_area_idx + _insert_param.insert_offset, _new_dock_area)
            self.updateSplitterHandles(_target_area_splitter)
            _size = (_target_area_size - _target_area_splitter.handleWidth()) / 2
            _sizes[_area_idx] = _size
            _sizes.insert(_area_idx, _size)
        else:
            _target_area_size = target_area.width() if _insert_param.orientation == QtCore.Qt.Orientation.Horizontal else target_area.height()
            _new_splitter = self.newSplitter(_insert_param.orientation)
            _new_splitter.addWidget(target_area)
            insertWidgetIntoSplitter(_new_splitter, _new_dock_area, _insert_param.append)
            self.updateSplitterHandles(_new_splitter)
            _size = _target_area_size / 2
            _new_splitter.setSizes([_size, _size])
            _target_area_splitter.insertWidget(_area_idx, _new_splitter)
            self.updateSplitterHandles(_target_area_splitter)
        _target_area_splitter.setSizes(_sizes)
        self.addDockAreasToList([_new_dock_area])

    def dropIntoCenterOfSection(self, floating_widget: 'CFloatingDockContainer',
                                target_area: CDockAreaWidget):
        '''
        Creates a new tab for a widget dropped into the center of a section

        Parameters
        ----------
        floating_widget : FloatingDockContainer
        target_area : DockAreaWidget
        '''
        _floating_container = floating_widget.dockContainer()
        _new_dock_widgets = _floating_container.dockWidgets()
        _top_level_dock_area = _floating_container.topLevelDockArea()
        _new_current_index = -1

        # If the floating widget contains only one single dock are, then the
        # current dock widget of the dock area will also be the future current
        # dock widget in the drop area.
        if _top_level_dock_area is not None:
            _new_current_index = _top_level_dock_area.currentIndex()

        for i, dock_widget in enumerate(_new_dock_widgets):
            target_area.insertDockWidget(i, dock_widget, False)

            # If the floating widget contains multiple visible dock areas, then we
            # simply pick the first visible open dock widget and make it
            # the current one.
            if _new_current_index < 0 and not dock_widget.isClosed():
                _new_current_index = i

        target_area.setCurrentIndex(_new_current_index)
        target_area.updateTitleBarVisibility()

    def addDockAreasToList(self, new_dock_areas: list):
        '''
        Adds new dock areas to the internal dock area list

        Parameters
        ----------
        new_dock_areas : list
        '''
        _count_before = len(self.dockAreas)
        _new_area_count = len(new_dock_areas)
        self.appendDockAreas(*new_dock_areas)

        # If the user dropped a floating widget that contains only one single
        # visible dock area, then its title bar button EnumTitleBarButtonUndock is
        # likely hidden. We need to ensure, that it is visible
        for dock_area in new_dock_areas:
            _undock = dock_area.titleBarButton(EnumTitleBarButton.AUTO_HIDE)
            _undock.setVisible(True)
            _close = dock_area.titleBarButton(EnumTitleBarButton.CLOSE)
            _close.setVisible(True)

        # We need to ensure, that the dock area title bar is visible. The title bar
        # is invisible, if the dock are is a single dock area in a floating widget.
        if _count_before == 1:
            self.dockAreas[0].updateTitleBarVisibility()
        if _new_area_count == 1:
            self.dockAreas[-1].updateTitleBarVisibility()

        self.emitDockAreasAdded()

    def addDockWidgetToContainer(self, area: EnumDockWidgetArea, widget: QtWidgets.QWidget):
        _new_dock_area = CDockAreaWidget(self.dockManager, self._this)
        _new_dock_area.addDockWidget(widget)
        self.addDockArea(_new_dock_area, area)
        _new_dock_area.updateTitleBarVisibility()
        self.lastAddedAreaCache[areaIdToIndex(int(area))] = _new_dock_area
        return _new_dock_area

    def addDockWidgetToDockArea(self, area: EnumDockWidgetArea, dock_widget: 'CDockWidget', target_area: 'CDockAreaWidget', idx: int = -1):
        if EnumDockWidgetArea.CENTER == area:
            target_area.insertDockWidget(idx, dock_widget)
            target_area.updateTitleBarVisibility()
            return target_area
        _new_dock_area = CDockAreaWidget(self.dockManager, self._this)
        _new_dock_area.addDockWidget(dock_widget)
        _insert_param = dockAreaInsertParameters(area)
        _target_area_splitter = findParent(QtWidgets.QSplitter, target_area)
        _idx = _target_area_splitter.indexOf(target_area)
        _is_equal_split_cfg = EnumDockMgrConfigFlag.EqualSplitOnInsertion in DOCK_MANAGER_DEFAULT_CONFIG
        if _target_area_splitter.orientation == _insert_param.orientation:
            logger.debug('TargetAreaSplitter->orientation() == InsertParam.orientation()')
            _target_area_splitter.insertWidget(idx + _insert_param.insert_offset(), _new_dock_area)
            self.updateSplitterHandles(_target_area_splitter)
            if _is_equal_split_cfg:
                self.adjustSplitterSizesOnInsertion(_target_area_splitter)
        else:
            logger.debug('TargetAreaSplitter->orientation() !== InsertParam.orientation()')
            _target_area_sizes = _target_area_splitter.sizes()
            _new_splitter = self.newSplitter(_insert_param.orientation)
            _new_splitter.addWidget(target_area)
            insertWidgetIntoSplitter(_new_splitter, _new_dock_area, _insert_param.append)
            self.updateSplitterHandles(_new_splitter)
            _target_area_splitter.insertWidget(idx, _new_splitter)
            self.updateSplitterHandles(_target_area_splitter)
            if _is_equal_split_cfg:
                _target_area_splitter.setSizes(_target_area_sizes)
                self.adjustSplitterSizesOnInsertion(_target_area_splitter)
        self.addDockAreasToList([_new_dock_area])
        return _new_dock_area

    def appendDockAreas(self, *new_dock_areas):
        '''
        Wrapper function for DockAreas append, that ensures that dock area
        signals are properly connected to dock container slots

        Parameters
        ----------
        *new_dock_areas : DockAreaWidget
        '''
        self.dockAreas.extend(new_dock_areas)
        for dock_area in new_dock_areas:
            dock_area.sigViewToggled.connect(self.onDockAreaViewToggled)

    def saveChildNodesState(self, stream: QtCore.QXmlStreamWriter, widget: QtWidgets.QWidget):
        '''
        Save state of child nodes

        Parameters
        ----------
        stream : QXmlStreamWriter
        widget : QWidget
        '''
        if isinstance(widget, QtWidgets.QSplitter):
            _splitter = widget
            stream.writeStartElement("Splitter")
            _orientation = ('|' if _splitter.orientation() == QtCore.Qt.Orientation.Horizontal
                            else '-')
            stream.writeAttribute("Orientation", _orientation)
            stream.writeAttribute("Count", str(_splitter.count()))
            logger.debug('NodeSplitter orient: %s WidgetCount: %s',
                         _orientation, _splitter.count())

            for i in range(_splitter.count()):
                self.saveChildNodesState(stream, _splitter.widget(i))

            stream.writeStartElement("Sizes")
            for size in _splitter.sizes():
                stream.writeCharacters(str(size) + " ")

            stream.writeEndElement()
            stream.writeEndElement()
        elif isinstance(widget, CDockAreaWidget):
            widget.saveState(stream)

    def saveAutoHideWidgetsState(self, stream: QtCore.QXmlStreamWriter):
        for x in self.sideTabBarWidgets.values():
            if not x.tabCount():
                continue
            x.saveState(stream)

    def restoreChildNodes(self, stream: CDockStateReader,
                          testing: bool) -> Tuple[bool, Optional[QtWidgets.QWidget]]:
        '''
        Restore state of child nodes.

        Parameters
        ----------
        stream : QXmlStreamReader
        testing : bool

        Returns
        -------
        value : bool
        widget : QWidget
        '''
        _result = True
        _widget = None
        while stream.readNextStartElement():
            if stream.name() == "Splitter":
                _result, _widget = self.restoreSplitter(stream, testing)
                logger.debug('restore splitter %s %s; testing: %s', _result, _widget, testing)
            elif stream.name() == "Area":
                _result, _widget = self.restoreDockArea(stream, testing)
                logger.debug('restore Area %s %s; testing: %s', _result, _widget, testing)
            elif stream.name() == "SideBar":
                _result = self.restoreSideBar(stream, testing)
                logger.debug('SideBar %s %s; testing: %s', _result, _widget, testing)
            else:
                stream.skipCurrentElement()
            logger.debug('restored child node %s: %s', stream.name(), _widget)

        return _result, _widget

    def restoreSideBar(self, stream: CDockStateReader, testing):
        if EnumAutoHideFlag.AutoHideFeatureEnabled not in AUTO_HIDE_DEFAULT_CONFIG:
            return True
        _area = stream.attributes().value('Area')
        if not _area:
            return False
        else:
            _area = EnumSideBarLocation(int(_area))
        while stream.readNextStartElement():
            if stream.name() != 'Widget':
                continue
            _name = stream.attributes().value('Name')
            if not _name:
                return False
            _close = stream.attributes().value('Closed')
            if not _close:
                return False
            else:
                _close = int(_close)
            _size = stream.attributes().value('Size')
            if not _size:
                return False
            else:
                _size = int(_size)
            stream.skipCurrentElement()
            _dw = self.dockManager.findDockWidget(_name)
            if _dw is None or testing:
                continue
            _sb = self._this.sideTabBar(_area)
            if _dw.isAutoHide():
                _ac = _dw.autoHideDockContainer()
                if _ac.sideBar() is not _sb:
                    _sb.addAutoHideWidget(_ac)
            else:
                _ac = _sb.insertDockWidget(-1, _dw)
            _ac.setSize(_size)
            _dw.setProperty('close', _close)
            _dw.setProperty('dirty', False)
        return True

    def restoreSplitter(self, stream: CDockStateReader, testing: bool
                        ) -> Tuple[bool, Optional[QtWidgets.QWidget]]:
        '''
        Restores a splitter.

        Parameters
        ----------
        stream : QXmlStreamReader
        created_widget : QWidget
        testing : bool

        Returns
        -------
        value : bool
        widget : QWidget
        '''
        _orientation_str = stream.attributes().value("Orientation")
        if _orientation_str.startswith("|"):
            _orientation = QtCore.Qt.Orientation.Horizontal
        elif _orientation_str.startswith("-"):
            _orientation = QtCore.Qt.Orientation.Vertical
        else:
            return False, None
        _is_h_splitter = _orientation_str.startswith('|')
        if stream.fileVersion() == 0:
            _is_h_splitter = not _is_h_splitter

        _widget_count = stream.attributes().value("Count")
        if not _widget_count:
            return False, None
        else:
            _widget_count = int(_widget_count)

        logger.debug('Restore NodeSplitter Orientation: %s  WidgetCount: %s',
                     _orientation, _widget_count)

        _splitter = (None if testing else self.newSplitter(_orientation))
        _visible = False
        _sizes = []

        while stream.readNextStartElement():
            _child_node = None
            _result = True
            if stream.name() == "Splitter":
                _result, _child_node = self.restoreSplitter(stream, testing)
                if not _result:
                    return False, None
            elif stream.name() == "Area":
                _result, _child_node = self.restoreDockArea(stream, testing)
                if not _result:
                    return False, None
            elif stream.name() == "Sizes":
                _s_sizes = stream.readElementText().strip()
                _sizes = [int(sz) for sz in _s_sizes.split(' ')]
                logger.debug('restoreSplitter Sizes: %s (from s_sizes: %s)', _sizes, _s_sizes)
            else:
                stream.skipCurrentElement()
            if not _result:
                return False, None
            if testing or _child_node is None:
                continue
            logger.debug('restoreSplitter ChildNode isVisible %s isVisibleTo %s',
                         _child_node.isVisible(),
                         _child_node.isVisibleTo(_splitter))
            _splitter.addWidget(_child_node)
            _visible |= _child_node.isVisibleTo(_splitter)
        if not testing:
            self.updateSplitterHandles(_splitter)
        if len(_sizes) != _widget_count:
            return False, None

        if testing:
            _splitter = None
        else:
            if not _splitter.count():
                _splitter.deleteLater()
                _splitter = None
            else:
                _splitter.setSizes(_sizes)
                _splitter.setVisible(_visible)

        return True, _splitter

    def restoreDockArea(self, stream: CDockStateReader, testing: bool) -> Tuple[bool, QtWidgets.QWidget]:
        '''
        Restores a dock area.

        Parameters
        ----------
        stream : QXmlStreamReader
        testing : bool

        Returns
        -------
        value : bool
        widget : QWidget
        '''
        # modified: fix this function, python can not overwrite the reference of argument
        #       maybe use a list for dock_area then pop the first.
        _da = None
        _result, _da = CDockAreaWidget.restoreState(stream, testing, self._this)
        if _result and _da is not None:
            self.appendDockAreas(_da)
        return _result, _da

    def dumpRecursive(self, level: int, widget: QtWidgets.QWidget):
        '''
        Helper function for recursive dumping of layout

        Parameters
        ----------
        level : int
        widget : QWidget
        '''
        _indent = ' ' * level * 4
        if isinstance(widget, QtWidgets.QSplitter):
            _splitter = widget
            logger.debug(
                "%sSplitter %s v: %s c: %s",
                _indent,
                ('--' if _splitter.orientation() == QtCore.Qt.Orientation.Vertical else '|'),
                ('h' if _splitter.isHidden() else 'v'),
                _splitter.count()
            )

            for i in range(_splitter.count()):
                self.dumpRecursive(level + 1, _splitter.widget(i))
        elif isinstance(widget, CDockAreaWidget):
            _dock_area = widget
            logger.debug('%sDockArea', _indent)
            logger.debug('%s%s %s DockArea',
                         _indent,
                         'h' if _dock_area.isHidden() else 'v',
                         ' ' if _dock_area.openDockWidgetsCount() > 0 else 'c',
                         )

            _indent = ' ' * (level + 1) * 4
            for i, dock_widget in enumerate(_dock_area.dockWidgets()):
                logger.debug('%s%s%s%s %s', _indent,
                             '*' if i == _dock_area.currentIndex() else ' ',
                             'h' if i == dock_widget.isHidden() else 'v',
                             'c' if i == dock_widget.isClosed() else ' ',
                             dock_widget.windowTitle()
                             )

    def visibleDockAreaCount(self) -> int:
        '''
        Access function for the visible dock area counter

        Returns
        -------
        value : int
        '''
        # Lazy initialisation - we initialize the VisibleDockAreaCount variable
        # on first use
        self.initVisibleDockAreaCount()
        return self.visibleDockAreaCount_

    def onVisibleDockAreaCountChanged(self):
        '''
        The visible dock area count changes, if dock areas are remove, added or when its view is toggled
        '''
        _top_level_dock_area = self._this.topLevelDockArea()
        if _top_level_dock_area is not None:
            self.topLevelDockArea = _top_level_dock_area
            _top_level_dock_area.updateTitleBarButtonVisibility(True)

        elif self.topLevelDockArea:
            self.topLevelDockArea.updateTitleBarButtonVisibility(False)
            self.topLevelDockArea = None

    def emitDockAreasRemoved(self):
        self.onVisibleDockAreaCountChanged()
        self._this.sigDockAreasRemoved.emit()

    def emitDockAreasAdded(self):
        self.onVisibleDockAreaCountChanged()
        self._this.sigDockAreasAdded.emit()

    def newSplitter(self, orientation: QtCore.Qt.Orientation,
                    parent: QtWidgets.QWidget = None) -> CDockSplitter:
        '''
        Helper function for creation of new splitter

        Parameters
        ----------
        orientation : Qt.Orientation
        parent : QWidget, optional

        Returns
        -------
        value : DockSplitter
        '''
        _splitter = CDockSplitter(orientation, parent)
        _opaque_resize = EnumDockMgrConfigFlag.OpaqueSplitterResize in DOCK_MANAGER_DEFAULT_CONFIG
        _splitter.setOpaqueResize(_opaque_resize)
        _splitter.setChildrenCollapsible(False)
        return _splitter

    def adjustSplitterSizesOnInsertion(self, splitter: QtWidgets.QSplitter,
                                       last_ratio: float = 1.0):
        _area_size = splitter.width() if splitter.orientation() == QtCore.Qt.Orientation.Horizontal else splitter.height()
        _splitter_sizes = splitter.sizes()
        _tot_ratio = _splitter_sizes.size() - 1.0 + last_ratio
        for i in range(len(_splitter_sizes) - 1):
            _splitter_sizes[i] = _area_size / _tot_ratio
        _splitter_sizes[-1] = _area_size * last_ratio / _tot_ratio
        splitter.setSizes(_splitter_sizes)

    def updateSplitterHandles(self, splitter: QtWidgets.QSplitter):
        if self.dockManager.centralWidget() is None or splitter is None:
            return
        for i in range(splitter.count()):
            splitter.setStretchFactor(i, 1 if self.widgetResizesWithContainer(splitter.widget(i)) else 0)

    def widgetResizesWithContainer(self, widget: QtWidgets.QWidget):
        if self.dockManager.centralWidget() is None:
            return True
        if isinstance(widget, CDockAreaWidget):
            return widget.isCentralWidgetArea()
        if isinstance(widget, CDockSplitter):
            return widget.isResizingWithContainer()
        return False

    def onDockAreaViewToggled(self, visible: bool):
        '''
        On dock area view toggled

        Parameters
        ----------
        visible : bool
        '''
        try:
            _dock_area = self._this.sender()
        except RuntimeError:
            logger.exception('qtpydocking bug')
            return

        self.visibleDockAreaCount_ += 1 if visible else -1
        self.onVisibleDockAreaCountChanged()
        self._this.sigDockAreaViewToggled.emit(_dock_area, visible)


class CDockContainerWidget(QtWidgets.QFrame):
    # This signal is emitted if one or multiple dock areas has been added to
    # the internal list of dock areas. If multiple dock areas are inserted,
    # this signal is emitted only once
    sigDockAreasAdded = QtCore.Signal()

    # This signal is emitted if one or multiple dock areas has been removed
    sigDockAreasRemoved = QtCore.Signal()

    # This signal is emitted if a dock area is opened or closed via
    # toggleView() function
    sigDockAreaViewToggled = QtCore.Signal(CDockAreaWidget, bool)
    sigAutoHideWidgetCreated = QtCore.Signal(CAutoHideDockContainer)
    Z_ORDER_COUNTER = 0

    def __init__(self, dock_manager: 'CDockManager', parent: QtWidgets.QWidget):
        '''

        Parameters
        ----------
        dock_manager : DockManager
        parent : QWidget
        '''

        super().__init__(parent)
        self._mgr = DockContainerWidgetMgr(self)
        self._mgr.dockManager = dock_manager
        self._mgr.isFloating = self.floatingWidget() is not None
        self._mgr.layout = QtWidgets.QGridLayout()
        self._mgr.layout.setContentsMargins(0, 0, 0, 0)
        self._mgr.layout.setSpacing(0)
        self._mgr.layout.setColumnStretch(1, 1)
        self._mgr.layout.setRowStretch(1, 1)
        self.setLayout(self._mgr.layout)

        # The function d.new_splitter() accesses the config flags from dock
        # manager which in turn requires a properly constructed dock manager.
        # If this dock container is the dock manager, then it is not properly
        # constructed yet because this base class constructor is called before
        # the constructor of the DockManager private class
        if dock_manager is not self:
            self._mgr.dockManager.registerDockContainer(self)
            self.createRootSplitter()
            self.createSideTabBarWidgets()

    def __repr__(self):
        return f'<{self.__class__.__name__} is_floating={self._mgr.isFloating}>'

    def deleteLater(self):
        if self._mgr.dockManager:
            self._mgr.dockManager.removeDockContainer(self)

        super().deleteLater()

    def autoHideWidgets(self):
        return self._mgr.autoHideWidgets

    def event(self, e: QtCore.QEvent) -> bool:
        '''
        Handles activation events to update zOrderIndex

        Parameters
        ----------
        e : QEvent

        Returns
        -------
        value : bool
        '''
        _result = super().event(e)
        if e.type() == QtCore.QEvent.Type.WindowActivate:
            self.Z_ORDER_COUNTER += 1
            self._mgr.zOrderIndex = self.Z_ORDER_COUNTER
        elif e.type() == QtCore.QEvent.Type.Show and not self._mgr.zOrderIndex:
            self.Z_ORDER_COUNTER += 1
            self._mgr.zOrderIndex = self.Z_ORDER_COUNTER
        return _result

    def rootSplitter(self) -> QtWidgets.QSplitter:
        '''
        Access function for the internal root splitter

        Returns
        -------
        value : QSplitter
        '''
        return self._mgr.rootSplitter

    def createRootSplitter(self):
        '''
        Helper function for creation of the root splitter
        '''
        if self._mgr.rootSplitter:
            return

        self._mgr.rootSplitter = self._mgr.newSplitter(QtCore.Qt.Orientation.Horizontal)
        self._mgr.layout.addWidget(self._mgr.rootSplitter, 1, 1)

    def createSideTabBarWidgets(self):
        if EnumAutoHideFlag.AutoHideFeatureEnabled not in AUTO_HIDE_DEFAULT_CONFIG:
            return
        _area = EnumSideBarLocation.LEFT
        self._mgr.sideTabBarWidgets[_area] = CAutoHideSideBar(self, _area)
        self._mgr.layout.addWidget(self._mgr.sideTabBarWidgets[_area], 1, 0)

        _area = EnumSideBarLocation.RIGHT
        self._mgr.sideTabBarWidgets[_area] = CAutoHideSideBar(self, _area)
        self._mgr.layout.addWidget(self._mgr.sideTabBarWidgets[_area], 1, 2)

        _area = EnumSideBarLocation.BOTTOM
        self._mgr.sideTabBarWidgets[_area] = CAutoHideSideBar(self, _area)
        self._mgr.layout.addWidget(self._mgr.sideTabBarWidgets[_area], 2, 1)

        _area = EnumSideBarLocation.TOP
        self._mgr.sideTabBarWidgets[_area] = CAutoHideSideBar(self, _area)
        self._mgr.layout.addWidget(self._mgr.sideTabBarWidgets[_area], 0, 1)

    def createAndSetupAutoHideContainer(self, location: EnumSideBarLocation, dock_widget: 'CDockWidget'):
        if EnumAutoHideFlag.AutoHideFeatureEnabled not in AUTO_HIDE_DEFAULT_CONFIG:
            return
        if self._mgr.dockManager is not dock_widget.dockManager():
            dock_widget.setDockManager(self._mgr.dockManager)
        return self.sideTabBar(location).insertDockWidget(-1, dock_widget)

    def contentRectGlobal(self):
        if self._mgr.rootSplitter is None:
            return QtCore.QRect()
        return globalGeometry(self._mgr.rootSplitter)

    def contentRect(self):
        if self._mgr.rootSplitter is None:
            return QtCore.QRect()
        return self._mgr.rootSplitter.geometry()

    def dropFloatingWidget(self,
                           floating_widget: 'CFloatingDockContainer',
                           target_pos: QtCore.QPoint):
        '''
        Drop floating widget into the container

        Parameters
        ----------
        floating_widget : FloatingDockContainer
        target_pos : QPoint
        '''
        logger.debug('DockContainerWidget.dropFloatingWidget')
        _single_drop_dock_w = floating_widget.topLevelDockWidget()
        _single_dock_w = self.topLevelDockWidget()
        _dock_area = self.dockAreaAt(target_pos)
        _area_to_drop = EnumDockWidgetArea.INVALID
        _container_drop_area = self._mgr.dockManager.containerOverlay().dropAreaUnderCursor()
        _dropped = False

        # floating_top_level_dock_widget = floating_widget.top_level_dock_widget()
        # top_level_dock_widget = self.top_level_dock_widget()

        if _dock_area is not None:
            _drop_overlay = self._mgr.dockManager.dockAreaOverlay()
            _drop_overlay.setAllowedAreas(_dock_area.allowedAreas())
            _area_to_drop = _drop_overlay.showOverlay(_dock_area)
            if (_container_drop_area not in (
                    EnumDockWidgetArea.INVALID, _area_to_drop)):
                _area_to_drop = EnumDockWidgetArea.INVALID

            if _area_to_drop != EnumDockWidgetArea.INVALID:
                logger.debug('Dock Area Drop Content: %s', _area_to_drop)
                self._mgr.dropIntoSection(floating_widget, _dock_area, _area_to_drop)
                _dropped = True

        # mouse is over container
        if EnumDockWidgetArea.INVALID == _area_to_drop:
            _area_to_drop = _container_drop_area
            logger.debug('Container Drop Content: %s', _area_to_drop)
            if _area_to_drop != EnumDockWidgetArea.INVALID:
                self._mgr.dropIntoContainer(floating_widget, _area_to_drop)
                _dropped = True
        # Remove the auto hide widgets from the FloatingWidget and insert
        # them into this widget
        for x in floating_widget.dockContainer().autoHideWidgets():
            _side_bar = self.sideTabBar(x.sideBarLocation())
            _side_bar.addAutoHideWidget(x)
        if _dropped:
            # Fix https: // github.com / githubuser0xFFFF / Qt - Advanced - Docking - System / issues / 351
            floating_widget.hideAndDeleteLater()
            # If we dropped a floating widget with only one single dock widget, then we
            # drop a top level widget that changes from floating to docked now
            emitTopLevelEventForWidget(_single_drop_dock_w, False)
            # If there was a top level widget before the drop, then it is not top
            # level widget anymore
            emitTopLevelEventForWidget(_single_dock_w, False)
        self.window().activateWindow()
        if _single_drop_dock_w is not None:
            self._mgr.dockManager.notifyWidgetOrAreaRelocation(_single_drop_dock_w)
        self._mgr.dockManager.notifyFloatingWidgetDrop(floating_widget)

    def dropWidget(self, widget: QtWidgets.QWidget, area: EnumDockWidgetArea, target_widget: CDockAreaWidget):
        _singe_dock_w = self.topLevelDockWidget()
        if target_widget is not None:
            self._mgr.moveToNewSection(widget, target_widget, area)
        else:
            self._mgr.moveToContainer(widget, area)
        # If there was a top level widget before the drop, then it is not top
        # level widget anymore
        emitTopLevelEventForWidget(_singe_dock_w, False)
        self.window().activateWindow()
        self._mgr.dockManager.notifyWidgetOrAreaRelocation(widget)

    def addDockArea(self, dock_area_widget: CDockAreaWidget,
                    area: EnumDockWidgetArea = EnumDockWidgetArea.CENTER):
        '''
        Adds the given dock area to this container widget

        Parameters
        ----------
        dock_area_widget : DockAreaWidget
        area : DockWidgetArea
        '''
        _container = dock_area_widget.dockContainer()
        if _container and _container is not self:
            _container.removeDockArea(dock_area_widget)

        self._mgr.addDockArea(dock_area_widget, area)

    def removeDockArea(self, area_widget: CDockAreaWidget):
        '''
        Removes the given dock area from this container

        Parameters
        ----------
        area_widget : DockAreaWidget
        '''

        def emit_and_exit():
            _top_level_widget = self.topLevelDockWidget()

            # Updated the title bar visibility of the dock widget if there is only
            # one single visible dock widget
            emitTopLevelEventForWidget(_top_level_widget, True)
            self.dumpLayout()
            self._mgr.emitDockAreasRemoved()

        logger.debug('DockContainerWidget.removeDockArea')
        if area_widget.isAutoHide():
            area_widget.setAutoHideDockContainer(None)
            return
        area_widget.disconnect(self)
        # disconnect
        # modified:
        area_widget.sigViewToggled.disconnect(self._mgr.onDockAreaViewToggled)
        self._mgr.dockAreas.remove(area_widget)
        _splitter = findParent(CDockSplitter, area_widget)
        """
        Remove are from parent splitter and recursively hide tree of parent
	    splitters if it has no visible content
        """
        area_widget.setParent(None)
        hideEmptyParentSplitters(_splitter)

        # Remove this area from cached areas
        _k_to_remove = None
        for k, v in self._mgr.lastAddedAreaCache.items():
            if v is area_widget:
                _k_to_remove = k
        if _k_to_remove is not None:
            self._mgr.lastAddedAreaCache.pop(_k_to_remove)
        # If splitter has more than 1 widgets, we are finished and can leave
        if _splitter.count() > 1:
            return emit_and_exit()
        # If this is the RootSplitter we need to remove empty splitters to
        # avoid too many empty splitters
        if _splitter is self._mgr.rootSplitter:
            logger.debug('Removed from RootSplitter')
            if not _splitter.count():
                _splitter.hide()
                return emit_and_exit()
            _widget = _splitter.widget(0)
            if not isinstance(_widget, QtWidgets.QSplitter):
                # If the one and only content widget of the splitter is not a splitter
                # then we are finished
                return emit_and_exit()
            # We replace the superfluous RootSplitter with the ChildSplitter
            _widget.setParent(None)
            self._mgr.layout.replaceWidget(_splitter, _widget)
            self._mgr.rootSplitter = _widget
            logger.debug('RootSplitter replaced by child splitter')
        elif _splitter.count() == 1:
            logger.debug('Replacing splitter with content')
            _parent_splitter = findParent(QtWidgets.QSplitter, _splitter)
            _sizes = _parent_splitter.sizes()
            _widget = _splitter.widget(0)
            _widget.setParent(self)
            replace_splitter_widget(_parent_splitter, _splitter, _widget)
            _parent_splitter.setSizes(_sizes)
        _splitter.deleteLater()

    def removeAutoHideWidget(self, auto_hide_widget: CAutoHideDockContainer):
        # todo: add exception handler
        self._mgr.autoHideWidgets.remove(auto_hide_widget)

    def saveState(self, stream: QtCore.QXmlStreamWriter):
        '''
        Saves the state into the given stream

        Parameters
        ----------
        stream : QXmlStreamWriter
        '''
        logger.debug('DockContainerWidget.saveState isFloating %s',
                     self.isFloating())
        stream.writeStartElement("Container")
        stream.writeAttribute("Floating", '1' if self.isFloating() else '0')
        if self.isFloating():
            _floating_widget = self.floatingWidget()
            _geometry = _floating_widget.saveGeometry()
            stream.writeTextElement("Geometry", bytes(_geometry.toBase64()).decode('utf-8'))
        self._mgr.saveChildNodesState(stream, self._mgr.rootSplitter)
        self._mgr.saveAutoHideWidgetsState(stream)
        stream.writeEndElement()

    def restoreState(self, stream: CDockStateReader, testing: bool = False) -> bool:
        '''
        Restores the state from given stream.

        Parameters
        ----------
        stream : QXmlStreamReader
        testing : bool
            If Testing is true, the function only parses the data from the
            given stream but does not restore anything. You can use this check
            for faulty files before you start restoring the state

        Returns
        -------
        value : bool
        '''
        _is_floating = bool(int(stream.attributes().value("Floating")))
        logger.debug('Restore DockContainerWidget Floating %s', _is_floating)

        if not testing:
            self._mgr.visibleDockAreaCount_ = -1

            # invalidate the dock area count and clear the area cache
            self._mgr.dockAreas.clear()
            self._mgr.lastAddedAreaCache.clear()

        if _is_floating:
            logger.debug('Restore floating widget')
            if not stream.readNextStartElement() or stream.name() != "Geometry":
                return False

            _geometry_string = stream.readElementText(
                CDockStateReader.ReadElementTextBehaviour.ErrorOnUnexpectedElement)
            _geometry = QtCore.QByteArray.fromBase64(_geometry_string.encode('utf-8'))
            if _geometry.isEmpty():
                return False

            if not testing:
                _floating_widget = self.floatingWidget()
                _floating_widget.restoreGeometry(_geometry)

        _res, _new_root_splitter = self._mgr.restoreChildNodes(stream, testing)
        if not _res:
            return False

        if testing:
            return True

        # If the root splitter is empty, rostoreChildNodes returns a 0 pointer
        # and we need to create a new empty root splitter
        if not _new_root_splitter:
            _new_root_splitter = self._mgr.newSplitter(QtCore.Qt.Orientation.Horizontal)

        self._mgr.layout.replaceWidget(self._mgr.rootSplitter, _new_root_splitter)
        _old_root = self._mgr.rootSplitter
        self._mgr.rootSplitter = _new_root_splitter
        _old_root.deleteLater()
        return True

    def registerAutoHideWidget(self, auto_hide_widget: CAutoHideDockContainer):
        self._mgr.autoHideWidgets.append(auto_hide_widget)
        self.sigAutoHideWidgetCreated.emit(auto_hide_widget)
        logger.debug('mgr->AutoHideWidgets.count() %s' % len(self._mgr.autoHideWidgets))

    def lastAddedDockAreaWidget(self, area: EnumDockWidgetArea) -> CDockAreaWidget:
        '''
        This function returns the last added dock area widget for the given
        area identifier or 0 if no dock area widget has been added for the
        given area

        Parameters
        ----------
        area : DockWidgetArea

        Returns
        -------
        value : DockAreaWidget
        '''
        return self._mgr.lastAddedAreaCache.get(area, None)

    def hasTopLevelDockWidget(self) -> bool:
        '''
        This function returns true if this dock area has only one single
        visible dock widget. A top level widget is a real floating widget. Only
        the isFloating() function of top level widgets may returns true.

        Returns
        -------
        value : bool
        '''
        _dock_areas = self.openedDockAreas()
        if len(_dock_areas) != 1:
            return False

        return _dock_areas[0].openDockWidgetsCount() == 1

    def hasOpenDockAreas(self):
        return len([x for x in self._mgr.dockAreas if not x.isHidden()]) != 0

    def handleAutoHideWidgetEvent(self, event: QtCore.QEvent, widget: QtWidgets.QWidget):
        if EnumAutoHideFlag.AutoHideShowOnMouseOver not in AUTO_HIDE_DEFAULT_CONFIG:
            return
        if self.dockManager().isRestoringState():
            return
        if isinstance(widget, CAutoHideTab):
            if event.type() == QtCore.QEvent.Type.Enter:
                if not widget.dockWidget().isVisible():
                    self._mgr.delayedAutoHideTab = widget
                    self._mgr.delayedAutoHideShow = True
                    self._mgr.delayedAutoHideTimer.start()
                else:
                    self._mgr.delayedAutoHideTimer.stop()
            elif event.type() == QtCore.QEvent.Type.MouseButtonPress:
                self._mgr.delayedAutoHideTimer.stop()
            elif event.type() == QtCore.QEvent.Type.Leave:
                if widget.dockWidget().isVisible():
                    self._mgr.delayedAutoHideTab = widget
                    self._mgr.delayedAutoHideShow = False
                    self._mgr.delayedAutoHideTimer.start()
                else:
                    self._mgr.delayedAutoHideTimer.stop()
        elif isinstance(widget, CAutoHideDockContainer):
            if event.type() in [QtCore.QEvent.Type.Enter, QtCore.QEvent.Type.Hide]:
                self._mgr.delayedAutoHideTimer.stop()
            elif event.type() == QtCore.QEvent.Type.Leave:
                if widget.isVisible():
                    self._mgr.delayedAutoHideTab = widget.autoHideTab()
                    self._mgr.delayedAutoHideShow = False
                    self._mgr.delayedAutoHideTimer.start()

    def topLevelDockWidget(self) -> 'CDockWidget':
        '''
        If hasSingleVisibleDockWidget() returns true, this function returns the
        one and only visible dock widget. Otherwise it returns a nullptr.

        Returns
        -------
        value : DockWidget
        '''
        _top_level_dock_area = self.topLevelDockArea()
        if _top_level_dock_area is None:
            return None

        _dock_widgets = _top_level_dock_area.openedDockWidgets()
        if len(_dock_widgets) != 1:
            return None

        return _dock_widgets[0]

    def topLevelDockArea(self) -> CDockAreaWidget:
        '''
        Returns the top level dock area.

        Returns
        -------
        value : DockAreaWidget
        '''
        _dock_areas = self.openedDockAreas()
        if len(_dock_areas) != 1:
            return None

        return _dock_areas[0]

    def dockWidgets(self) -> list:
        '''
        This function returns a list of all dock widgets in this floating
        widget. It may be possible, depending on the implementation, that dock
        widgets, that are not visible to the user have no parent widget.
        Therefore simply calling findChildren() would not work here. Therefore
        this function iterates over all dock areas and creates a list that
        contains all dock widgets returned from all dock areas.

        Returns
        -------
        value : list
        '''
        return [widget
                for dock_area in self._mgr.dockAreas
                for widget in dock_area.dockWidgets()
                ]

    def addDockWidget(self, area: EnumDockWidgetArea, dock_widget: 'CDockWidget',
                      dock_area_widget: CDockAreaWidget = None, idx: int = -1) -> CDockAreaWidget:
        '''
        Adds dockwidget into the given area. If DockAreaWidget is not null,
        then the area parameter indicates the area into the DockAreaWidget. If
        DockAreaWidget is null, the Dockwidget will be dropped into the
        container.

        Parameters
        ----------
        area : DockWidgetArea
        dock_widget : DockWidget
        dock_area_widget : DockAreaWidget

        Returns
        -------
        value : DockAreaWidget
        '''
        _top_level_dock_widget = self.topLevelDockWidget()
        _old_dock_area = dock_widget.dockAreaWidget()
        if _old_dock_area is not None:
            _old_dock_area.removeDockWidget(dock_widget)

        dock_widget.setDockManager(self._mgr.dockManager)
        if dock_area_widget is not None:
            _dock_area = self._mgr.addDockWidgetToDockArea(area, dock_widget, dock_area_widget, idx)
        else:
            _dock_area = self._mgr.addDockWidgetToContainer(area, dock_widget)
        if _top_level_dock_widget is not None:
            _new_top_level_dock_widget = self.topLevelDockWidget()
            """
            If the container contained only one visible dock widget, the we need
            to emit a top level event for this widget because it is not the one and
		    only visible docked widget anymore
            """
            if _new_top_level_dock_widget is None:
                emitTopLevelEventForWidget(_top_level_dock_widget, False)
        return _dock_area

    def removeDockWidget(self, widget: 'CDockWidget'):
        '''
        Removes a given DockWidget

        Parameters
        ----------
        widget : DockWidget
        '''
        _area = widget.dockAreaWidget()
        if _area is not None:
            _area.removeDockWidget(widget)

    def zOrderIndex(self) -> int:
        '''
        Returns the current zOrderIndex

        Returns
        -------
        value : unsigned int
        '''
        return self._mgr.zOrderIndex

    def isInFrontOf(self, other: 'CDockContainerWidget') -> bool:
        '''
        This function returns true if this container widgets z order index is
        higher than the index of the container widget given in Other parameter

        Parameters
        ----------
        other : DockContainerWidget

        Returns
        -------
        value : bool
        '''
        return self.zOrderIndex() > other.zOrderIndex()

    def dockAreaAt(self, global_pos: QtCore.QPoint) -> CDockAreaWidget:
        '''
        Returns the dock area at teh given global position or 0 if there is no
        dock area at this position

        Parameters
        ----------
        global_pos : QPoint

        Returns
        -------
        value : DockAreaWidget
        '''
        for dock_area in self._mgr.dockAreas:
            _pos = dock_area.mapFromGlobal(global_pos)
            if dock_area.isVisible() and dock_area.rect().contains(_pos):
                return dock_area
        return None

    def dockManager(self):
        return self._mgr.dockManager

    def dockArea(self, index: int) -> CDockAreaWidget:
        '''
        Returns the dock area at the given Index or 0 if the index is out of range

        Parameters
        ----------
        index : int

        Returns
        -------
        value : DockAreaWidget
        '''
        try:
            return self._mgr.dockAreas[index]
        except IndexError:
            return None

    def openedDockAreas(self) -> list:
        '''
        Returns the list of dock areas that are not closed If all dock widgets
        in a dock area are closed, the dock area will be closed

        Returns
        -------
        value : list
        '''
        return [dock_area
                for dock_area in self._mgr.dockAreas
                if not dock_area.isHidden()
                ]

    def openedDockWidgets(self):
        _list = list()

        [_list.extend(dock_area.openedDockWidgets())
         for dock_area in self._mgr.dockAreas
         if not dock_area.isHidden()
         ]
        return _list

    def dockAreaCount(self) -> int:
        '''
        Returns the number of dock areas in this container

        Returns
        -------
        value : int
        '''
        return len(self._mgr.dockAreas)

    def updateSplitterHandles(self, splitter: QtWidgets.QSplitter):
        self._mgr.updateSplitterHandles(splitter)

    def visibleDockAreaCount(self) -> int:
        '''
        Returns the number of visible dock areas

        Returns
        -------
        value : int
        '''
        return len([dock_area
                    for dock_area in self._mgr.dockAreas
                    if not dock_area.isHidden()
                    ])

        # TODO_UPSTREAM Cache or precalculate this to speed it up because it is used during
        # movement of floating widget
        # return d.visible_dock_area_count()

    def isFloating(self) -> bool:
        '''
        This function returns true, if this container is in a floating widget

        Returns
        -------
        value : bool
        '''
        return self._mgr.isFloating

    def dumpLayout(self):
        '''
        Dumps the layout for debugging purposes
        '''
        if not logger.isEnabledFor(logging.DEBUG):
            return

        logger.debug("--------------------------")
        self._mgr.dumpRecursive(0, self._mgr.rootSplitter)
        logger.debug("--------------------------\n\n")

    def features(self) -> EnumDockWidgetFeature:
        '''
        This functions returns the dock widget features of all dock widget in
        this container. A bitwise and is used to combine the flags of all dock
        widgets. That means, if only dock widget does not support a certain
        flag, the whole dock are does not support the flag.

        Returns
        -------
        value : DockWidgetFeature
        '''
        _features = EnumDockWidgetFeature.ALL
        for dock_area in self._mgr.dockAreas:
            _features &= dock_area.features()
        return _features

    def floatingWidget(self) -> 'CFloatingDockContainer':
        '''
        If this dock container is in a floating widget, this function returns
        the floating widget. Else, it returns a nullptr.

        Returns
        -------
        value : FloatingDockContainer
        '''
        return findParent('CFloatingDockContainer', self)

    def closeOtherAreas(self, keep_open_area: CDockAreaWidget):
        '''
        Call this function to close all dock areas except the KeepOpenArea

        Parameters
        ----------
        keep_open_area : DockAreaWidget
        '''
        for dock_area in self._mgr.dockAreas:
            if dock_area is keep_open_area:
                continue
            if EnumDockWidgetFeature.CLOSEABLE not in dock_area.features():
                continue
            if EnumDockWidgetFeature.CUSTOM_CLOSE_HANDLING in dock_area.features(EnumBitwiseOP.OR):
                continue
            dock_area.closeArea()

    def sideTabBar(self, location: EnumSideBarLocation):
        return self._mgr.sideTabBarWidgets[location]
