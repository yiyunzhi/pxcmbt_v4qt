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


class NodeViewPropertyChangedCmd(QtGui.QUndoCommand):
    """
    Node property changed command.

    Args:
        node_view (node_graph.BaseNodeViewItem): node_view.
        name (str): node property name.
        new_value (object): node property value.
    """

    def __init__(self, node_view, name, new_value):
        QtGui.QUndoCommand.__init__(self)
        if name == 'name':
            self.setText('renamed "{}" to "{}"'.format(node_view.type_, new_value))
        else:
            self.setText('change property "{}:{}"'.format(node_view.type_, name))
        self.nodeView = node_view
        self.name = name
        assert node_view.get_property(name) is not None
        self.oldVal = node_view.get_property(name).value
        self.newVal = new_value

    def set_node_prop(self, name, value):
        """
        updates the node view and model.
        """
        _prop=self.nodeView.get_property(name)
        # set model data.
        self.nodeView.do_set_property(_prop, value)

        # set view data.
        # _view = self.node.view

        # view widgets.
        # if hasattr(_view, 'widgets') and name in _view.widgets.keys():
        #     # check if previous value is identical to current value,
        #     # prevent signals from causing a infinite loop.
        #     if _view.widgets[name].get_value() != value:
        #         _view.widgets[name].set_value(value)

        # view properties.
        # if name in _view.property_names:
        #     # remap "pos" to "xy_pos" node view has pre-existing pos method.
        #     if name == 'pos':
        #         name = 'xy_pos'
        #     setattr(_view, name, value)

    def undo(self):
        if self.oldVal != self.newVal:
            self.set_node_prop(self.name, self.oldVal)
            # emit property changed signal.
            _graph = self.nodeView.node.graph
            _graph.sigPropertyChanged.emit(self.nodeView, self.name, self.oldVal)

    def redo(self):
        if self.oldVal != self.newVal:
            self.set_node_prop(self.name, self.newVal)
            # emit property changed signal.
            _graph = self.nodeView.node.graph
            _graph.sigPropertyChanged.emit(self.nodeView.node, self.name, self.newVal)


class NodeViewMovedCmd(QtGui.QUndoCommand):
    """
    Node moved command.

    Args:
        node_view (node_graph.BaseNodeViewItem): node_view.
        pos (tuple(float, float)): new node position.
        prev_pos (tuple(float, float)): previous node position.
    """

    def __init__(self, node_view, pos, prev_pos):
        QtGui.QUndoCommand.__init__(self)
        self.nodeView = node_view
        self.pos = pos
        self.prevPos = prev_pos

    def undo(self):
        self.nodeView.view.setPos(*self.prevPos)

    def redo(self):
        if self.pos == self.prevPos:
            return
        self.nodeView.view.setPos(*self.pos)


class NodeViewAddedCmd(QtGui.QUndoCommand):
    """
    Node added command.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
        node (node_graph.GraphNode): node_view.
        pos (tuple(float, float)): initial node position (optional).
    """

    def __init__(self, graph, node, pos=None):
        QtGui.QUndoCommand.__init__(self)
        self.setText('added node')
        self.graphView = graph.get_view()
        self.graph = graph
        self.node = node
        self.pos = pos

    def undo(self):
        self.pos = self.pos or self.node.view.pos()
        self.graph.nodes.pop(self.node.id)
        self.node.view.delete()

    def redo(self):
        self.graph.nodes[self.node.id] = self.node
        self.graphView.add_item(self.node.view, self.pos)

        # node width & height is calculated when its added to the scene
        # so we have to update the node model here.
        #self.nodeView.width = self.node.view.width
        #self.nodeView.height = self.node.view.height


class NodeViewRemovedCmd(QtGui.QUndoCommand):
    """
    Node deleted command.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
        node_view (node_graph.BaseNodeViewItem): node_view.
    """

    def __init__(self, graph, node_view):
        QtGui.QUndoCommand.__init__(self)
        self.setText('deleted node')
        self.scene = graph.get_scene()
        self.graph = graph
        self.nodeView = node_view

    def undo(self):
        self.graph.nodes[self.nodeView.id] = self.nodeView.node
        self.scene.addItem(self.nodeView)

    def redo(self):
        self.graph.nodes.pop(self.nodeView.id)
        self.nodeView.delete()


class NodeViewInputConnectedCmd(QtGui.QUndoCommand):
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


class NodeViewInputDisconnectedCmd(QtGui.QUndoCommand):
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


class PortViewConnectedCmd(QtGui.QUndoCommand):
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


class PortViewDisconnectedCmd(QtGui.QUndoCommand):
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


class PortViewLockedCmd(QtGui.QUndoCommand):
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


class PortViewUnlockedCmd(QtGui.QUndoCommand):
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


class PortViewVisibleChangedCmd(QtGui.QUndoCommand):
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
