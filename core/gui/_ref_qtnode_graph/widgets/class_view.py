# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_view.py
# ------------------------------------------------------------------------------
#
# File          : class_view.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import math
from distutils.version import LooseVersion
from gui import QtGui, QtCore, QtWidgets, QtOpenGLWidgets

from ..core.define import (
    EnumLayoutDirection, EnumPortType, EnumPipeShape
)
from ..graphics.class_base import BaseNodeItem
from ..graphics.class_backdrop_node_item import BackdropNodeItem
from ..graphics.class_pipe_item import PipeItem, LivePipeItem
from ..graphics.class_port_item import PortItem
from ..graphics.class_slicer_item import SlicerPipeItem
from .class_dialogs import FeedbackDialog, FileDialog
from .class_scene import NodeScene
from .class_search_widget import SearchMenuWidget
from .class_menu_widget import BaseMenu

# todo: move into style
ZOOM_MIN = -0.95
ZOOM_MAX = 2.0


class NodeGraphView(QtWidgets.QGraphicsView):
    """
    The widget interface used for displaying the scene and nodes.

    functions in this class should mainly be called by the
    class:`NodeGraphQt.NodeGraph` class.
    """

    # node viewer signals.
    # (some of these signals are called by port & node items and connected
    # to the node graph slot functions)
    sigMovedNodes = QtCore.Signal(dict)
    sigSearchTriggered = QtCore.Signal(str, tuple)
    sigConnectionSliced = QtCore.Signal(list)
    sigConnectionChanged = QtCore.Signal(list, list)
    sigNodeInserted = QtCore.Signal(object, str, dict)
    sigNodeNameChanged = QtCore.Signal(str, str)
    sigBackdropNodeUpdated = QtCore.Signal(str, str, object)

    # pass through signals that are translated into "NodeGraph()" signals.
    sigNodeSelected = QtCore.Signal(str)
    sigNodeSelectionChanged = QtCore.Signal(list, list)
    sigNodeDoubleClicked = QtCore.Signal(str)
    sigDataDropped = QtCore.Signal(QtCore.QMimeData, QtCore.QPoint)

    sigSceneUpdate = QtCore.Signal(QtCore.QObject)

    def __init__(self, parent=None, undo_stack=None):
        """
        Args:
            parent:
            undo_stack (QtWidgets.QUndoStack): undo stack from the parent
                                               graph controller.
        """
        super(NodeGraphView, self).__init__(parent)

        self.setScene(NodeScene(self))
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setCacheMode(QtWidgets.QGraphicsView.CacheModeFlag.CacheBackground)
        self.setOptimizationFlag(QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing)

        self.setAcceptDrops(True)
        self.resize(850, 800)

        self._sceneRange = QtCore.QRectF(0, 0, self.size().width(), self.size().height())
        self._update_scene()
        self._lastSize = self.size()

        self._layoutDirection = EnumLayoutDirection.HORIZONTAL.value

        self._pipeLayout = EnumPipeShape.CURVED.value
        self._detachedPort = None
        self._startPort = None
        self._originPos = None
        self._previousPos = QtCore.QPoint(int(self.width() / 2),
                                          int(self.height() / 2))
        self._prevSelectionNodes = []
        self._prevSelectionPipes = []
        self._nodePositions = {}
        self._rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Shape.Rectangle, self)
        self._rubberBand.isActive = False

        self._LIVE_PIPE = LivePipeItem()
        self._LIVE_PIPE.setVisible(False)
        self.scene().addItem(self._LIVE_PIPE)

        self._PIPE_HANDLE = None
        self._pipeHandleStartPos = QtCore.QPoint(0,0)

        self._SLICER_PIPE = SlicerPipeItem()
        self._SLICER_PIPE.setVisible(False)
        self.scene().addItem(self._SLICER_PIPE)

        self._searchWidget = SearchMenuWidget()
        self._searchWidget.sigSearchSubmitted.connect(self._on_search_submitted)

        # workaround fix for shortcuts from the non-native menu.
        # actions don't seem to trigger so we create a hidden menu bar.
        self._ctxMenuBar = QtWidgets.QMenuBar(self)
        self._ctxMenuBar.setNativeMenuBar(False)
        # shortcuts don't work with "setVisibility(False)".
        self._ctxMenuBar.setMaximumSize(0, 0)

        # context menus.
        self._ctxGraphMenu = BaseMenu('NodeGraph', self)
        self._ctxNodeMenu = BaseMenu('Nodes', self)

        if undo_stack:
            self._undoAction = undo_stack.createUndoAction(self, '&Undo')
            self._redoAction = undo_stack.createRedoAction(self, '&Redo')
        else:
            self._undoAction = None
            self._redoAction = None

        self._build_context_menus()

        self.acyclic = True
        self.pipeCollision = False

        self._previousCursor = None
        self.LMBState = False
        self.RMBState = False
        self.MMBState = False
        self.ALTState = False
        self.CTRLState = False
        self.SHIFTState = False
        self.COLLIDINGState = False

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def focusInEvent(self, event):
        """
        Args:
            event (QtGui.QFocusEvent): focus event.
        """
        # workaround fix: Re-populate the QMenuBar so the QAction shotcuts don't
        #                 conflict with parent existing host app.
        self._ctxMenuBar.addMenu(self._ctxGraphMenu)
        self._ctxMenuBar.addMenu(self._ctxNodeMenu)
        return super(NodeGraphView, self).focusInEvent(event)

    def focusOutEvent(self, event):
        """
        Args:
            event (QtGui.QFocusEvent): focus event.
        """
        # workaround fix: Clear the QMenuBar so the QAction shotcuts don't
        #                 conflict with existing parent host app.
        self._ctxMenuBar.clear()
        return super(NodeGraphView, self).focusOutEvent(event)

    # ----------------------------------------------------------
    # private
    # ----------------------------------------------------------

    def _build_context_menus(self):
        """
        Build context menu for the node graph.
        """
        # "node context menu" disabled by default and enabled when a action
        # is added through the "NodesMenu" interface.
        self._ctxNodeMenu.setDisabled(True)

        # add the base menus.
        self._ctxMenuBar.addMenu(self._ctxGraphMenu)
        self._ctxMenuBar.addMenu(self._ctxNodeMenu)

        # setup the undo and redo actions.
        if self._undoAction and self._redoAction:
            self._undoAction.setShortcuts(QtGui.QKeySequence.StandardKey.Undo)
            self._redoAction.setShortcuts(QtGui.QKeySequence.StandardKey.Redo)
            if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
                self._undoAction.setShortcutVisibleInContextMenu(True)
                self._redoAction.setShortcutVisibleInContextMenu(True)

            # undo & redo always at the top of the "node graph context menu".
            self._ctxGraphMenu.addAction(self._undoAction)
            self._ctxGraphMenu.addAction(self._redoAction)
            self._ctxGraphMenu.addSeparator()

    def _set_view_zoom(self, value, sensitivity=None, pos=None):
        """
        Sets the zoom level.

        Args:
            value (float): zoom factor.
            sensitivity (float): zoom sensitivity.
            pos (QtCore.QPoint): mapped position.
        """
        if pos:
            pos = self.mapToScene(pos)
        if sensitivity is None:
            _scale = 1.001 ** value
            self.scale(_scale, _scale, pos)
            return

        if value == 0.0:
            return

        _scale = (0.9 + sensitivity) if value < 0.0 else (1.1 - sensitivity)
        _zoom = self.get_zoom()
        if ZOOM_MIN >= _zoom:
            if _scale == 0.9:
                return
        if ZOOM_MAX <= _zoom:
            if _scale == 1.1:
                return
        self.scale(_scale, _scale, pos)
        self.sigSceneUpdate.emit(self)

    def _set_viewer_pan(self, pos_x, pos_y):
        """
        Set the viewer in panning mode.

        Args:
            pos_x (float): x pos.
            pos_y (float): y pos.
        """
        self._sceneRange.adjust(pos_x, pos_y, pos_x, pos_y)
        self._update_scene()

    def scale(self, sx, sy, pos=None):
        _scale = [sx, sx]
        _center = pos or self._sceneRange.center()
        _w = self._sceneRange.width() / _scale[0]
        _h = self._sceneRange.height() / _scale[1]
        self._sceneRange = QtCore.QRectF(
            _center.x() - (_center.x() - self._sceneRange.left()) / _scale[0],
            _center.y() - (_center.y() - self._sceneRange.top()) / _scale[1],
            _w, _h
        )
        self._update_scene()

    def _update_scene(self):
        """
        Redraw the scene.
        """
        self.setSceneRect(self._sceneRange)
        self.fitInView(self._sceneRange, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.sigSceneUpdate.emit(self)

    def _combined_rect(self, nodes):
        """
        Returns a QRectF with the combined size of the provided node items.

        Args:
            nodes (list[AbstractNodeItem]): list of node gqgraphics items.

        Returns:
            QtCore.QRectF: combined rect
        """
        _group = self.scene().createItemGroup(nodes)
        _rect = _group.boundingRect()
        self.scene().destroyItemGroup(_group)
        return _rect

    def _items_near(self, pos, item_type=None, width=20, height=20):
        """
        Filter node graph items from the specified position, width and
        height area.

        Args:
            pos (QtCore.QPoint): scene pos.
            item_type: filter item type. (optional)
            width (int): width area.
            height (int): height area.

        Returns:
            list: qgraphics items from the scene.
        """
        _x, _y = pos.x() - width, pos.y() - height
        _rect = QtCore.QRectF(_x, _y, width, height)
        _items = []
        _excl = [self._LIVE_PIPE, self._SLICER_PIPE]
        for item in self.scene().items(_rect):
            if item in _excl:
                continue
            if not item_type or isinstance(item, item_type):
                _items.append(item)
        return _items

    def _on_search_submitted(self, node_type):
        """
        Slot function triggered when the ``TabSearchMenuWidget`` has
        submitted a search.

        This will emit the "sigSearchTriggered" signal and tell the parent node
        graph to create a new node object.

        Args:
            node_type (str): node type identifier.
        """
        _pos = self.mapToScene(self._previousPos)
        self.sigSearchTriggered.emit(node_type, (_pos.x(), _pos.y()))

    def _on_pipes_sliced(self, path):
        """
        Triggered when the slicer pipe is active

        Args:
            path (QtGui.QPainterPath): slicer path.
        """
        _ports = []
        for i in self.scene().items(path):
            if isinstance(i, PipeItem) and i != self._LIVE_PIPE:
                if any([i.input_port.locked, i.output_port.locked]):
                    continue
                _ports.append([i.input_port, i.output_port])
        self.sigConnectionSliced.emit(_ports)

    # ----------------------------------------------------------
    # override events
    # ----------------------------------------------------------

    def resizeEvent(self, event):
        _w, _h = self.size().width(), self.size().height()
        if 0 in [_w, _h]:
            self.resize(self._lastSize)
        if 0 in [self._lastSize.width(), self._lastSize.height()]:
            return
        _delta = max(_w / self._lastSize.width(), _h / self._lastSize.height())
        self._set_view_zoom(_delta)
        self._lastSize = self.size()
        self.sigSceneUpdate.emit(self)
        super(NodeGraphView, self).resizeEvent(event)

    def contextMenuEvent(self, event):
        self.RMBState = False

        _ctx_menu = None
        _ctx_menus = self.get_context_menus()

        if _ctx_menus['nodes'].isEnabled():
            _pos = self.mapToScene(self._previousPos)
            _items = self._items_near(_pos)
            _nodes = [i for i in _items if isinstance(i, BaseNodeItem)]
            if _nodes:
                _node = _nodes[0]
                _ctx_menu = _ctx_menus['nodes'].get_menu(_node.type_, _node.id)
                if _ctx_menu:
                    for action in _ctx_menu.actions():
                        if not action.menu():
                            action.node_id = _node.id

        _ctx_menu = _ctx_menu or _ctx_menus['graph']
        if len(_ctx_menu.actions()) > 0:
            if _ctx_menu.isEnabled():
                _ctx_menu.exec_(event.globalPos())
            else:
                return super(NodeGraphView, self).contextMenuEvent(event)

        return super(NodeGraphView, self).contextMenuEvent(event)

    def mousePressEvent(self, event):
        self._previousCursor = self.cursor()
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.LMBState = True
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.RMBState = True
        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.MMBState = True

        self._originPos = event.pos()
        self._previousPos = event.pos()
        (self._prevSelectionNodes,
         self._prevSelectionPipes) = self.get_selected_items()

        # close tab search
        if self._searchWidget.isVisible():
            self.tab_search_toggle()

        # cursor pos.
        _map_pos = self.mapToScene(event.pos())

        # pipe slicer enabled.
        _slicer_mode = all([self.ALTState, self.SHIFTState, self.LMBState])
        if _slicer_mode:
            self._SLICER_PIPE.draw_path(_map_pos, _map_pos)
            self._SLICER_PIPE.setVisible(True)
            return

        # pan mode.
        if self.ALTState:
            self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
            return

        _items = self._items_near(_map_pos, None, 20, 20)
        _nodes = [i for i in _items if isinstance(i, BaseNodeItem)]
        # pipes = [i for i in items if isinstance(i, PipeItem)]

        if _nodes:
            self.MMBState = False

        # toggle extend node selection.
        if self.LMBState:
            if self.SHIFTState:
                for node in _nodes:
                    node.selected = not node.selected
            elif self.CTRLState:
                for node in _nodes:
                    node.selected = False

        # update the recorded node positions.
        self._nodePositions.update(
            {n: n.xy_pos for n in self.get_selected_nodes()}
        )

        # show selection selection marquee.
        if self.LMBState and not _items:
            _rect = QtCore.QRect(self._previousPos, QtCore.QSize())
            _rect = _rect.normalized()
            _map_rect = self.mapToScene(_rect).boundingRect()
            self.scene().update(_map_rect)
            self._rubberBand.setGeometry(_rect)
            self._rubberBand.isActive = True

        if self.LMBState and (self.SHIFTState or self.CTRLState):
            return

        if not self._LIVE_PIPE.isVisible():
            super(NodeGraphView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.LMBState = False
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.RMBState = False
        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.MMBState = False
        self.setCursor(self._previousCursor)
        # hide pipe slicer.
        if self._SLICER_PIPE.isVisible():
            self._on_pipes_sliced(self._SLICER_PIPE.path())
            _p = QtCore.QPointF(0.0, 0.0)
            self._SLICER_PIPE.draw_path(_p, _p)
            self._SLICER_PIPE.setVisible(False)

        # hide selection marquee
        if self._rubberBand.isActive:
            self._rubberBand.isActive = False
            if self._rubberBand.isVisible():
                _rect = self._rubberBand.rect()
                _map_rect = self.mapToScene(_rect).boundingRect()
                self._rubberBand.hide()

                _rect = QtCore.QRect(self._originPos, event.pos()).normalized()
                _rect_items = self.scene().items(
                    self.mapToScene(_rect).boundingRect()
                )
                _node_ids = []
                for item in _rect_items:
                    if isinstance(item, BaseNodeItem):
                        _node_ids.append(item.id)

                # emit the node selection signals.
                if _node_ids:
                    prev_ids = [
                        n.id for n in self._prevSelectionNodes
                        if not n.selected
                    ]
                    self.sigNodeSelected.emit(_node_ids[0])
                    self.sigNodeSelectionChanged.emit(_node_ids, prev_ids)

                self.scene().update(_map_rect)
                return

        # find position changed nodes and emit signal.
        _moved_nodes = {
            n: xy_pos for n, xy_pos in self._nodePositions.items()
            if n.xy_pos != xy_pos
        }
        # only emit of node is not colliding with a pipe.
        if _moved_nodes and not self.COLLIDINGState:
            self.sigMovedNodes.emit(_moved_nodes)

        # reset recorded positions.
        self._nodePositions = {}

        # emit signal if selected node collides with pipe.
        # Note: if collide state is true then only 1 node is selected.
        _nodes, _pipes = self.get_selected_items()
        if self.COLLIDINGState and _nodes and _pipes:
            self.sigNodeInserted.emit(_pipes[0], _nodes[0].id, _moved_nodes)

        # emit node selection changed signal.
        _prev_ids = [n.id for n in self._prevSelectionNodes if not n.selected]
        _node_ids = [n.id for n in _nodes if n not in self._prevSelectionNodes]
        self.sigNodeSelectionChanged.emit(_node_ids, _prev_ids)

        super(NodeGraphView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.ALTState and self.SHIFTState:
            if self.LMBState and self._SLICER_PIPE.isVisible():
                _p1 = self._SLICER_PIPE.path().pointAtPercent(0)
                _p2 = self.mapToScene(self._previousPos)
                self._SLICER_PIPE.draw_path(_p1, _p2)
                self._SLICER_PIPE.show()
            self._previousPos = event.pos()
            super(NodeGraphView, self).mouseMoveEvent(event)
            return

        if self.MMBState and self.ALTState:
            _pos_x = (event.x() - self._previousPos.x())
            _zoom = 0.1 if _pos_x > 0 else -0.1
            self._set_view_zoom(_zoom, 0.05, pos=event.pos())
        elif self.MMBState or (self.LMBState and self.ALTState):
            if self.cursor() != QtCore.Qt.CursorShape.ClosedHandCursor:
                self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            _previous_pos = self.mapToScene(self._previousPos)
            _current_pos = self.mapToScene(event.pos())
            _delta = _previous_pos - _current_pos
            self._set_viewer_pan(_delta.x(), _delta.y())

        if self.LMBState and self._rubberBand.isActive:
            _rect = QtCore.QRect(self._originPos, event.pos()).normalized()
            # if the rubber band is too small, do not show it.
            if max(_rect.width(), _rect.height()) > 5:
                if not self._rubberBand.isVisible():
                    self._rubberBand.show()
                _map_rect = self.mapToScene(_rect).boundingRect()
                _path = QtGui.QPainterPath()
                _path.addRect(_map_rect)
                self._rubberBand.setGeometry(_rect)
                self.scene().setSelectionArea(
                    _path,
                    QtCore.Qt.ItemSelectionOperation.ReplaceSelection,
                    QtCore.Qt.ItemSelectionMode.IntersectsItemShape
                )
                self.scene().update(_map_rect)
                self.sigSceneUpdate.emit(self)
                if self.SHIFTState or self.CTRLState:
                    _nodes, _pipes = self.get_selected_items()

                    for node in self._prevSelectionNodes:
                        node.selected = True

                    if self.CTRLState:
                        for pipe in _pipes:
                            pipe.setSelected(False)
                        for node in _nodes:
                            node.selected = False

        elif self.LMBState:
            self.COLLIDINGState = False
            _nodes, _pipes = self.get_selected_items()
            if len(_nodes) == 1:
                node = _nodes[0]
                [p.setSelected(False) for p in _pipes]

                if self.pipeCollision:
                    _colliding_pipes = [
                        i for i in node.collidingItems()
                        if isinstance(i, PipeItem) and i.isVisible()
                    ]
                    for pipe in _colliding_pipes:
                        if not pipe.input_port:
                            continue
                        _port_node_check = all([
                            not pipe.input_port.node is node,
                            not pipe.output_port.node is node
                        ])
                        if _port_node_check:
                            pipe.setSelected(True)
                            self.COLLIDINGState = True
                            break

        self._previousPos = event.pos()
        super(NodeGraphView, self).mouseMoveEvent(event)

    def wheelEvent(self, event):
        try:
            _delta = event.delta()
        except AttributeError:
            # For PyQt5
            _delta = event.angleDelta().y()
            if _delta == 0:
                _delta = event.angleDelta().x()
        self._set_view_zoom(_delta, pos=event.position().toPoint())

    def dropEvent(self, event):
        _pos = self.mapToScene(event.pos())
        event.setDropAction(QtCore.Qt.DropAction.CopyAction)
        self.sigDataDropped.emit(
            event.mimeData(), QtCore.QPoint(_pos.x(), _pos.y()))

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        """
        Key press event re-implemented to update the states for attributes:
        - ALT_state
        - CTRL_state
        - SHIFT_state

        Args:
            event (QtGui.QKeyEvent): key event.
        """
        self.ALTState = event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier
        self.CTRLState = event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier
        self.SHIFTState = event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier

        # Todo: find a better solution to catch modifier keys.
        if event.modifiers() == (QtCore.Qt.KeyboardModifier.AltModifier | QtCore.Qt.KeyboardModifier.ShiftModifier):
            self.ALTState = True
            self.SHIFTState = True

        super(NodeGraphView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """
        Key release event re-implemented to update the states for attributes:
        - ALT_state
        - CTRL_state
        - SHIFT_state

        Args:
            event (QtGui.QKeyEvent): key event.
        """
        self.ALTState = event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier
        self.CTRLState = event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier
        self.SHIFTState = event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier
        super(NodeGraphView, self).keyReleaseEvent(event)

    # ----------------------------------------------------------
    # scene events
    # ----------------------------------------------------------
    def sceneMouseMoveEvent(self, event):
        """
        triggered mouse move event for the scene.
         - redraw the connection pipe.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        if self._PIPE_HANDLE:
            _pos = event.scenePos()
            print(_pos-self._pipeHandleStartPos)
        else:
            if not self._LIVE_PIPE.isVisible():
                return
            if not self._startPort:
                return
            _pos = event.scenePos()
            _items = self.scene().items(_pos)
            if _items and isinstance(_items[0], PortItem):
                _x = _items[0].boundingRect().width() / 2
                _y = _items[0].boundingRect().height() / 2
                _pos = _items[0].scenePos()
                _pos.setX(_pos.x() + _x)
                _pos.setY(_pos.y() + _y)
            self._LIVE_PIPE.draw_path(self._startPort, cursor_pos=_pos)

    def sceneMousePressEvent(self, event):
        """
        triggered mouse press event for the scene (takes priority over viewer event).
         - detect selected pipe and start connection.
         - remap Shift and Ctrl modifier.

        Args:
            event (QtWidgets.QGraphicsScenePressEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        # pipe slicer enabled.
        if self.ALTState and self.SHIFTState:
            return

        # viewer pan mode.
        if self.ALTState:
            return

        if self._LIVE_PIPE.isVisible():
            self.apply_live_connection(event)
            return

        _pos = event.scenePos()
        _items = self._items_near(_pos, None, 5, 5)
        # modified:---------->add pipeHandle
        # filter from the selection stack in the following order
        # "node, port, pipe" this is to avoid selecting items under items.
        from ..graphics.class_pipe_item import PipeHandle
        _node, _port, _pipe, _pipe_handle = None, None, None, None
        for item in _items:
            if isinstance(item, BaseNodeItem):
                _node = item
            elif isinstance(item, PortItem):
                _port = item
            elif isinstance(item, PipeItem):
                _pipe = item
            elif isinstance(item, PipeHandle):
                 _pipe_handle = item
            if any([_node, _port, _pipe, _pipe_handle]):
                break

        if _port:
            if _port.locked:
                return

            if not _port.multi_connection and _port.connected_ports:
                self._detachedPort = _port.connected_ports[0]
            self.start_live_connection(_port)
            if not _port.multi_connection:
                [p.delete() for p in _port.connected_pipes]
            return

        if _node:
            _node_items = self._items_near(_pos, BaseNodeItem, 3, 3)

            # record the node positions at selection time.
            for n in _node_items:
                self._nodePositions[n] = n.xy_pos

            # emit selected node id with LMB.
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.sigNodeSelected.emit(_node.id)

            if not isinstance(_node, BackdropNodeItem):
                return

        if _pipe:

            if not self.LMBState:
                return

            _from_port = _pipe.get_port_at(_pos, True)

            if _from_port.locked:
                return

            _from_port.hovered = True

            _attr = {
                EnumPortType.IN.value: 'output_port',
                EnumPortType.OUT.value: 'input_port'
            }
            self._detachedPort = getattr(_pipe, _attr[_from_port.port_type])
            self.start_live_connection(_from_port)
            self._LIVE_PIPE.draw_path(self._startPort, cursor_pos=_pos)

            if self.SHIFTState:
                self._LIVE_PIPE.shift_selected = True
                return

            _pipe.delete()
        if _pipe_handle:
            self._PIPE_HANDLE = _pipe_handle
            self._pipeHandleStartPos=_pos

    def sceneMouseReleaseEvent(self, event):
        """
        triggered mouse release event for the scene.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        if event.button() != QtCore.Qt.MouseButton.MiddleButton:
            self.apply_live_connection(event)
        self._PIPE_HANDLE = None

    # --- port connections ---

    def apply_live_connection(self, event):
        """
        triggered mouse press/release event for the scene.
        - verifies the live connection pipe.
        - makes a connection pipe if valid.
        - emits the "connection changed" signal.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        if not self._LIVE_PIPE.isVisible():
            return

        self._startPort.hovered = False

        # find the end port.
        _end_port = None
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, PortItem):
                _end_port = item
                break

        _connected = []
        _disconnected = []

        # if port disconnected from existing pipe.
        if _end_port is None:
            if self._detachedPort and not self._LIVE_PIPE.shiftSelected:
                _dist = math.hypot(self._previousPos.x() - self._originPos.x(),
                                   self._previousPos.y() - self._originPos.y())
                if _dist <= 2.0:  # cursor pos threshold.
                    self.establish_connection(self._startPort,
                                              self._detachedPort)
                    self._detachedPort = None
                else:
                    _disconnected.append((self._startPort, self._detachedPort))
                    self.sigConnectionChanged.emit(_disconnected, _connected)

            self._detachedPort = None
            self.end_live_connection()
            return

        else:
            if self._startPort is _end_port:
                return

        # restore connection check.
        _restore_connection = any([
            # if the end port is locked.
            _end_port.locked,
            # if same port type.
            _end_port.port_type == self._startPort.port_type,
            # if connection to itself.
            _end_port.node == self._startPort.node,
            # if end port is the start port.
            _end_port == self._startPort,
            # if detached port is the end port.
            self._detachedPort == _end_port
        ])
        if _restore_connection:
            if self._detachedPort:
                _to_port = self._detachedPort or _end_port
                self.establish_connection(self._startPort, _to_port)
                self._detachedPort = None
            self.end_live_connection()
            return

        # end connection if starting port is already connected.
        if self._startPort.multi_connection and \
                self._startPort in _end_port.connected_ports:
            self._detachedPort = None
            self.end_live_connection()
            return

        # register as disconnected if not acyclic.
        if self.acyclic and not self.acyclic_check(self._startPort, _end_port):
            if self._detachedPort:
                _disconnected.append((self._startPort, self._detachedPort))

            self.sigConnectionChanged.emit(_disconnected, _connected)

            self._detachedPort = None
            self.end_live_connection()
            return

        # make connection.
        if not _end_port.multi_connection and _end_port.connected_ports:
            _dettached_end = _end_port.connected_ports[0]
            _disconnected.append((_end_port, _dettached_end))

        if self._detachedPort:
            _disconnected.append((self._startPort, self._detachedPort))

        _connected.append((self._startPort, _end_port))

        self.sigConnectionChanged.emit(_disconnected, _connected)

        self._detachedPort = None
        self.end_live_connection()

    def start_live_connection(self, selected_port):
        """
        create new pipe for the connection.
        (show the live pipe visibility from the port following the cursor position)
        """
        if not selected_port:
            return
        self._startPort = selected_port
        if self._startPort.type == EnumPortType.IN.value:
            self._LIVE_PIPE.input_port = self._startPort
        elif self._startPort == EnumPortType.OUT.value:
            self._LIVE_PIPE.output_port = self._startPort
        self._LIVE_PIPE.setVisible(True)

    def end_live_connection(self):
        """
        delete live connection pipe and reset start port.
        (hides the pipe item used for drawing the live connection)
        """
        self._LIVE_PIPE.reset_path()
        self._LIVE_PIPE.setVisible(False)
        self._LIVE_PIPE.shift_selected = False
        self._startPort = None

    def establish_connection(self, start_port, end_port):
        """
        establish a new pipe connection.
        (adds a new pipe item to draw between 2 ports)
        """
        _pipe = PipeItem()
        self.scene().addItem(_pipe)
        _pipe.set_connections(start_port, end_port)
        _pipe.draw_path(_pipe.input_port, _pipe.output_port)
        if start_port.node.selected or end_port.node.selected:
            _pipe.highlight()
        if not start_port.node.visible or not end_port.node.visible:
            _pipe.hide()

    @staticmethod
    def acyclic_check(start_port, end_port):
        """
        Validate the node connections so it doesn't loop itself.

        Args:
            start_port (PortItem): port item.
            end_port (PortItem): port item.

        Returns:
            bool: True if port connection is valid.
        """
        _start_node = start_port.node
        _check_nodes = [end_port.node]
        _io_types = {
            EnumPortType.IN.value: 'outputs',
            EnumPortType.OUT.value: 'inputs'
        }
        while _check_nodes:
            _check_node = _check_nodes.pop(0)
            for check_port in getattr(_check_node, _io_types[end_port.port_type]):
                if check_port.connected_ports:
                    for port in check_port.connected_ports:
                        if port.node != _start_node:
                            _check_nodes.append(port.node)
                        else:
                            return False
        return True

    # ----------------------------------------------------------
    # view handle
    # ----------------------------------------------------------

    def tab_search_set_nodes(self, nodes):
        self._searchWidget.set_nodes(nodes)

    def tab_search_toggle(self):
        _state = self._searchWidget.isVisible()
        if not _state:
            self._searchWidget.setVisible(_state)
            self.setFocus()
            return

        _pos = self._previousPos
        _rect = self._searchWidget.rect()
        _new_pos = QtCore.QPoint(int(_pos.x() - _rect.width() / 2),
                                 int(_pos.y() - _rect.height() / 2))
        self._searchWidget.move(_new_pos)
        self._searchWidget.setVisible(_state)
        self._searchWidget.setFocus()

        _rect = self.mapToScene(_rect).boundingRect()
        self.scene().update(_rect)

    def rebuild_tab_search(self):
        if isinstance(self._searchWidget, SearchMenuWidget):
            self._searchWidget.rebuild = True

    def qaction_for_undo(self):
        """
        Get the undo QAction from the parent undo stack.

        Returns:
            QtWidgets.QAction: undo action.
        """
        return self._undoAction

    def qaction_for_redo(self):
        """
        Get the redo QAction from the parent undo stack.

        Returns:
            QtWidgets.QAction: redo action.
        """
        return self._redoAction

    def get_context_menus(self):
        """
        All the available context menus for the viewer.

        Returns:
            dict: viewer context menu.
        """
        return {'graph': self._ctxGraphMenu, 'nodes': self._ctxNodeMenu}

    def question_dialog(self, text, title='Node Graph'):
        """
        Prompt node viewer question dialog widget with "yes", "no" buttons.

        Args:
            text (str): dialog text.
            title (str): dialog window title.

        Returns:
            bool: true if user click yes.
        """
        self.clear_key_state()
        return FeedbackDialog.question_dialog(text, title)

    def message_dialog(self, text, title='Node Graph'):
        """
        Prompt node viewer message dialog widget with "ok" button.

        Args:
            text (str): dialog text.
            title (str): dialog window title.
        """
        self.clear_key_state()
        FeedbackDialog.message_dialog(text, title)

    def load_dialog(self, current_dir=None, ext=None):
        """
        Prompt node viewer file load dialog widget.

        Args:
            current_dir (str): directory path starting point. (optional)
            ext (str): custom file extension filter type. (optional)

        Returns:
            str: selected file path.
        """
        self.clear_key_state()
        ext = '*{} '.format(ext) if ext else ''
        ext_filter = ';;'.join([
            'Node Graph ({}*json)'.format(ext), 'All Files (*)'
        ])
        file_dlg = FileDialog.getOpenFileName(
            self, 'Open File', current_dir, ext_filter)
        file = file_dlg[0] or None
        return file

    def save_dialog(self, current_dir=None, ext=None):
        """
        Prompt node viewer file save dialog widget.

        Args:
            current_dir (str): directory path starting point. (optional)
            ext (str): custom file extension filter type. (optional)

        Returns:
            str: selected file path.
        """
        self.clear_key_state()
        ext_label = '*{} '.format(ext) if ext else ''
        ext_type = '.{}'.format(ext) if ext else '.json'
        ext_map = {'Node Graph ({}*json)'.format(ext_label): ext_type,
                   'All Files (*)': ''}
        file_dlg = FileDialog.getSaveFileName(
            self, 'Save Session', current_dir, ';;'.join(ext_map.keys()))
        file_path = file_dlg[0]
        if not file_path:
            return
        ext = ext_map[file_dlg[1]]
        if ext and not file_path.endswith(ext):
            file_path += ext

        return file_path

    def get_all_pipes(self):
        """
        Returns all pipe qgraphic items.

        Returns:
            list[PipeItem]: instances of pipe items.
        """
        _excl = [self._LIVE_PIPE, self._SLICER_PIPE]
        return [i for i in self.scene().items()
                if isinstance(i, PipeItem) and i not in _excl]

    def get_all_nodes(self):
        """
        Returns all node qgraphic items.

        Returns:
            list[AbstractNodeItem]: instances of node items.
        """
        return [i for i in self.scene().items()
                if isinstance(i, BaseNodeItem)]

    def get_selected_nodes(self):
        """
        Returns selected node qgraphic items.

        Returns:
            list[AbstractNodeItem]: instances of node items.
        """
        return [i for i in self.scene().selectedItems()
                if isinstance(i, BaseNodeItem)]

    def get_selected_pipes(self):
        """
        Returns selected pipe qgraphic items.

        Returns:
            list[Pipe]: pipe items.
        """
        _pipes = [i for i in self.scene().selectedItems()
                  if isinstance(i, PipeItem)]
        return _pipes

    def get_selected_items(self):
        """
        Return selected graphic items in the scene.

        Returns:
            tuple(list[AbstractNodeItem], list[Pipe]):
                selected (node items, pipe items).
        """
        # todo: code redundant
        _nodes = []
        _pipes = []
        for item in self.scene().selectedItems():
            if isinstance(item, BaseNodeItem):
                _nodes.append(item)
            elif isinstance(item, PipeItem):
                _pipes.append(item)
        return _nodes, _pipes

    def add_node(self, node, pos=None):
        """
        Add node item into the scene.

        Args:
            node (AbstractNodeItem): node item instance.
            pos (tuple or list): node scene position.
        """
        pos = pos or (self._previousPos.x(), self._previousPos.y())
        node.pre_init(self, pos)
        self.scene().addItem(node)
        node.post_init(self, pos)

    @staticmethod
    def remove_node(node):
        """
        Remove node item from the scene.

        Args:
            node (AbstractNodeItem): node item instance.
        """
        if isinstance(node, BaseNodeItem):
            node.delete()

    def move_nodes(self, nodes, pos=None, offset=None):
        """
        Globally move specified nodes.

        Args:
            nodes (list[AbstractNodeItem]): node items.
            pos (tuple or list): custom x, y position.
            offset (tuple or list): x, y position offset.
        """
        _group = self.scene().createItemGroup(nodes)
        _group_rect = _group.boundingRect()
        if pos:
            _x, _y = pos
        else:
            pos = self.mapToScene(self._previousPos)
            _x = pos.x() - _group_rect.center().x()
            _y = pos.y() - _group_rect.center().y()
        if offset:
            _x += offset[0]
            _y += offset[1]
        _group.setPos(_x, _y)
        self.scene().destroyItemGroup(_group)
        self.sigSceneUpdate.emit(self)

    def get_pipes_from_nodes(self, nodes=None):
        nodes = nodes or self.get_selected_nodes()
        if not nodes:
            return
        _pipes = []
        for node in nodes:
            _n_inputs = node.inputs if hasattr(node, 'inputs') else []
            _n_outputs = node.outputs if hasattr(node, 'outputs') else []

            for port in _n_inputs:
                for pipe in port.connected_pipes:
                    connected_node = pipe.output_port.node
                    if connected_node in nodes:
                        _pipes.append(pipe)
            for port in _n_outputs:
                for pipe in port.connected_pipes:
                    connected_node = pipe.input_port.node
                    if connected_node in nodes:
                        _pipes.append(pipe)
        return _pipes

    def center_selection(self, nodes=None):
        """
        Center on the given nodes or all nodes by default.

        Args:
            nodes (list[AbstractNodeItem]): a list of node items.
        """
        if not nodes:
            if self.get_selected_nodes():
                nodes = self.get_selected_nodes()
            elif self.get_all_nodes():
                nodes = self.get_all_nodes()
            if not nodes:
                return

        if len(nodes) == 1:
            self.centerOn(nodes[0])
        else:
            _rect = self._combined_rect(nodes)
            self.centerOn(_rect.center().x(), _rect.center().y())

    def get_pipe_layout(self):
        """
        Returns the pipe layout mode.

        Returns:
            int: pipe layout mode.
        """
        return self._pipeLayout

    def set_pipe_layout(self, layout):
        """
        Sets the pipe layout mode and redraw all pipe items in the scene.

        Args:
            layout (int): pipe layout mode. (see the constants module)
        """
        self._pipeLayout = layout
        for pipe in self.get_all_pipes():
            pipe.draw_path(pipe.input_port, pipe.output_port)

    def get_layout_direction(self):
        """
        Returns the layout direction set on the the node graph viewer
        used by the pipe items for drawing.

        Returns:
            int: graph layout mode.
        """
        return self._layoutDirection

    def set_layout_direction(self, direction):
        """
        Sets the node graph viewer layout direction for re-drawing
        the pipe items.

        Args:
            direction (int): graph layout direction.
        """
        self._layoutDirection = direction
        for pipe_item in self.get_all_pipes():
            pipe_item.draw_path(pipe_item.input_port, pipe_item.output_port)

    def reset_zoom(self, cent=None):
        """
        Reset the viewer zoom level.

        Args:
            cent (QtCore.QPoint): specified center.
        """
        self._sceneRange = QtCore.QRectF(0, 0,
                                         self.size().width(),
                                         self.size().height())
        if cent:
            self._sceneRange.translate(cent - self._sceneRange.center())
        self._update_scene()

    def get_zoom(self):
        """
        Returns the viewer zoom level.

        Returns:
            float: zoom level.
        """
        _transform = self.transform()
        _cur_scale = (_transform.m11(), _transform.m22())
        return float('{:0.2f}'.format(_cur_scale[0] - 1.0))

    def set_zoom(self, value=0.0):
        """
        Set the viewer zoom level.

        Args:
            value (float): zoom level
        """
        if value == 0.0:
            self.reset_zoom()
            return
        _zoom = self.get_zoom()
        if _zoom < 0.0:
            if not (ZOOM_MIN <= _zoom <= ZOOM_MAX):
                return
        else:
            if not (ZOOM_MIN <= value <= ZOOM_MAX):
                return
        value = value - _zoom
        self._set_view_zoom(value, 0.0)

    def zoom_to_nodes(self, nodes):
        self._sceneRange = self._combined_rect(nodes)
        self._update_scene()

        if self.get_zoom() > 0.1:
            self.reset_zoom(self._sceneRange.center())

    def force_update(self):
        """
        Redraw the current node graph scene.
        """
        self._update_scene()

    def get_scene_rect(self):
        """
        Returns the scene rect size.

        Returns:
            list[float]: x, y, width, height
        """
        return [self._sceneRange.x(), self._sceneRange.y(),
                self._sceneRange.width(), self._sceneRange.height()]

    def set_scene_rect(self, rect):
        """
        Sets the scene rect and redraws the scene.

        Args:
            rect (list[float]): x, y, width, height
        """
        self._sceneRange = QtCore.QRectF(*rect)
        self._update_scene()

    def get_scene_center(self):
        """
        Get the center x,y pos from the scene.

        Returns:
            list[float]: x, y position.
        """
        _cent = self._sceneRange.center()
        return [_cent.x(), _cent.y()]

    def get_nodes_rect_center(self, nodes):
        """
        Get the center x,y pos from the specified nodes.

        Args:
            nodes (list[AbstractNodeItem]): list of node qgrphics items.

        Returns:
            list[float]: x, y position.
        """
        _cent = self._combined_rect(nodes).center()
        return [_cent.x(), _cent.y()]

    def clear_key_state(self):
        """
        Resets the Ctrl, Shift, Alt modifiers key states.
        """
        self.CTRLState = False
        self.SHIFTState = False
        self.ALTState = False

    def use_OpenGL(self):
        """
        Use QOpenGLWidget as the viewer.
        """
        # use QOpenGLWidget instead of the deprecated QGLWidget to avoid
        # problems with Wayland.
        self.setViewport(QtOpenGLWidgets.QOpenGLWidget())
