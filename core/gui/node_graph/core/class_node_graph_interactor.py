# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_node_graph_interactor.py
# ------------------------------------------------------------------------------
#
# File          : class_node_graph_interactor.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import typing, math
from core.gui.qtimp import QtGui, QtCore, QtWidgets
from ..views.class_base_node_view_item import BaseNodeViewItem
from ..views.class_search_widget import SearchMenuWidget
from ..views.class_pipe_view_item import LivePipeItem, PipeViewItem
from ..views.class_slicer_item import PipeSlicerItem

if typing.TYPE_CHECKING:
    from ..views.class_node_graph_view import NodeGraphView


class NodeGraphBaseInteractor:
    def __init__(self, view: 'NodeGraphView'):
        self.view = view

        self._rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Shape.Rectangle, self.view)
        self._rubberBand.isActive = False

        self._livePipe = LivePipeItem()
        self._livePipe.setVisible(False)
        self.view.scene().addItem(self._livePipe)

        self._pipeHandle = None
        self._pipeHandleStartPos = QtCore.QPoint(0, 0)

        self._pipeSlicer = PipeSlicerItem()
        self._pipeSlicer.setVisible(False)
        self.view.scene().addItem(self._pipeSlicer)
        self.previousCursor = self.view.cursor()
        self.originPos = None
        self.previousPos = QtCore.QPoint(int(self.view.width() / 2),
                                         int(self.view.height() / 2))
        self.prevSelectionNodes = []
        self.prevSelectionPipes = []
        self.nodePositions = {}
        self.LMBState = False
        self.RMBState = False
        self.MMBState = False
        self.ALTState = False
        self.CTRLState = False
        self.SHIFTState = False
        self.COLLIDINGState = False

    @property
    def view_class(self):
        return self.view.__class__

    @property
    def no_exposed_pipes(self):
        return [self._livePipe, self._pipeSlicer]

    def on_pipes_sliced(self, path):
        """
        Triggered when the slicer pipe is active

        Args:
            path (QtGui.QPainterPath): slicer path.
        """
        _ports = []
        for i in self.view.scene().items(path):
            if isinstance(i, PipeViewItem) and i != self._livePipe:
                if any([i.input_port.locked, i.output_port.locked]):
                    continue
                _ports.append([i.input_port, i.output_port])
        self.view.sigConnectionSliced.emit(_ports)

    def on_focus_in(self, event: QtGui.QFocusEvent):
        pass

    def on_focus_out(self, event: QtGui.QFocusEvent):
        pass

    def on_context_menu_event(self, evt):
        self.RMBState = False

    def on_mouse_press(self, event):
        self.previousCursor = self.view.cursor()
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.LMBState = True
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.RMBState = True
        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.MMBState = True

        self.originPos = event.pos()
        self.previousPos = event.pos()
        (self.prevSelectionNodes, self.prevSelectionPipes) = self.view.get_selected_items_all_type()

        # cursor pos.
        _map_pos = self.view.mapToScene(event.pos())

        # pipe slicer enabled.
        _slicer_mode = all([self.ALTState, self.SHIFTState, self.LMBState])
        if _slicer_mode:
            self._pipeSlicer.draw_path(_map_pos, _map_pos)
            self._pipeSlicer.setVisible(True)
            return

        # pan mode.
        if self.ALTState:
            self.view.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
            return

        _items = self.view.get_items_near(_map_pos, None, 20, 20)
        _items = [i for i in _items if isinstance(i, BaseNodeViewItem)]
        # pipes = [i for i in items if isinstance(i, PipeItem)]

        if _items:
            self.MMBState = False

        # toggle extend node selection.
        if self.LMBState:
            if self.SHIFTState:
                for item in _items:
                    item.selected = not item.selected
            elif self.CTRLState:
                for item in _items:
                    item.selected = False

        # update the recorded node positions.
        self.nodePositions.update({n: n.xy_pos for n in self.view.get_selected_items()})
        # show selection selection marquee.
        if self.LMBState and not _items:
            _rect = QtCore.QRect(self.previousPos, QtCore.QSize())
            _rect = _rect.normalized()
            _map_rect = self.view.mapToScene(_rect).boundingRect()
            self.view.scene().update(_map_rect)
            self._rubberBand.setGeometry(_rect)
            self._rubberBand.isActive = True

        if self.LMBState and (self.SHIFTState or self.CTRLState):
            return

        if not self._livePipe.isVisible():
            return

    def on_mouse_release(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.LMBState = False
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.RMBState = False
        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.MMBState = False
        self.view.setCursor(self.previousCursor)
        # hide pipe slicer.
        if self._pipeSlicer.isVisible():
            self.on_pipes_sliced(self._pipeSlicer.path())
            _p = QtCore.QPointF(0.0, 0.0)
            self._pipeSlicer.draw_path(_p, _p)
            self._pipeSlicer.setVisible(False)

        # hide selection marquee
        if self._rubberBand.isActive:
            self._rubberBand.isActive = False
            if self._rubberBand.isVisible():
                _rect = self._rubberBand.rect()
                _map_rect = self.view.mapToScene(_rect).boundingRect()
                self._rubberBand.hide()

                _rect = QtCore.QRect(self.originPos, event.pos()).normalized()
                _rect_items = self.view.scene().items(
                    self.view.mapToScene(_rect).boundingRect()
                )
                _node_ids = []
                for item in _rect_items:
                    if isinstance(item, BaseNodeViewItem):
                        _node_ids.append(item.id)

                # emit the node selection signals.
                if _node_ids:
                    _prev_ids = [n.id for n in self.prevSelectionNodes if not n.selected]
                    self.view.sigNodeSelected.emit(_node_ids[0])
                    self.view.sigNodeSelectionChanged.emit(_node_ids, _prev_ids)

                self.view.scene().update(_map_rect)
                return

        # find position changed nodes and emit signal.
        _moved_nodes = {n: xy_pos for n, xy_pos in self.nodePositions.items() if n.xy_pos != xy_pos}
        # only emit of node is not colliding with a pipe.
        if _moved_nodes and not self.COLLIDINGState:
            self.view.sigMovedNodes.emit(_moved_nodes)
        # reset recorded positions.
        self.nodePositions = {}

        # emit signal if selected node collides with pipe.
        # Note: if collide state is true then only 1 node is selected.
        _nodes, _pipes = self.view.get_selected_items_all_type()
        if self.COLLIDINGState and _nodes and _pipes:
            self.view.sigNodeInserted.emit(_pipes[0], _nodes[0].id, _moved_nodes)

        # emit node selection changed signal.
        _prev_ids = [n.id for n in self.prevSelectionNodes if not n.isSelected()]
        _node_ids = [n.id for n in _nodes if n not in self.prevSelectionNodes]
        self.view.sigNodeSelectionChanged.emit(_node_ids, _prev_ids)

    def on_mouse_move(self, event):
        if self.ALTState and self.SHIFTState:
            if self.LMBState and self._pipeSlicer.isVisible():
                _p1 = self._pipeSlicer.path().pointAtPercent(0)
                _p2 = self.view.mapToScene(self.previousPos)
                self._pipeSlicer.draw_path(_p1, _p2)
                self._pipeSlicer.show()
            self.previousPos = event.pos()
            return

        if self.MMBState and self.ALTState:
            _pos_x = (event.x() - self.previousPos.x())
            _zoom = 0.1 if _pos_x > 0 else -0.1
            self.view.set_view_zoom(_zoom, 0.05, pos=event.pos())
        elif self.MMBState or (self.LMBState and self.ALTState):
            if self.view.cursor() != QtCore.Qt.CursorShape.ClosedHandCursor:
                self.view.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            _previous_pos = self.view.mapToScene(self.previousPos)
            _current_pos = self.view.mapToScene(event.pos())
            _delta = _previous_pos - _current_pos
            self.view.set_view_pan(_delta.x(), _delta.y())

        if self.LMBState and self._rubberBand.isActive:
            _rect = QtCore.QRect(self.originPos, event.pos()).normalized()
            # if the rubber band is too small, do not show it.
            if max(_rect.width(), _rect.height()) > 5:
                if not self._rubberBand.isVisible():
                    self._rubberBand.show()
                _map_rect = self.view.mapToScene(_rect).boundingRect()
                _path = QtGui.QPainterPath()
                _path.addRect(_map_rect)
                self._rubberBand.setGeometry(_rect)
                self.view.scene().setSelectionArea(
                    _path,
                    QtCore.Qt.ItemSelectionOperation.ReplaceSelection,
                    QtCore.Qt.ItemSelectionMode.IntersectsItemShape
                )
                self.view.scene().update(_map_rect)
                self.view.sigSceneUpdate.emit(self.view)
                if self.SHIFTState or self.CTRLState:
                    _nodes, _pipes = self.view.get_selected_items()

                    for node in self.prevSelectionNodes:
                        node.selected = True

                    if self.CTRLState:
                        for pipe in _pipes:
                            pipe.setSelected(False)
                        for node in _nodes:
                            node.selected = False

        elif self.LMBState:
            self.COLLIDINGState = False
            _nodes, _pipes = self.view.get_selected_items_all_type()
            if len(_nodes) == 1:
                node = _nodes[0]
                [p.setSelected(False) for p in _pipes]

                if self.view.view_setting.pipeCollisionEnabled:
                    _colliding_pipes = [
                        i for i in node.collidingItems()
                        if isinstance(i, PipeViewItem) and i.isVisible()
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

        self.previousPos = event.pos()

    def on_wheel(self, event):
        try:
            _delta = event.delta()
        except AttributeError:
            # For PyQt5
            _delta = event.angleDelta().y()
            if _delta == 0:
                _delta = event.angleDelta().x()
        self.view.set_view_zoom(_delta, pos=event.position().toPoint())

    def on_key_press(self, event):
        self.ALTState = event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier
        self.CTRLState = event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier
        self.SHIFTState = event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier
        # Todo: find a better solution to catch modifier keys.
        if event.modifiers() == (QtCore.Qt.KeyboardModifier.AltModifier | QtCore.Qt.KeyboardModifier.ShiftModifier):
            self.ALTState = True
            self.SHIFTState = True

    def on_key_release(self, event):
        self.ALTState = event.modifiers() == QtCore.Qt.KeyboardModifier.AltModifier
        self.CTRLState = event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier
        self.SHIFTState = event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier

    def on_scene_mouse_move(self, event):
        if self._pipeHandle:
            _pos = event.scenePos()
        else:
            if not self._livePipe.isVisible():
                return
            if not self.startPort:
                return
            _pos = event.scenePos()
            _items = self.view.scene().items(_pos)
            if _items and isinstance(_items[0], PortItem):
                _x = _items[0].boundingRect().width() / 2
                _y = _items[0].boundingRect().height() / 2
                _pos = _items[0].scenePos()
                _pos.setX(_pos.x() + _x)
                _pos.setY(_pos.y() + _y)
            self._livePipe.draw_path(self.startPort, cursor_pos=_pos)

    def on_scene_mouse_press(self, event):
        # pipe slicer enabled.
        if self.ALTState and self.SHIFTState:
            return

        # viewer pan mode.
        if self.ALTState:
            return

        if self._livePipe.isVisible():
            self.apply_live_connection(event)
            return

        _pos = event.scenePos()
        _items = self.view.get_items_near(_pos, None, 5, 5)
        # modified:---------->add pipeHandle
        # filter from the selection stack in the following order
        # "node, port, pipe" this is to avoid selecting items under items.
        from ..views.class_pipe_view_item import PipeHandle
        _node, _port, _pipe, _pipe_handle = None, None, None, None
        # for item in _items:
        #     if isinstance(item, BaseNodeItem):
        #         _node = item
        #     elif isinstance(item, PortItem):
        #         _port = item
        #     elif isinstance(item, PipeItem):
        #         _pipe = item
        #     elif isinstance(item, PipeHandle):
        #         _pipe_handle = item
        #     if any([_node, _port, _pipe, _pipe_handle]):
        #         break

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
            _node_items = self.view.get_items_near(_pos, BaseNodeViewItem, 3, 3)

            # record the node positions at selection time.
            for n in _node_items:
                self.nodePositions[n] = n.xy_pos

            # emit selected node id with LMB.
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.view.sigNodeSelected.emit(_node.id)

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
            self._livePipe.draw_path(self.startPort, cursor_pos=_pos)

            if self.SHIFTState:
                self._livePipe.shift_selected = True
                return

            _pipe.delete()
        if _pipe_handle:
            self._pipeHandle = _pipe_handle
            self._pipeHandleStartPos = _pos

    def on_scene_mouse_release(self, event):
        if event.button() != QtCore.Qt.MouseButton.MiddleButton:
            self.apply_live_connection(event)
        self._pipeHandle = None

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
        if not self._livePipe.isVisible():
            return

        self.startPort.hovered = False

        # find the end port.
        _end_port = None
        for item in self.view.scene().items(event.scenePos()):
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
                    self.view.sigConnectionChanged.emit(_disconnected, _connected)

            self._detachedPort = None
            self.end_live_connection()
            return

        else:
            if self.startPort is _end_port:
                return

        # restore connection check.
        _restore_connection = any([
            # if the end port is locked.
            _end_port.locked,
            # if same port type.
            _end_port.port_type == self.startPort.port_type,
            # if connection to itself.
            _end_port.node == self.startPort.node,
            # if end port is the start port.
            _end_port == self.startPort,
            # if detached port is the end port.
            self._detachedPort == _end_port
        ])
        if _restore_connection:
            if self._detachedPort:
                _to_port = self._detachedPort or _end_port
                self.establish_connection(self.startPort, _to_port)
                self._detachedPort = None
            self.end_live_connection()
            return

        # end connection if starting port is already connected.
        if self.startPort.multi_connection and \
                self.startPort in _end_port.connected_ports:
            self._detachedPort = None
            self.end_live_connection()
            return

        # register as disconnected if not acyclic.
        if self.view.view_setting.acyclic and not self.acyclic_check(self.startPort, _end_port):
            if self._detachedPort:
                _disconnected.append((self.startPort, self._detachedPort))

            self.view.sigConnectionChanged.emit(_disconnected, _connected)

            self._detachedPort = None
            self.end_live_connection()
            return

        # make connection.
        if not _end_port.multi_connection and _end_port.connected_ports:
            _dettached_end = _end_port.connected_ports[0]
            _disconnected.append((_end_port, _dettached_end))

        if self._detachedPort:
            _disconnected.append((self.startPort, self._detachedPort))

        _connected.append((self.startPort, _end_port))

        self.view.sigConnectionChanged.emit(_disconnected, _connected)

        self._detachedPort = None
        self.end_live_connection()

    def start_live_connection(self, selected_port):
        """
        create new pipe for the connection.
        (show the live pipe visibility from the port following the cursor position)
        """
        if not selected_port:
            return
        self.startPort = selected_port
        if self.startPort.type == EnumPortType.IN.value:
            self._livePipe.input_port = self.startPort
        elif self.startPort == EnumPortType.OUT.value:
            self._livePipe.output_port = self.startPort
        self._livePipe.setVisible(True)

    def end_live_connection(self):
        """
        delete live connection pipe and reset start port.
        (hides the pipe item used for drawing the live connection)
        """
        self._livePipe.reset_path()
        self._livePipe.setVisible(False)
        self._livePipe.shift_selected = False
        self.startPort = None

    def establish_connection(self, start_port, end_port):
        """
        establish a new pipe connection.
        (adds a new pipe item to draw between 2 ports)
        """
        _pipe = PipeItem()
        self.view.scene().addItem(_pipe)
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

    def clear_key_state(self):
        """
        Resets the Ctrl, Shift, Alt modifiers key states.
        """
        self.CTRLState = False
        self.SHIFTState = False
        self.ALTState = False
