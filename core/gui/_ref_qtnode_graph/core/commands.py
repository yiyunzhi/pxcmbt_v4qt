# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : commands.py
# ------------------------------------------------------------------------------
#
# File          : commands.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtGui
from .define import EnumPortType


class NodePropertyChangedCmd(QtGui.QUndoCommand):
    """
    Node property changed command.

    Args:
        node (NodeGraphQt.NodeObject): node.
        name (str): node property name.
        value (object): node property value.
    """

    def __init__(self, node, name, value):
        QtGui.QUndoCommand.__init__(self)
        if name == 'name':
            self.setText('renamed "{}" to "{}"'.format(node.get_name(), value))
        else:
            self.setText('property "{}:{}"'.format(node.get_name(), name))
        self.node = node
        self.name = name
        self.old_val = node.get_property(name)
        self.new_val = value

    def set_node_prop(self, name, value):
        """
        updates the node view and model.
        """
        # set model data.
        _model = self.node.model
        _model.set_property(name, value)

        # set view data.
        _view = self.node.view

        # view widgets.
        if hasattr(_view, 'widgets') and name in _view.widgets.keys():
            # check if previous value is identical to current value,
            # prevent signals from causing a infinite loop.
            if _view.widgets[name].get_value() != value:
                _view.widgets[name].set_value(value)

        # view properties.
        if name in _view.properties.keys():
            # remap "pos" to "xy_pos" node view has pre-existing pos method.
            if name == 'pos':
                name = 'xy_pos'
            setattr(_view, name, value)

    def undo(self):
        if self.old_val != self.new_val:
            self.set_node_prop(self.name, self.old_val)
            # emit property changed signal.
            _graph = self.node.graph
            _graph.sigPropertyChanged.emit(self.node, self.name, self.old_val)

    def redo(self):
        if self.old_val != self.new_val:
            self.set_node_prop(self.name, self.new_val)
            # emit property changed signal.
            _graph = self.node.graph
            _graph.sigPropertyChanged.emit(self.node, self.name, self.new_val)


class NodeMovedCmd(QtGui.QUndoCommand):
    """
    Node moved command.

    Args:
        node (NodeGraphQt.NodeObject): node.
        pos (tuple(float, float)): new node position.
        prev_pos (tuple(float, float)): previous node position.
    """

    def __init__(self, node, pos, prev_pos):
        QtGui.QUndoCommand.__init__(self)
        self.node = node
        self.pos = pos
        self.prev_pos = prev_pos

    def undo(self):
        self.node.view.xy_pos = self.prev_pos
        self.node.model.pos = self.prev_pos

    def redo(self):
        if self.pos == self.prev_pos:
            return
        self.node.view.xy_pos = self.pos
        self.node.model.pos = self.pos


class NodeAddedCmd(QtGui.QUndoCommand):
    """
    Node added command.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
        node (NodeGraphQt.NodeObject): node.
        pos (tuple(float, float)): initial node position (optional).
    """

    def __init__(self, graph, node, pos=None):
        QtGui.QUndoCommand.__init__(self)
        self.setText('added node')
        self.viewer = graph.get_view()
        self.model = graph.model
        self.node = node
        self.pos = pos

    def undo(self):
        self.pos = self.pos or self.node.pos()
        self.model.nodes.pop(self.node.id)
        self.node.view.delete()

    def redo(self):
        self.model.nodes[self.node.id] = self.node
        self.viewer.add_node(self.node.view, self.pos)

        # node width & height is calculated when its added to the scene
        # so we have to update the node model here.
        self.node.model.width = self.node.view.width
        self.node.model.height = self.node.view.height


class NodeRemovedCmd(QtGui.QUndoCommand):
    """
    Node deleted command.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
        node (NodeGraphQt.BaseNode or NodeGraphQt.NodeObject): node.
    """

    def __init__(self, graph, node):
        QtGui.QUndoCommand.__init__(self)
        self.setText('deleted node')
        self.scene = graph.get_scene()
        self.model = graph.model
        self.node = node

    def undo(self):
        self.model.nodes[self.node.id] = self.node
        self.scene.addItem(self.node.view)

    def redo(self):
        self.model.nodes.pop(self.node.id)
        self.node.view.delete()


class NodeInputConnectedCmd(QtGui.QUndoCommand):
    """
    "BaseNode.on_input_connected()" command.

    Args:
        src_port (NodeGraphQt.Port): source port.
        trg_port (NodeGraphQt.Port): target port.
    """

    def __init__(self, src_port, trg_port):
        QtGui.QUndoCommand.__init__(self)
        if src_port.type_() == EnumPortType.IN.value:
            self.source = src_port
            self.target = trg_port
        else:
            self.source = trg_port
            self.target = src_port

    def undo(self):
        _node = self.source.get_node()
        _node.on_input_disconnected(self.source, self.target)

    def redo(self):
        _node = self.source.get_node()
        _node.on_input_connected(self.source, self.target)


class NodeInputDisconnectedCmd(QtGui.QUndoCommand):
    """
    Node "on_input_disconnected()" command.

    Args:
        src_port (NodeGraphQt.Port): source port.
        trg_port (NodeGraphQt.Port): target port.
    """

    def __init__(self, src_port, trg_port):
        QtGui.QUndoCommand.__init__(self)
        if src_port.type_() == EnumPortType.IN.value:
            self.source = src_port
            self.target = trg_port
        else:
            self.source = trg_port
            self.target = src_port

    def undo(self):
        _node = self.source.get_node()
        _node.on_input_connected(self.source, self.target)

    def redo(self):
        _node = self.source.get_node()
        _node.on_input_disconnected(self.source, self.target)


class PortConnectedCmd(QtGui.QUndoCommand):
    """
    Port connected command.

    Args:
        src_port (NodeGraphQt.Port): source port.
        trg_port (NodeGraphQt.Port): target port.
    """

    def __init__(self, src_port, trg_port):
        QtGui.QUndoCommand.__init__(self)
        self.source = src_port
        self.target = trg_port

    def undo(self):
        _src_model = self.source.model
        _trg_model = self.target.model
        _src_id = self.source.get_node().id
        _trg_id = self.target.get_node().id

        _port_names = _src_model.connectedPorts.get(_trg_id)
        if _port_names is []:
            del _src_model.connectedPorts[_trg_id]
        if _port_names and self.target.get_name() in _port_names:
            _port_names.remove(self.target.get_name())

        _port_names = _trg_model.connectedPorts.get(_src_id)
        if _port_names is []:
            del _trg_model.connectedPorts[_src_id]
        if _port_names and self.source.get_name() in _port_names:
            _port_names.remove(self.source.get_name())

        self.source.view.disconnect_from(self.target.view)

    def redo(self):
        _src_model = self.source.model
        _trg_model = self.target.model
        _src_id = self.source.get_node().id
        _trg_id = self.target.get_node().id

        _src_model.connectedPorts[_trg_id].append(self.target.get_name())
        _trg_model.connectedPorts[_src_id].append(self.source.get_name())

        self.source.view.connect_to(self.target.view)


class PortDisconnectedCmd(QtGui.QUndoCommand):
    """
    Port disconnected command.

    Args:
        src_port (NodeGraphQt.Port): source port.
        trg_port (NodeGraphQt.Port): target port.
    """

    def __init__(self, src_port, trg_port):
        QtGui.QUndoCommand.__init__(self)
        self.source = src_port
        self.target = trg_port

    def undo(self):
        _src_model = self.source.model
        _trg_model = self.target.model
        _src_id = self.source.get_node().id
        _trg_id = self.target.get_node().id

        _src_model.connectedPorts[_trg_id].append(self.target.get_name())
        _trg_model.connectedPorts[_src_id].append(self.source.get_name())

        self.source.view.connect_to(self.target.view)

    def redo(self):
        _src_model = self.source.model
        _trg_model = self.target.model
        _src_id = self.source.get_node().id
        _trg_id = self.target.get_node().id

        _port_names = _src_model.connectedPorts.get(_trg_id)
        if _port_names is []:
            del _src_model.connectedPorts[_trg_id]
        if _port_names and self.target.get_name() in _port_names:
            _port_names.remove(self.target.get_name())

        _port_names = _trg_model.connectedPorts.get(_src_id)
        if _port_names is []:
            del _trg_model.connectedPorts[_src_id]
        if _port_names and self.source.get_name() in _port_names:
            _port_names.remove(self.source.get_name())

        self.source.view.disconnect_from(self.target.view)


class PortLockedCmd(QtGui.QUndoCommand):
    """
    Port locked command.

    Args:
        port (NodeGraphQt.Port): node port.
    """

    def __init__(self, port):
        QtGui.QUndoCommand.__init__(self)
        self.setText('lock port "{}"'.format(port.name()))
        self.port = port

    def undo(self):
        self.port.model.locked = False
        self.port.view.locked = False

    def redo(self):
        self.port.model.locked = True
        self.port.view.locked = True


class PortUnlockedCmd(QtGui.QUndoCommand):
    """
    Port unlocked command.

    Args:
        port (NodeGraphQt.Port): node port.
    """

    def __init__(self, port):
        QtGui.QUndoCommand.__init__(self)
        self.setText('unlock port "{}"'.format(port.get_name()))
        self.port = port

    def undo(self):
        self.port.model.locked = True
        self.port.view.locked = True

    def redo(self):
        self.port.model.locked = False
        self.port.view.locked = False


class PortVisibleChangedCmd(QtGui.QUndoCommand):
    """
    Port visibility command.

    Args:
        port (NodeGraphQt.Port): node port.
    """

    def __init__(self, port):
        QtGui.QUndoCommand.__init__(self)
        self.port = port
        self.visible = port.is_visible()

    def set_visible(self, visible):
        self.port.model.visible = visible
        self.port.view.setVisible(visible)
        _node_view = self.port.get_node().view
        _text_item = None
        if self.port.type_() == EnumPortType.IN.value:
            _text_item = _node_view.get_input_text_item(self.port.view)
        elif self.port.type_() == EnumPortType.OUT.value:
            _text_item = _node_view.get_output_text_item(self.port.view)
        if _text_item:
            _text_item.setVisible(visible)
        _node_view.post_init()

    def undo(self):
        self.set_visible(not self.visible)

    def redo(self):
        self.set_visible(self.visible)
