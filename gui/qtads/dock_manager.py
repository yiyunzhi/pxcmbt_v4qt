import logging
import pathlib
import typing

from typing import TYPE_CHECKING, Dict, List
from PySide6 import QtCore, QtGui, QtWidgets

from .define import (EnumInsertionOrder,
                     EnumDockFlags,
                     EnumDockAreaFlag,
                     EnumDockWidgetArea,
                     EnumOverlayMode,
                     EnumDockWidgetFeature,
                     EnumDockMgrConfigFlag,
                     EnumAutoHideFlag,
                     EnumSideBarLocation,
                     EnuStateFileVersion,
                     DOCK_MANAGER_DEFAULT_CONFIG,
                     AUTO_HIDE_DEFAULT_CONFIG)

from .dock_container_widget import CDockContainerWidget,DockContainerWidgetMgr
from .dock_overlay import CDockOverlay
from .dock_state_reader import CDockStateReader
from .floating_dock_container import CFloatingDockContainer
from .dock_focus_controller import CDockFocusController
from .util import LINUX, findParent, testFlag
from .dock_area_widget import CDockAreaWidget

try:
    from qtpy.QtCore import qCompress, qUncompress
except ImportError:
    qCompress = None
    qUncompress = None

if TYPE_CHECKING:

    from .dock_widget import CDockWidget
    from .dock_splitter import CDockSplitter

logger = logging.getLogger(__name__)


class DockManagerMgr:
    _this: 'CDockManager'
    floatingWidgets: List['CFloatingDockContainer']
    hiddenFloatingWidgets: List['CFloatingDockContainer']
    containers: List['CDockContainerWidget']
    containerOverlay: 'CDockOverlay'
    dockAreaOverlay: 'CDockOverlay'
    dockWidgetsMap: Dict[str, 'CDockWidget']
    perspectives: Dict[str, QtCore.QByteArray]
    viewMenuGroups: Dict[str, QtWidgets.QMenu]
    viewMenu: QtWidgets.QMenu
    menuInsertionOrder: EnumInsertionOrder
    restoringState: bool
    uninitializedFloatingWidgets: List['CFloatingDockContainer']
    focusController: 'CDockFocusController'
    centralWidget: 'CDockWidget'

    def __init__(self, _this):
        '''
        Private data constructor

        Parameters
        ----------
        _this : DockManager
        '''

        self._this = _this
        self.floatingWidgets = []
        self.hiddenFloatingWidgets=[]
        self.containers = []
        self.uninitializedFloatingWidgets = []
        self.containerOverlay = None
        self.dockAreaOverlay = None
        self.dockWidgetsMap = {}
        self.perspectives = {}
        self.viewMenuGroups = {}
        self.viewMenu = None
        self.focusController = None
        self.centralWidget = None
        self.menuInsertionOrder = EnumInsertionOrder.BY_SPELLING
        self.restoringState = False

    def checkFormat(self, state: QtCore.QByteArray, version: int) -> bool:
        '''
        Checks if the given data stream is a valid docking system state file.

        Parameters
        ----------
        state : QByteArray
        version : int

        Returns
        -------
        value : bool
        '''
        """
        bool DockManagerPrivate::checkFormat(const QByteArray &state, int version)
        {
            return restoreStateFromXml(state, version, internal::RestoreTesting);
        }
        """
        return self.restoreStateFromXml(state, version, testing=True)

    def restoreStateFromXml(self, state: QtCore.QByteArray, version: int, testing: bool) -> bool:
        '''
        Restores the state

        Parameters
        ----------
        state : QByteArray
        version : int
        testing : bool

        Returns
        -------
        value : bool
        '''
        if state.isEmpty():
            return False

        _stream = CDockStateReader(state)
        _stream.readNextStartElement()
        if _stream.name() != "QtAdvancedDockingSystem":
            return False

        _v = _stream.attributes().value("Version")
        if int(_v) != version:
            return False
        _stream.setFileVersion(_v)
        if not _stream.attributes().value("UserVersion").isEmpty():
            _v = _stream.attributes().value("UserVersion")
            if int(_v) != version:
                return False
        _result = True
        _dock_containers = int(_stream.attributes().value("Containers"))
        logger.debug('dock_containers %s', _dock_containers)
        if self.centralWidget is not None:
            _central_w_attr = _stream.attributes().value("CentralWidget")
            # If we have a central widget but a state without central widget, then
            # something is wrong.
            if _central_w_attr.isEmpty():
                logger.warning('Dock manager has central widget but saved state does not have central widget.')
                return False
            if _central_w_attr.toString() != self.centralWidget.objectName():
                logger.warning('Object name of central widget does not match name of central widget in saved state.')
                return False

        _dock_container_count = 0
        while _stream.readNextStartElement():
            if _stream.name() == "Container":
                _result = self.restoreContainer(_dock_container_count, _stream,
                                                testing=testing)
                if not _result:
                    break
                _dock_container_count += 1

        if not testing:
            _f_w_idx = _dock_container_count - 1
            for i in range(_f_w_idx, len(self.floatingWidgets)):
                _fw = self.floatingWidgets[i]
                self._this.removeDockContainer(_fw.dockContainer())
                _fw.deleteLater()

        return _result

    def restoreState(self, state: QtCore.QByteArray, version: int) -> bool:
        '''
        Restore state

        Parameters
        ----------
        state : QByteArray
        version : int

        Returns
        -------
        value : bool
        '''
        _state = state if state.startsWith('<?xml') else QtCore.qUncompress(state)
        if not self.checkFormat(state, version):
            logger.debug('checkFormat: Error checking format!')
            return False

        # Hide updates of floating widgets from use
        self.hideFloatingWidgets()
        self.markDockWidgetsDirty()
        if not self.restoreStateFromXml(state, version, testing=False):
            logger.debug('restoreState: Error restoring state!')
            return False

        self.restoreDockWidgetsOpenState()
        self.restoreDockAreasIndices()
        self.emitTopLevelEvents()
        self._this.dumpLayout()
        return True

    def restoreDockWidgetsOpenState(self):
        # All dock widgets, that have not been processed in the restore state
        # function are invisible to the user now and have no assigned dock area
        # They do not belong to any dock container, until the user toggles the
        # toggle view action the next time
        for dock_widget in self.dockWidgetsMap.values():
            if dock_widget.property("dirty"):
                # If the DockWidget is an auto hide widget that is not assigned yet,
                # then we need to delete the auto hide container now
                if dock_widget.isAutoHide():
                    dock_widget.autoHideDockContainer().cleanupAndDelete()
                dock_widget.flagAsUnassigned()
                dock_widget.sigViewToggled.emit(False)
            else:
                dock_widget.toggleViewInternal(
                    not dock_widget.property("closed")
                )

    def restoreDockAreasIndices(self):
        # Now all dock areas are properly restored and we setup the index of
        # The dock areas because the previous toggleView() action has changed
        # the dock area index
        for dock_container in self.containers:
            for i in range(dock_container.dockAreaCount()):
                _dock_area = dock_container.dockArea(i)
                _dock_widget_name = _dock_area.property("currentDockWidget")
                _dock_widget = None
                if not _dock_widget_name:
                    _dock_widget = self._this.findDockWidget(_dock_widget_name)

                if not _dock_widget or _dock_widget.isClosed():
                    _index = _dock_area.indexOfFirstOpenDockWidget()
                    if _index < 0:
                        continue
                    _dock_area.setCurrentIndex(_index)
                else:
                    _dock_area.internalSetCurrentDockWidget(_dock_widget)

    def emitTopLevelEvents(self):
        # Finally we need to send the topLevelChanged() signals for all dock
        # widgets if top level changed
        for dock_container in self.containers:
            _top_level_dock_widget = dock_container.topLevelDockWidget()
            if _top_level_dock_widget is not None:
                _top_level_dock_widget.emitTopLevelChanged(True)
            else:
                for i in range(dock_container.dockAreaCount()):
                    _dock_area = dock_container.dockArea(i)
                    for dock_widget in _dock_area.dockWidgets():
                        dock_widget.emitTopLevelChanged(False)

    def hideFloatingWidgets(self):
        # Hide updates of floating widgets from use
        for floating_widget in self.floatingWidgets:
            floating_widget.hide()

    def markDockWidgetsDirty(self):
        for dock_widget in self.dockWidgetsMap.values():
            dock_widget.setProperty("dirty", True)

    def restoreContainer(self, index: int, stream: 'CDockingStateReader',
                         testing: bool) -> bool:
        '''
        Restores the container with the given index

        Parameters
        ----------
        index : int
        stream : CDockingStateReader
        testing : bool

        Returns
        -------
        value : bool
        '''
        if testing:
            index = 0

        if index >= len(self.containers):
            _floating_widget = CFloatingDockContainer(dock_manager=self._this)
            _result = _floating_widget.restoreState(stream, testing)
        else:
            logger.debug('containers[%d].restore_state()', index)
            _container = self.containers[index]
            if _container.isFloating():
                _result = _container.floatingWidget().restoreState(stream, testing)
            else:
                _result = _container.restoreState(stream, testing)
        return _result

    def loadStylesheet(self):
        '''
        Loads the stylesheet
        '''
        # todo: initial resources
        _file_name = ":ads/stylesheets/"
        _file_name += 'focus_highlighting' if testFlag(self._this.configFlags(), EnumDockMgrConfigFlag.FocusHighlighting) else 'default'
        if LINUX:
            _file_name += '_linux'
        _file_name += '.css'
        _style_file = QtCore.QFile(_file_name)
        _style_file.open(QtCore.QIODevice.OpenModeFlag.ReadOnly)
        _stream = QtCore.QTextStream(_style_file)
        _result = _stream.readAll()
        _style_file.close()
        self._this.setStyleSheet(_result)

    def addActionToMenu(self, action: QtGui.QAction,
                        menu: QtWidgets.QMenu, insert_sorted: bool):
        '''
        Adds action to menu - optionally in sorted order

        Parameters
        ----------
        action : QAction
        menu : QMenu
        insert_sorted : bool
        '''
        if insert_sorted:
            _actions = menu.actions()
            if not _actions:
                menu.addAction(action)
            else:
                _actions = [act.text() for act in _actions] + [action.text()]
                _actions.sort()
                menu.insertAction(_actions.index(_actions.text()), action)
        else:
            menu.addAction(action)


class CDockManager(CDockContainerWidget):
    # default_style_sheet = pathlib.Path(__file__).parent / (
    #     'default_linux.css' if LINUX else 'default.css')

    # This signal is emitted if the list of perspectives changed
    sigPerspectiveListChanged = QtCore.Signal()

    # This signal is emitted if perspectives have been removed
    sigPerspectivesRemoved = QtCore.Signal()

    # This signal is emitted, if the restore function is called, just before
    # the dock manager starts restoring the state. If this function is called,
    # nothing has changed yet
    sigRestoringState = QtCore.Signal()

    # This signal is emitted if the state changed in restoreState. The signal
    # is emitted if the restoreState() function is called or if the
    # openPerspective() function is called
    sigStateRestored = QtCore.Signal()

    # This signal is emitted, if the dock manager starts opening a perspective.
    # Opening a perspective may take more than a second if there are many complex
    # widgets. The application may use this signal to show some progress
    # indicator or to change the mouse cursor into a busy cursor.
    sigOpeningPerspective = QtCore.Signal(str)

    # This signal is emitted if the dock manager finished opening a perspective
    sigPerspectiveOpened = QtCore.Signal(str)
    sigFloatingWidgetCreated = QtCore.Signal(CFloatingDockContainer)
    sigDockWidgetAdded = QtCore.Signal('CDockWidget')
    sigDockWidgetAboutToBeRemoved = QtCore.Signal()
    sigDockWidgetRemoved = QtCore.Signal('CDockWidget')
    sigPerspectiveListLoaded = QtCore.Signal()
    sigDockAreaCreated = QtCore.Signal(CDockAreaWidget)
    sigFocusedDockWidgetChanged = QtCore.Signal('CDockWidget','CDockWidget')

    def __init__(self, parent: QtWidgets.QWidget):
        '''
        The central dock manager that maintains the complete docking system.
        With the configuration flags you can globally control the functionality
        of the docking system.

        If the given parent is a QMainWindow, the dock manager sets itself as
        the central widget. Before you create any dock widgets, you should
        properly setup the configuration flags via setConfigFlags()

        Parameters
        ----------
        parent : QWidget
        '''
        super().__init__(self, parent)
        self._mgrThis = DockManagerMgr(self)
        self.createRootSplitter()
        self.createSideTabBarWidgets()
        if isinstance(parent, QtWidgets.QMainWindow):
            parent.setCentralWidget(self)
        self.floatingContainerTitle = ''
        self._mgrThis.viewMenu = QtWidgets.QMenu("Show View", self)
        self._mgrThis.dockAreaOverlay = CDockOverlay(self, EnumOverlayMode.DOCK_AREA)
        self._mgrThis.containerOverlay = CDockOverlay(self, EnumOverlayMode.CONTAINER)
        self._mgrThis.containers.append(self)
        self._mgrThis.loadStylesheet()
        if testFlag(self.configFlags(), EnumDockMgrConfigFlag.FocusHighlighting):
            self._mgrThis.focusController = CDockFocusController(self)
        # todo: support for linux

    def deleteLater(self):
        _floating_widgets = self._mgr.floatingWidgets
        for area in self.dockArea():
            area.dockWidget().deleteLater()
        for floating_widget in _floating_widgets:
            floating_widget.deleteLater()
        self._mgr.floatingWidgets.clear()
        super().deleteLater()

    def registerFloatingWidget(self, floating_widget: CFloatingDockContainer):
        '''
        Registers the given floating widget in the internal list of floating widgets

        Parameters
        ----------
        floating_widget : FloatingDockContainer
        '''
        self._mgrThis.floatingWidgets.append(floating_widget)
        self.sigFloatingWidgetCreated.emit(floating_widget)
        logger.debug('floating widgets count = %d',
                     len(self._mgrThis.floatingWidgets))

    def removeFloatingWidget(self, floating_widget: CFloatingDockContainer):
        '''
        Remove the given floating widget from the list of registered floating widgets

        Parameters
        ----------
        floating_widget : FloatingDockContainer
        '''
        if floating_widget not in self._mgrThis.floatingWidgets:
            logger.error('qtpydocking bug; floating widget not in list: '
                         '%s not in %s', floating_widget,
                         self._mgrThis.floatingWidgets)
            return

        self._mgrThis.floatingWidgets.remove(floating_widget)

    def registerDockContainer(self, dock_container: CDockContainerWidget):
        '''
        Registers the given dock container widget

        Parameters
        ----------
        dock_container : DockContainerWidget
        '''
        self._mgrThis.containers.append(dock_container)

    def removeDockContainer(self, dock_container: CDockContainerWidget):
        '''
        Remove dock container from the internal list of registered dock containers

        Parameters
        ----------
        dock_container : DockContainerWidget
        '''
        if self is not dock_container and dock_container in self._mgrThis.containers:
            self._mgrThis.containers.remove(dock_container)

    def testAutoHideConfigFlag(self, flag):
        return flag in self.autoHideConfigFlags()

    def iconProvider(self):
        return None

    def containerOverlay(self) -> CDockOverlay:
        '''
        Overlay for containers

        Returns
        -------
        value : DockOverlay
        '''
        return self._mgrThis.containerOverlay

    def dockAreaOverlay(self) -> CDockOverlay:
        '''
        Overlay for dock areas

        Returns
        -------
        value : DockOverlay
        '''
        return self._mgrThis.dockAreaOverlay

    def dockWidgetMap(self):
        return self._mgrThis.dockWidgetsMap

    def configFlags(self) -> EnumDockMgrConfigFlag:
        '''
        This function returns the global configuration flags

        Returns
        -------
        value : DockFlags
        '''
        return DOCK_MANAGER_DEFAULT_CONFIG

    def autoHideConfigFlags(self) -> EnumAutoHideFlag:
        return AUTO_HIDE_DEFAULT_CONFIG

    def setConfigFlags(self, flags: EnumDockMgrConfigFlag):
        '''
        Sets the global configuration flags for the whole docking system. Call
        this function before you create your first dock widget.

        Parameters
        ----------
        flags : DockFlags
        '''
        # todo: fixthis
        _STATIC_DM_CONFIG_FLAGS = flags

    def setAutoHideConfigFlags(self, flags: EnumAutoHideFlag):
        _STATIC_AH_FLAGS = flags

    def addDockWidget(
            self, area: 'EnumDockWidgetArea',
            dock_widget: 'CDockWidget',
            dock_area_widget: 'CDockAreaWidget' = None,
            idx: int = -1
    ) -> 'CDockAreaWidget':
        '''
        Adds dock_widget into the given area. If DockAreaWidget is not null,
        then the area parameter indicates the area into the DockAreaWidget. If
        DockAreaWidget is null, the Dockwidget will be dropped into the
        container. If you would like to add a dock widget tabified, then you
        need to add it to an existing dock area object into the
        CenterEnumDockWidgetArea The following code shows this:

        Parameters
        ----------
        area : DockWidgetArea
        dock_widget : DockWidget
        dock_area_widget : DockAreaWidget, optional

        Returns
        -------
        value : DockAreaWidget
        '''
        # self._mgrThis.dockWidgetsMap[dock_widget.objectName()] = dock_widget
        # if dock_area_widget is None:
        #     dock_area_widget=self
        #     _area_of_added_dock_widget=super().addDockWidget(area, dock_widget, dock_area_widget, idx)
        # else:
        #     _container = dock_area_widget.dockContainer()
        #     _area_of_added_dock_widget = _container.addDockWidget(area, dock_widget, dock_area_widget, idx)
        # self.sigDockWidgetAdded.emit(dock_widget)
        # return _area_of_added_dock_widget
        # self._mgrThis.dockWidgetsMap[dock_widget.objectName()] = dock_widget
        # _container = dock_area_widget.dockContainer() if dock_area_widget is not None else self
        # _area_of_added_dock_widget = _container.addDockWidget(area, dock_widget, _container, idx)
        # self.sigDockWidgetAdded.emit(dock_widget)
        # return _area_of_added_dock_widget
        return super().addDockWidget(area,dock_widget,dock_area_widget,idx)

    def addDockWidgetFloating(self, dock_widget: 'CDockWidget'):
        self._mgrThis.dockWidgetsMap.update({dock_widget.objectName(): dock_widget})
        _old_dock_area = dock_widget.dockAreaWidget()
        if _old_dock_area is not None:
            _old_dock_area.removeDockWidget(dock_widget)
        dock_widget.setDockManager(self)
        _fw = CFloatingDockContainer(dock_widget)
        _fw.resize(dock_widget.size())
        if self.isVisible():
            _fw.show()
        else:
            self._mgrThis.uninitializedFloatingWidgets.append(_fw)
        self.sigDockWidgetAdded.emit(dock_widget)
        return _fw

    def addDockWidgetTab(self, area: 'EnumDockWidgetArea',
                         dock_widget: 'CDockWidget') -> 'CDockAreaWidget':
        '''
        This function will add the given Dockwidget to the given dock area as a
        new tab. If no dock area widget exists for the given area identifier, a
        new dock area widget is created.

        Parameters
        ----------
        area : DockWidgetArea
        dock_widget : DockWidget

        Returns
        -------
        value : DockAreaWidget
        '''
        _area_widget = self.lastAddedDockAreaWidget(area)
        if _area_widget is not None:
            return self.addDockWidget(EnumDockWidgetArea.CENTER,
                                      dock_widget, _area_widget)
        else:
            return self.addDockWidget(area, dock_widget, None)

    def addDockWidgetToContainer(self, area: 'EnumDockWidgetArea',
                                 dock_widget: 'CDockWidget',
                                 dock_container_widget: 'CDockContainerWidget'):
        self._mgrThis.dockWidgetsMap.update({dock_widget.objectName(): dock_widget})
        _area_of_added_dock_widget = dock_container_widget.addDockWidget(area, dock_widget)
        self.sigDockWidgetAdded.emit(dock_widget)
        return _area_of_added_dock_widget

    def addAutoHideDockWidget(self, location: EnumSideBarLocation, dock_widget: 'CDockWidget'):
        return self.addAutoHideDockWidgetToContainer(location, dock_widget, self)

    def addAutoHideDockWidgetToContainer(self, location: EnumSideBarLocation,
                                         dock_widget: 'CDockWidget',
                                         dock_container_widget: 'CDockContainerWidget'):
        self._mgrThis.dockWidgetsMap.update({dock_widget.objectName(): dock_widget})
        _container = dock_container_widget.createAndSetupAutoHideContainer(location, dock_widget)
        _container.collapseView(True)
        self.sigDockWidgetAdded.emit(dock_widget)
        return _container

    def addDockWidgetTabToArea(self, dock_widget: 'CDockWidget',
                               dock_area_widget: 'CDockAreaWidget', idx: int
                               ) -> 'CDockAreaWidget':
        '''
        This function will add the given Dockwidget to the given DockAreaWidget
        as a new tab.

        Parameters
        ----------
        dock_widget : DockWidget
        dock_area_widget : DockAreaWidget

        Returns
        -------
        value : DockAreaWidget
        '''
        return self.addDockWidget(EnumDockWidgetArea.CENTER,
                                  dock_widget, dock_area_widget, idx)

    def findDockWidget(self, object_name: str) -> 'CDockWidget':
        '''
        Searches for a registered doc widget with the given ObjectName

        Parameters
        ----------
        object_name : str

        Returns
        -------
        value : DockWidget
        '''
        return self._mgrThis.dockWidgetsMap.get(object_name, None)

    def removeDockWidget(self, widget: 'CDockWidget'):
        '''
        Removes a given DockWidget

        Parameters
        ----------
        widget : DockWidget
        '''

        self.sigDockWidgetAboutToBeRemoved.emit(widget)
        self._mgrThis.dockWidgetsMap.pop(widget.objectName())
        CDockContainerWidget.removeDockWidget(widget)
        widget.setDockManager(None)
        self.sigDockWidgetRemoved.emit(widget)

    def dockContainers(self) -> list:
        '''
        Returns the list of all active and visible dock containers

        Dock containers are the main dock manager and all floating widgets.

        Returns
        -------
        value : list
        '''
        for container in list(self._mgrThis.containers):
            try:
                container.isVisible()
            except RuntimeError as ex:
                self._mgrThis.containers.remove(container)
                logger.debug('qtpydocking TODO, container deleted',
                             exc_info=ex)

        return list(self._mgrThis.containers)

    def floatingWidgets(self) -> list:
        '''
        Returns the list of all floating widgets

        Returns
        -------
        value : list
        '''
        return self._mgrThis.floatingWidgets

    def zOrderIndex(self) -> int:
        '''
        This function always return 0 because the main window is always behind
        any floating widget

        Returns
        -------
        value : unsigned int
        '''
        return 0

    def saveState(self, version: int = 0) -> QtCore.QByteArray:
        '''
        Saves the current state of the dockmanger and all its dock widgets into
        the returned QByteArray.

        See also `config_flags`, which allow for auto-formatting and compression
        of the resulting XML file.

        Parameters
        ----------
        version : int

        Returns
        -------
        value : QByteArray
        '''

        _xml_data = QtCore.QByteArray()
        _stream = QtCore.QXmlStreamWriter(_xml_data)
        _stream.setAutoFormatting(EnumDockFlags.XML_AUTO_FORMATTING in self.configFlags())
        _stream.writeStartDocument()
        _stream.writeStartElement("QtAdvancedDockingSystem")
        _stream.writeAttribute("Version", str(EnuStateFileVersion.CurrentVersion))
        _stream.writeAttribute("UserVersion", str(version))
        _stream.writeAttribute("Containers", str(len(self._mgrThis.containers)))
        if self._mgrThis.centralWidget is not None:
            _stream.writeAttribute("CentralWidget", self._mgrThis.centralWidget.objectName())
        for container in self._mgrThis.containers:
            container.saveState(_stream)

        _stream.writeEndElement()
        _stream.writeEndDocument()

        return (QtCore.qCompress(_xml_data, 9)
                if EnumDockFlags.XML_COMPRESSION in self.configFlags()
                   and qCompress is not None
                else _xml_data)

    def restore_state(self, state: QtCore.QByteArray, version: int = 0) -> bool:
        '''
        Restores the state of this dockmanagers dockwidgets. The version number
        is compared with that stored in state. If they do not match, the
        dockmanager's state is left unchanged, and this function returns false;
        otherwise, the state is restored, and this function returns true.

        Parameters
        ----------
        state : QByteArray
        version : int

        Returns
        -------
        value : bool
        '''
        if self._mgrThis.restoringState:
            return False
        if not self.isHidden():
            self.hide()
        self._mgrThis.restoringState = True
        self.sigRestoringState.emit()
        _res = self._mgrThis.restoreState(state, version)
        self._mgrThis.restoringState = False
        if not self.isHidden():
            self.show()
        self.sigStateRestored.emit()
        return _res

    def addPerspective(self, unique_perspective_name: str):
        '''
        Saves the current perspective to the internal list of perspectives. A
        perspective is the current state of the dock manager assigned with a
        certain name. This makes it possible for the user, to switch between
        different perspectives quickly. If a perspective with the given name
        already exists, then it will be overwritten with the new state.

        Parameters
        ----------
        unique_perspective_name : str
        '''
        self._mgrThis.perspectives[unique_perspective_name] = self.saveState()
        self.sigPerspectiveListChanged.emit()

    def removePerspective(self, *names):
        '''
        Removes the given perspective(s) from the dock manager

        Parameters
        ----------
        *names : str
        '''
        _count = 0
        for name in names:
            try:
                del self._mgrThis.perspectives[name]
            except KeyError:
                ...
            else:
                _count += 1

        if _count:
            self.sigPerspectivesRemoved.emit()
            self.sigPerspectiveListChanged.emit()

    def perspectiveNames(self) -> List[str]:
        '''
        Returns the names of all available perspectives

        Returns
        -------
        value : list
        '''
        return list(self._mgrThis.perspectives.keys())

    def openPerspective(self, perspective_name: str):
        if perspective_name not in self._mgrThis.perspectives:
            return
        self.sigOpeningPerspective.emit(perspective_name)
        self.restoreState(self._mgrThis.perspectives.get(perspective_name))
        self.sigPerspectiveOpened.emit(perspective_name)

    def savePerspectives(self, settings: QtCore.QSettings):
        '''
        Saves the perspectives to the given settings file.

        Parameters
        ----------
        settings : QSettings
        '''
        settings.beginWriteArray("Perspectives", len(self._mgrThis.perspectives))

        for i, (key, perspective) in enumerate(self._mgrThis.perspectives.items()):
            settings.setArrayIndex(i)
            settings.setValue("Name", key)
            settings.setValue("State", perspective)

        settings.endArray()

    def loadPerspectives(self, settings: QtCore.QSettings):
        '''
        Loads the perspectives from the given settings file

        Parameters
        ----------
        settings : QSettings
        '''
        self._mgrThis.perspectives.clear()
        _size = settings.beginReadArray("Perspectives")
        if not _size:
            settings.endArray()
            return

        for i in range(_size):
            settings.setArrayIndex(i)
            name = settings.value("Name")
            data = settings.value("State")
            if not name or not data:
                continue

            self._mgrThis.perspectives[name] = data

        settings.endArray()
        self.sigPerspectiveListChanged.emit()
        self.sigPerspectiveListLoaded.emit()

    def centralWidget(self):
        return self._mgrThis.centralWidget

    def setCentralWidget(self, widget: 'CDockWidget'):
        if widget is None:
            self._mgrThis.centralWidget = None
            return None
        if self._mgrThis.centralWidget:
            logger.warning('central widget already exist')
            return None
        if self._mgrThis.dockWidgetsMap:
            logger.warning('no place for the central widget')
            return None
        widget.setFeature(EnumDockWidgetFeature.CLOSEABLE, False)
        widget.setFeature(EnumDockWidgetFeature.MOVABLE, False)
        widget.setFeature(EnumDockWidgetFeature.FLOATABLE, False)
        widget.setFeature(EnumDockWidgetFeature.PINNABLE, False)
        self._mgrThis.centralWidget = widget
        _center_area = self.addDockWidget(EnumDockWidgetArea.CENTER, widget)
        _center_area.setDockAreaFlag(EnumDockAreaFlag.HideSingleWidgetTitleBar, True)
        return _center_area

    def showEvent(self, event: QtGui.QShowEvent):
        super().showEvent(event)
        self.restoreHiddenFloatingWidgets()
        if not self._mgrThis.uninitializedFloatingWidgets:
            return
        for x in self._mgrThis.uninitializedFloatingWidgets:
            if x.dockContainer().hasOpenDockAreas():
                x.show()
        self._mgrThis.uninitializedFloatingWidgets.clear()

    def restoreHiddenFloatingWidgets(self):
        if not self._mgrThis.hiddenFloatingWidgets:
            return
        for x in self._mgrThis.hiddenFloatingWidgets:
            _visible = False
            for y in x.dockWidgets():
                if y.toggleViewAction().isChecked():
                    y.toggleView(True)
                    _visible = True
            if _visible:
                x.show()
        self._mgrThis.hiddenFloatingWidgets.clear()

    def addToggleViewActionToMenu(self, toggle_view_action: QtGui.QAction,
                                  group: str, group_icon: QtGui.QIcon) -> QtGui.QAction:
        '''
        Adds a toggle view action to the the internal view menu. You can either
        manage the insertion of the toggle view actions in your application or
        you can add the actions to the internal view menu and then simply
        insert the menu object into your.

        Parameters
        ----------
        toggle_view_action : QAction
        group : str
        group_icon : QIcon

        Returns
        -------
        value : QAction
        '''
        _order = self._mgrThis.menuInsertionOrder
        _alphabetically_sorted = EnumInsertionOrder.BY_SPELLING == _order

        if not group:
            self._mgrThis.addActionToMenu(toggle_view_action,
                                      self._mgrThis.viewMenu,
                                      _alphabetically_sorted)
            return toggle_view_action

        try:
            _group_menu = self._mgrThis.viewMenuGroups[group]
        except KeyError:
            _group_menu = QtWidgets.QMenu(group, self)
            _group_menu.setIcon(group_icon)
            self._mgrThis.addActionToMenu(
                _group_menu.menuAction(), self._mgrThis.viewMenu,
                _alphabetically_sorted)
            self._mgrThis.viewMenuGroups[group] = _group_menu

        self._mgrThis.addActionToMenu(toggle_view_action, _group_menu,
                                  _alphabetically_sorted)
        return _group_menu.menuAction()

    def viewMenu(self) -> QtWidgets.QMenu:
        '''
        This function returns the internal view menu. To fill the view menu,
        you can use the addToggleViewActionToMenu() function.

        Returns
        -------
        value : QMenu
        '''
        return self._mgrThis.viewMenu

    def setViewMenuInsertionOrder(self, order: EnumInsertionOrder):
        '''
        Define the insertion order for toggle view menu items. The order
        defines how the actions are added to the view menu. The default
        insertion order is MenuAlphabeticallySorted to make it easier for users
        to find the menu entry for a certain dock widget. You need to call this
        function befor you insert the first menu item into the view menu.

        Parameters
        ----------
        order : InsertionOrder
        '''
        self._mgrThis.menuInsertionOrder = order

    def isRestoringState(self) -> bool:
        '''
        This function returns true between the restoringState() and
        sigStateRestored() signals.

        Returns
        -------
        value : bool
        '''
        return self._mgrThis.restoringState
    @staticmethod
    def startDragDistance():
        return QtWidgets.QApplication.startDragDistance() * 1.5

    def notifyWidgetOrAreaRelocation(self, widget: QtWidgets.QWidget):
        if self._mgrThis.focusController:
            self._mgrThis.focusController.notifyWidgetOrAreaRelocation(widget)

    def notifyFloatingWidgetDrop(self, widget: 'CFloatingDockContainer'):
        if self._mgrThis.focusController:
            self._mgrThis.focusController.notifyFloatingWidgetDrop(widget)

    @staticmethod
    def setWidgetFocus(widget: QtWidgets.QWidget):
        if EnumDockMgrConfigFlag.FocusHighlighting not in DOCK_MANAGER_DEFAULT_CONFIG:
            return
        widget.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)

    def setDockWidgetFocused(self, widget: 'CDockWidget'):
        if self._mgrThis.focusController:
            self._mgrThis.focusController.setDockWidgetFocused(widget)

    def hideManagerAndFloatingWidgets(self):
        self.hide()
        self._mgrThis.hiddenFloatingWidgets.clear()
        for x in self._mgrThis.floatingWidgets:
            if x.isVisible():
                _visible_w = list()
                for y in x.dockWidgets():
                    if y.toggleViewAction().isChecked():
                        _visible_w.append(y)
                self._mgrThis.hiddenFloatingWidgets.append(x)
                x.hide()
                for y in _visible_w:
                    y.toggleViewAction().setChecked(True)

    def focusedDockWidget(self):
        if self._mgrThis.focusController is None:
            return None
        return self._mgrThis.focusController.focusedDockWidget()

    def splitterSizes(self, container_area: 'CDockAreaWidget'):
        if container_area:
            _splitter = findParent(CDockSplitter, container_area)
            if _splitter is not None:
                return _splitter.sizes()
        return []

    def setSplitterSizes(self, container_area: 'CDockAreaWidget', sizes: typing.List[int]):
        if container_area:
            _splitter = findParent(CDockSplitter, container_area)
            if _splitter is not None and len(_splitter) == len(sizes):
                _splitter.setSizes(sizes)
        return

    def dockFocusController(self):
        return self._mgrThis.focusController

    def setFloatingContainersTitle(self, title: str):
        self.floatingContainerTitle = title

    def floatingContainersTitle(self):
        if not self.floatingContainerTitle:
            return QtWidgets.QApplication.instance().applicationName()
        return self.floatingContainerTitle
