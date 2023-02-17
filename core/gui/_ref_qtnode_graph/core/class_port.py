# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_port.py
# ------------------------------------------------------------------------------
#
# File          : class_port.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .commands import (
    PortConnectedCmd,
    PortDisconnectedCmd,
    PortLockedCmd,
    PortUnlockedCmd,
    PortVisibleChangedCmd,
    NodeInputConnectedCmd,
    NodeInputDisconnectedCmd
)
from .class_model import PortModel
from .define import EnumPortType
from .exceptions import PortError


class Port(object):
    """
    The ``Port`` class is used for connecting one node to another.

    .. image:: ../_images/port.png
        :width: 50%

    See Also:
        For adding a ports into a node see:
        :meth:`BaseNode.add_input`, :meth:`BaseNode.add_output`

    Args:
        node (NodeGraphQt.NodeObject): parent node.
        port (PortItem): graphic item used for drawing.
    """

    def __init__(self, node: 'NodeObject', port: 'PortItem'):
        self.__view = port
        self.__model = PortModel(node)

    def __repr__(self):
        _port = str(self.__class__.__name__)
        return '<{}("{}") object at {}>'.format(
            _port, self.get_name(), hex(id(self)))

    @property
    def view(self):
        """
        Returns the :class:`QtWidgets.QGraphicsItem` used in the scene.

        Returns:
            NodeGraphQt.qgraphics.port.PortItem: port item.
        """
        return self.__view

    @property
    def model(self):
        """
        Returns the port model.

        Returns:
            NodeGraphQt.base.model.PortModel: port model.
        """
        return self.__model

    def type_(self):
        """
        Returns the port type.

        Port Types:
            - :attr:`NodeGraphQt.constants.IN_PORT` for input port
            - :attr:`NodeGraphQt.constants.OUT_PORT` for output port

        Returns:
            str: port connection type.
        """
        return self.model.type_

    def can_multi_connection(self):
        """
        Returns if the ports is a single connection or not.

        Returns:
            bool: false if port is a single connection port
        """
        return self.model.multiConnection

    def get_node(self):
        """
        Return the parent node.

        Returns:
            NodeGraphQt.BaseNode: parent node object.
        """
        return self.model.node

    def get_name(self):
        """
        Returns the port name.

        Returns:
            str: port name.
        """
        return self.model.name

    def is_visible(self):
        """
        Port visible in the node graph.

        Returns:
            bool: true if visible.
        """
        return self.model.visible

    def set_visible(self, visible=True):
        """
        Sets weather the port should be visible or not.

        Args:
            visible (bool): true if visible.
        """
        self.model.visible = visible
        _label = 'show' if visible else 'hide'
        _undo_stack = self.get_node().graph.get_undo_stack()
        _undo_stack.beginMacro('{} port {}'.format(_label, self.get_name()))

        for port in self.get_connected_ports():
            _undo_stack.push(PortDisconnectedCmd(self, port))

        _undo_stack.push(PortVisibleChangedCmd(self))
        _undo_stack.endMacro()

    def is_locked(self):
        """
        Returns the locked state.

        If ports are locked then new pipe connections can't be connected
        and current connected pipes can't be disconnected.

        Returns:
            bool: true if locked.
        """
        return self.model.locked

    def lock(self):
        """
        Lock the port so new pipe connections can't be connected and
        current connected pipes can't be disconnected.

        This is the same as calling :meth:`Port.set_locked` with the arg
        set to ``True``
        """
        self.set_locked(True, connected_ports=True)

    def unlock(self):
        """
        Unlock the port so new pipe connections can be connected and
        existing connected pipes can be disconnected.

        This is the same as calling :meth:`Port.set_locked` with the arg
        set to ``False``
        """
        self.set_locked(False, connected_ports=True)

    def set_locked(self, state=False, connected_ports=True, push_undo=True):
        """
        Sets the port locked state. When locked pipe connections can't be
        connected or disconnected from this port.

        Args:
            state (Bool): port lock state.
            connected_ports (Bool): apply to lock state to connected ports.
            push_undo (bool): register the command to the undo stack. (default: True)

        """
        _graph = self.get_node().graph
        _undo_stack = _graph.get_undo_stack()
        if state:
            _undo_cmd = PortLockedCmd(self)
        else:
            _undo_cmd = PortUnlockedCmd(self)
        if push_undo:
            _undo_stack.push(_undo_cmd)
        else:
            _undo_cmd.redo()
        if connected_ports:
            for port in self.get_connected_ports():
                port.set_locked(state,
                                connected_ports=False,
                                push_undo=push_undo)

    def get_connected_ports(self):
        """
        Returns all connected ports.

        Returns:
            list[NodeGraphQt.Port]: list of connected ports.
        """
        _ports = []
        _graph = self.get_node().graph
        for node_id, port_names in self.model.connectedPorts.items():
            for port_name in port_names:
                node = _graph.get_node_by_id(node_id)
                if self.type_() == EnumPortType.IN.value:
                    _ports.append(node.get_outputs()[port_name])
                elif self.type_() == EnumPortType.OUT.value:
                    _ports.append(node.get_inputs()[port_name])
        return _ports

    def connect_to(self, port=None, push_undo=True):
        """
        Create connection to the specified port and emits the
        :attr:`NodeGraph.port_connected` signal from the parent node graph.

        Args:
            port (NodeGraphQt.Port): port object.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if not port:
            return

        if self in port.get_connected_ports():
            return

        if self.is_locked() or port.is_locked():
            _name = [p.name() for p in [self, port] if p.is_locked()][0]
            raise PortError(
                'Can\'t connect port because "{}" is locked.'.format(_name))

        _graph = self.get_node().graph
        _view = _graph.get_view()

        if push_undo:
            _undo_stack = _graph.get_undo_stack()
            _undo_stack.beginMacro('connect port')

        _pre_conn_port = None
        _src_conn_ports = self.get_connected_ports()
        if not self.can_multi_connection() and _src_conn_ports:
            _pre_conn_port = _src_conn_ports[0]

        if not port:
            if _pre_conn_port:
                if push_undo:
                    _undo_stack.push(PortDisconnectedCmd(self, port))
                    _undo_stack.push(NodeInputDisconnectedCmd(self, port))
                    _undo_stack.endMacro()
                else:
                    PortDisconnectedCmd(self, port).redo()
                    NodeInputDisconnectedCmd(self, port).redo()
            return

        if _graph.is_acyclic() and _view.acyclic_check(self.view, port.view):
            if _pre_conn_port:
                if push_undo:
                    _undo_stack.push(PortDisconnectedCmd(self, _pre_conn_port))
                    _undo_stack.push(NodeInputDisconnectedCmd(
                        self, _pre_conn_port))
                    _undo_stack.endMacro()
                else:
                    PortDisconnectedCmd(self, _pre_conn_port).redo()
                    NodeInputDisconnectedCmd(self, _pre_conn_port).redo()
                return

        _trg_conn_ports = port.get_connected_ports()
        if not port.can_multi_connection() and _trg_conn_ports:
            _dettached_port = _trg_conn_ports[0]
            if push_undo:
                _undo_stack.push(PortDisconnectedCmd(port, _dettached_port))
                _undo_stack.push(NodeInputDisconnectedCmd(port, _dettached_port))
            else:
                PortDisconnectedCmd(port, _dettached_port).redo()
                NodeInputDisconnectedCmd(port, _dettached_port).redo()
        if _pre_conn_port:
            if push_undo:
                _undo_stack.push(PortDisconnectedCmd(self, _pre_conn_port))
                _undo_stack.push(NodeInputDisconnectedCmd(self, _pre_conn_port))
            else:
                PortDisconnectedCmd(self, _pre_conn_port).redo()
                NodeInputDisconnectedCmd(self, _pre_conn_port).redo()

        if push_undo:
            _undo_stack.push(PortConnectedCmd(self, port))
            _undo_stack.push(NodeInputConnectedCmd(self, port))
            _undo_stack.endMacro()
        else:
            PortConnectedCmd(self, port).redo()
            NodeInputConnectedCmd(self, port).redo()

        # emit "port_connected" signal from the parent graph.
        _ports = {p.type_(): p for p in [self, port]}
        _graph.sigPortConnected.emit(_ports[EnumPortType.IN.value],
                                     _ports[EnumPortType.OUT.value])

    def disconnect_from(self, port=None, push_undo=True):
        """
        Disconnect from the specified port and emits the
        :attr:`NodeGraph.port_disconnected` signal from the parent node graph.

        Args:
            port (NodeGraphQt.Port): port object.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if not port:
            return

        if self.is_locked() or port.is_locked():
            _name = [p.name() for p in [self, port] if p.is_locked()][0]
            raise PortError(
                'Can\'t disconnect port because "{}" is locked.'.format(_name))

        _graph = self.get_node().graph
        if push_undo:
            _graph.get_undo_stack().beginMacro('disconnect port')
            _graph.get_undo_stack().push(PortDisconnectedCmd(self, port))
            _graph.get_undo_stack().push(NodeInputDisconnectedCmd(self, port))
            _graph.get_undo_stack().endMacro()
        else:
            PortDisconnectedCmd(self, port).redo()
            NodeInputDisconnectedCmd(self, port).redo()

        # emit "port_disconnected" signal from the parent graph.
        _ports = {p.type_(): p for p in [self, port]}
        _graph.sigPortDisconnected.emit(_ports[EnumPortType.IN.value],
                                        _ports[EnumPortType.OUT.value])

    def clear_connections(self, push_undo=True):
        """
        Disconnect from all port connections and emit the
        :attr:`NodeGraph.port_disconnected` signals from the node graph.

        See Also:
            :meth:`Port.disconnect_from`,
            :meth:`Port.connect_to`,
            :meth:`Port.connected_ports`

        Args:
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if self.is_locked():
            _err = 'Can\'t clear connections because port "{}" is locked.'
            raise PortError(_err.format(self.get_name()))

        if not self.get_connected_ports():
            return

        if push_undo:
            _graph = self.get_node().graph
            _undo_stack = _graph.get_undo_stack()
            _undo_stack.beginMacro('"{}" clear connections')
            for cp in self.get_connected_ports():
                self.disconnect_from(cp)
            _undo_stack.endMacro()
        else:
            for cp in self.get_connected_ports():
                self.disconnect_from(cp, push_undo=False)

    @property
    def color(self):
        return self.__view.color

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self.__view.color = color

    @property
    def border_color(self):
        return self.__view.border_color

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self.__view.border_color = color
