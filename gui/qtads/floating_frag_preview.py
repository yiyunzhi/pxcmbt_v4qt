# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : floating_frag_preview.py
# ------------------------------------------------------------------------------
#
# File          : floating_frag_preview.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import logging
from PySide6 import QtGui, QtCore, QtWidgets
from .floating_base import IFloatingWidget
from .define import EnumDragState, EnumDockWidgetFeature, EnumDockWidgetArea
from .util import testFlag, qApp

logger = logging.getLogger(__name__)


class FloatingDragPreviewMgr:
    _this: 'CFloatingDragPreview'
    content: QtWidgets.QWidget
    contentSourceArea: 'CDockAreaWidget'
    dragStartMousePosition: QtCore.QPoint
    dockManager: 'CDockManager'
    dropContainer: 'CDockContainerWidget'
    windowOpacity: float
    hidden: bool
    contentPreviewPixmap: QtGui.QPixmap
    cancel: bool

    def __init__(self, _this):
        self._this = _this
        self.content = None
        self.contentSourceArea = None
        self.dragStartMousePosition = None
        self.dockManager = None
        self.dropContainer = None
        self.windowOpacity = 1
        self.hidden = False
        self.cancel = False
        self.contentPreviewPixmap = None

    def setHidden(self, value):
        self.hidden = value
        self._this.update()

    def cancelDragging(self):
        self.cancel = True
        self._this.sigDraggingCanceled.emit()
        self.dockManager.containerOverlay().hideOverlay()
        self.dockManager.dockAreaOverlay().hideOverlay()
        self._this.close()

    def createFloatingWidget(self):
        _fw = None
        if testFlag(self.content.features(), EnumDockWidgetFeature.FLOATABLE):
            _fw = CFloatingDockContainer(self.content)
        if _fw is not None:
            _fw.setGeometry(self._this.geometry())
            _fw.show()
            if self.dockManager.testConfigFlag(DragPreviewHasWindowFrame):
                QtWidgets.QApplication.processEvents()
                _fm_h = _fw.frameGeometry().height() - _fw.geometry().height()
                _fix_geo = self._this.geometry()
                _fix_geo.adjusted(0, _fm_h, 0, 0)
                _fw.setGeometry(_fix_geo)

    def updateDropOverlays(self, pos: QtCore.QPoint):
        if self.dockManager is None or not self._this.isVisible():
            return
        _containers = self.dockManager.dockContainers()
        _top_c = None
        for x in _containers:
            if not x.isVisible():
                continue
            _mapped_pos = x.mapFromGlobal(pos)
            if x.rect().contains(_mapped_pos):
                if _top_c is not None or x.isInFrontOf(_top_c):
                    _top_c = x
        _drop_c = _top_c
        _c_ol = self.dockManager.containerOverlay()
        _da_ol = self.dockManager.dockAreaOverlay()
        _dock_drop_area = _da_ol.dropAreaUnderCursor()
        _container_drop_area = _c_ol.dropAreaUnderCursor()
        if _top_c is not None:
            _c_ol.hideOverlay()
            _da_ol.hideOverlay()
            if self.dockManager.testConfigFlag(DragPreviewIsDynamic):
                self.setHidden(False)
            return
        _visible_dock_areas = _top_c.visibleDockAreaCount()
        # Include the overlay widget we're dragging as a visible widget
        if isinstance(self.content, CDockAreaWidget):
            if self.content.isAutoHide():
                _visible_dock_areas += 1
        _c_ol.setAllowedAreas(EnumDockWidgetArea.OUTER_DOCK_AREAS if _visible_dock_areas > 1 else EnumDockWidgetArea.ALL_DOCK_AREAS)
        _dock_area = _top_c.dockAreaAt(pos)
        if _dock_area is not None and _dock_area.isVisible() and _visible_dock_areas >= 0 and _dock_area is not self.contentSourceArea:
            _da_ol.enableDropPreview(True)
            _da_ol.setAllowedAreas(EnumDockWidgetArea.NO_AREA if _visible_dock_areas == 1 else _dock_area.allowedAreas())
            _area = _da_ol.showOverlay(_dock_area)
            # A CenterDockWidgetArea for the dockAreaOverlay() indicates that
            # the mouse is in the title bar. If the ContainerArea is valid
            # then we ignore the dock area of the dockAreaOverlay() and disable
            # the drop preview
            if _area == EnumDockWidgetArea.CENTER and _container_drop_area != EnumDockWidgetArea.INVALID:
                _da_ol.enableDropPreview(False)
                _c_ol.enableDropPreview(True)
            else:
                _c_ol.enableDropPreview(_area == EnumDockWidgetArea.INVALID)
            _c_ol.showOverlay(_top_c)
        else:
            _da_ol.hideOverlay()
            # If there is only one single visible dock area in a container, then
            # it does not make sense to show a dock overlay because the dock area
            # would be removed and inserted at the same position
            if _visible_dock_areas == 1:
                _c_ol.hideOverlay()
            else:
                _c_ol.showOverlay(_top_c)
            if _dock_area is self.contentSourceArea and EnumDockWidgetArea.INVALID == _container_drop_area:
                self.dropContainer = None
        if self.dockManager.testConfigFlag(DragPreviewIsDynamic):
            self.setHidden(_dock_drop_area != EnumDockWidgetArea.INVALID or _container_drop_area != EnumDockWidgetArea.INVALID)


class CFloatingDragPreview(QtWidgets.QWidget, IFloatingWidget):
    sigDraggingCanceled = QtCore.Signal()

    def __init__(self, content: QtWidgets.QWidget, parent: QtWidgets.QWidget=None):
        super().__init__(parent)
        self._mgr = FloatingDragPreviewMgr(self)
        self._mgr.content = content
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        if CDockManager.testConfigFlag(DragPreviewHasWindowFrame):
            self.setWindowFlags(QtCore.Qt.WindowType.WindowMaximizeButtonHint
                                | QtCore.Qt.WindowType.WindowMaximizeButtonHint)
        else:
            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        if LINUX:
            _flags = self.windowFlags()
            _flags |= QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.X11BypassWindowManagerHint
            self.setWindowFlags(_flags)
        self.setWindowOpacity(0.6)
        # Create a static image of the widget that should get undocked
        # This is like some kind preview image like it is uses in drag and drop
        # operations
        if CDockManager.testConfigFlag(DragPreviewShowsContentPixmap):
            self._mgr.contentPreviewPixmap = QtGui.QPixmap(content.size())
        qApp.applicationStateChanged.connect(self.onApplicationStateChanged)
        qApp.installEventFilter(self)
        if isinstance(content, CDockWidget):
            self._mgr.dockManager = content.dockManager()
            if content.dockAreaWidget().openDockWidgetsCount() == 1:
                self._mgr.contentSourceArea = content.dockAreaWidget()
            self.setWindowTitle(content.windowTitle())
        elif isinstance(content, CDockAreaWidget):
            self._mgr.dockManager = content.dockManager()
            self._mgr.contentSourceArea = content
            self.setWindowTitle(content.currentDockWidget().windowTitle())

    def cleanupAutoHideContainerWidget(self):

        if isinstance(self._mgr.content, CDockWidget):
            self._mgr.content.autoHideDockContainer().cleanupAndDelete()
        elif isinstance(self._mgr.content, CDockAreaWidget):
            self._mgr.content.autoHideDockContainer().cleanupAndDelete()

    def finishDragging(self):
        logger.debug('CFloatingDragPreview::finishDragging')
        self.cleanupAutoHideContainerWidget()
        _dock_drop_area = self._mgr.dockManager.dockAreaOverlay().visibleDropAreaUnderCursor()
        _container_drop_area = self._mgr.dockManager.containerAreaOverlay().visibleDropAreaUnderCursor()
        if self._mgr.dropContainer is None:
            self._mgr.createFloatingWidget()
        elif _dock_drop_area != EnumDockWidgetArea.INVALID:
            self._mgr.dropContainer.dropWidget(self._mgr.content, _dock_drop_area, self._mgr.dropContainer.dockAreaAt(QtGui.QCursor.pos()))
        elif _container_drop_area != EnumDockWidgetArea.INVALID:
            # If there is only one single dock area, and we drop into the center
            # then we tabify the dropped widget into the only visible dock area
            if self._mgr.dropContainer.visibleDockAreaCount() <= 1 and EnumDockWidgetArea.CENTER == _container_drop_area:
                self._mgr.dropContainer.dropWidget(self._mgr.content, _container_drop_area, self._mgr.dropContainer.dockAreaAt(QtGui.QCursor.pos()))
            else:
                self._mgr.dropContainer.dropWidget(self._mgr.content, _container_drop_area, None)
        else:
            self._mgr.createFloatingWidget()
        self.close()
        self._mgr.dockManager.containerOverlay().hideOverlay()
        self._mgr.dockManager.dockAreaOverlay().hideOverlay()

    def moveFloating(self):
        _border_size = (self.frameSize().width() - self.size().width()) / 2
        _move_to_pos = QtGui.QCursor.pos() - self._mgr.dragStartMousePosition - QtCore.QPoint(_border_size, 0)
        self.move(_move_to_pos)
        self._mgr.updateDropOverlays(QtGui.QCursor.pos())

    def startFloating(self, drag_start_mouse_pos: QtCore.QPoint,
                      size: QtCore.QSize,
                      drag_state: EnumDragState, widget: QtWidgets.QWidget):
        self.resize(size)
        self._mgr.dragStartMousePosition = drag_start_mouse_pos
        self.moveFloating()
        self.show()

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if not self._mgr.cancel and event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Escape:
                watched.removeEventFilter(self)
                self._mgr.cancelDragging()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        if self._mgr.hidden:
            return
        _p = QtGui.QPainter(self)
        if CDockManager.testConfigFlag(DragPreviewShowsContentPixmap):
            _p.drawPixmap(QtCore.QPoint(0, 0), self._mgr.contentPreviewPixmap)
        # If we do not have a window frame then we paint a QRubberBand like
        # frameless window
        if not CDockManager.testConfigFlag(DragPreviewHasWindowFrame):
            _color = self.palette().color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Highlight)
            _pen = _p.pen()
            _pen.setColor(_color.darker(120))
            _pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
            _pen.setWidth(1)
            _pen.setCosmetic(True)
            _p.setPen(_pen)
            _color = _color.lighter(130)
            _color.setAlpha(64)
            _p.setBrush(_color)
            _p.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def onApplicationStateChanged(self, state: QtCore.Qt.ApplicationState):
        if state != QtCore.Qt.ApplicationState.ApplicationActive:
            qApp.applicationStateChanged.disconnect(self.onApplicationStateChanged)
            self._mgr.cancelDragging()
