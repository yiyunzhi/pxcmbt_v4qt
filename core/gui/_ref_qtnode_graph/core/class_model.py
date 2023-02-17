# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_model.py
# ------------------------------------------------------------------------------
#
# File          : class_model.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import json
from collections import defaultdict

from .define import EnumLayoutDirection, EnumNodePropWidgetType
from .exceptions import NodePropertyError


class PortModel(object):
    """
    Data dump for a port object.
    """

    def __init__(self, node):
        self.node = node
        self.type_ = ''
        self.name = 'port'
        self.displayName = True
        self.multiConnection = False
        self.visible = True
        self.locked = False
        self.connectedPorts = defaultdict(list)

    def __repr__(self):
        return '<{}(\'{}\') object at {}>'.format(
            self.__class__.__name__, self.name, hex(id(self)))

    @property
    def to_dict(self):
        """
        serialize model information to a dictionary.

        Returns:
            dict: node port dictionary eg.
                {
                    'type': 'in',
                    'name': 'port',
                    'display_name': True,
                    'multi_connection': False,
                    'visible': True,
                    'locked': False,
                    'connected_ports': {<node_id>: [<port_name>, <port_name>]}
                }
        """
        _props = self.__dict__.copy()
        _props.pop('node')
        _props['connectedPorts'] = dict(_props.pop('connectedPorts'))
        return _props


class NodeModel(object):
    """
    Data dump for a node object.
    """

    def __init__(self):
        self.type_ = None
        self.id = hex(id(self))
        self.icon = None
        self.name = 'node'
        self.color = (13, 18, 23, 255)
        self.borderColor = (74, 84, 85, 255)
        self.textColor = (255, 255, 255, 180)
        self.disabled = False
        self.selected = False
        self.visible = True
        self.width = 100.0
        self.height = 80.0
        self.pos = [0.0, 0.0]
        self.layoutDirection = EnumLayoutDirection.HORIZONTAL.value

        # BaseNode attrs.
        self.inputs = {}
        self.outputs = {}
        self.portDeletionAllowed = False

        # GroupNode attrs.
        self.subgraphSession = {}

        # Custom
        self._customProp = {}

        # node graph model set at node added time.
        self._graphModel = None

        # store the property attributes.
        # (deleted when node is added to the graph)
        self._TEMP_property_attrs = {}

        # temp store the property widget types.
        # (deleted when node is added to the graph)
        self._TEMP_property_widget_types = {
            'type_': EnumNodePropWidgetType.QLABEL.value,
            'id': EnumNodePropWidgetType.QLABEL.value,
            'icon': EnumNodePropWidgetType.HIDDEN.value,
            'name': EnumNodePropWidgetType.QLINE_EDIT.value,
            'color': EnumNodePropWidgetType.COLOR_PICKER.value,
            'borderColor': EnumNodePropWidgetType.HIDDEN.value,
            'textColor': EnumNodePropWidgetType.COLOR_PICKER.value,
            'disabled': EnumNodePropWidgetType.QCHECK_BOX.value,
            'selected': EnumNodePropWidgetType.HIDDEN.value,
            'width': EnumNodePropWidgetType.HIDDEN.value,
            'height': EnumNodePropWidgetType.HIDDEN.value,
            'pos': EnumNodePropWidgetType.HIDDEN.value,
            'layoutDirection': EnumNodePropWidgetType.HIDDEN.value,
            'inputs': EnumNodePropWidgetType.HIDDEN.value,
            'outputs': EnumNodePropWidgetType.HIDDEN.value,
        }

    def __repr__(self):
        return '<{}(\'{}\') object at {}>'.format(
            self.__class__.__name__, self.name, self.id)

    def add_property(self, name, value, items=None, range=None,
                     widget_type=None, tab=None):
        """
        add custom property.

        Args:
            name (str): name of the property.
            value (object): data.
            items (list[str]): items used by widget type NODE_PROP_QCOMBO.
            range (tuple): min, max values used by NODE_PROP_SLIDER.
            widget_type (int): widget type flag.
            tab (str): widget tab name.
        """
        widget_type = widget_type or EnumNodePropWidgetType.HIDDEN.value
        tab = tab or 'Properties'

        if name in self.properties.keys():
            raise NodePropertyError(
                '"{}" reserved for default property.'.format(name))
        if name in self._customProp.keys():
            raise NodePropertyError(
                '"{}" property already exists.'.format(name))

        self._customProp[name] = value

        if self._graphModel is None:
            self._TEMP_property_widget_types[name] = widget_type
            self._TEMP_property_attrs[name] = {'tab': tab}
            if items:
                self._TEMP_property_attrs[name]['items'] = items
            if range:
                self._TEMP_property_attrs[name]['range'] = range
        else:
            _attrs = {
                self.type_: {
                    name: {
                        'widget_type': widget_type,
                        'tab': tab
                    }
                }
            }
            if items:
                _attrs[self.type_][name]['items'] = items
            if range:
                _attrs[self.type_][name]['range'] = range
            self._graphModel.set_node_common_properties(_attrs)

    def set_property(self, name, value):
        if name in self.properties.keys():
            setattr(self, name, value)
        elif name in self._customProp.keys():
            self._customProp[name] = value
        else:
            raise NodePropertyError('No property "{}"'.format(name))

    def get_property(self, name):
        if name in self.properties.keys():
            return self.properties[name]
        return self._customProp.get(name)

    def get_widget_type(self, name):
        _model = self._graphModel
        if _model is None:
            return self._TEMP_property_widget_types.get(name)
        return _model.get_node_common_properties(self.type_)[name]['widget_type']

    def get_tab_name(self, name):
        _model = self._graphModel
        if _model is None:
            _attrs = self._TEMP_property_attrs.get(name)
            if _attrs:
                return _attrs[name].get('tab')
            return
        return _model.get_node_common_properties(self.type_)[name]['tab']

    @property
    def properties(self):
        """
        return all default node properties.

        Returns:
            dict: default node properties.
        """
        _props = self.__dict__.copy()
        _exclude = ['_custom_prop',
                    '_graph_model',
                    '_TEMP_property_attrs',
                    '_TEMP_property_widget_types']
        [_props.pop(i) for i in _exclude if i in _props.keys()]
        return _props

    @property
    def custom_properties(self):
        """
        return all custom properties specified by the user.

        Returns:
            dict: user defined properties.
        """
        return self._customProp

    @property
    def to_dict(self):
        """
        serialize model information to a dictionary.

        Returns:
            dict: node id as the key and properties as the values eg.
                {'0x106cf75a8': {
                    'name': 'foo node',
                    'color': (48, 58, 69, 255),
                    'border_color': (85, 100, 100, 255),
                    'text_color': (255, 255, 255, 180),
                    'type_': 'com.chantasticvfx.FooNode',
                    'selected': False,
                    'disabled': False,
                    'visible': True,
                    'width': 0.0,
                    'height: 0.0,
                    'pos': (0.0, 0.0),
                    'layout_direction': 0,
                    'custom': {},
                    'inputs': {
                        <port_name>: {<node_id>: [<port_name>, <port_name>]}
                    },
                    'outputs': {
                        <port_name>: {<node_id>: [<port_name>, <port_name>]}
                    },
                    'input_ports': [<port_name>, <port_name>],
                    'output_ports': [<port_name>, <port_name>],
                    },
                    subgraph_session: <sub graph session data>
                }
        """
        _node_dict = self.__dict__.copy()
        _node_id = _node_dict.pop('id')

        _inputs = {}
        _outputs = {}
        _input_ports = []
        _output_ports = []
        for name, model in _node_dict.pop('inputs').items():
            if self.portDeletionAllowed:
                _input_ports.append({
                    'name': name,
                    'multi_connection': model.multiConnection,
                    'display_name': model.displayName,
                })
            _connected_ports = model.to_dict['connectedPorts']
            if _connected_ports:
                _inputs[name] = _connected_ports
        for name, model in _node_dict.pop('outputs').items():
            if self.portDeletionAllowed:
                _output_ports.append({
                    'name': name,
                    'multi_connection': model.multiConnection,
                    'display_name': model.displayName,
                })
            _connected_ports = model.to_dict['connectedPorts']
            if _connected_ports:
                _outputs[name] = _connected_ports
        if _inputs:
            _node_dict['inputs'] = _inputs
        if _outputs:
            _node_dict['outputs'] = _outputs

        if self.portDeletionAllowed:
            _node_dict['input_ports'] = _input_ports
            _node_dict['output_ports'] = _output_ports

        if self.subgraphSession:
            _node_dict['subgraph_session'] = self.subgraphSession

        _custom_props = _node_dict.pop('_custom_prop', {})
        if _custom_props:
            _node_dict['custom'] = _custom_props

        _exclude = ['_graph_model',
                   '_TEMP_property_attrs',
                   '_TEMP_property_widget_types']
        [_node_dict.pop(i) for i in _exclude if i in _node_dict.keys()]

        return {_node_id: _node_dict}

    @property
    def serial(self):
        """
        Serialize model information to a string.

        Returns:
            str: serialized JSON string.
        """
        _model_dict = self.to_dict
        return json.dumps(_model_dict)


class NodeGraphModel(object):
    """
    Data dump for a node graph.
    """

    def __init__(self):
        self.__common_node_props = {}

        self.nodes = {}
        self.session = ''
        self.acyclic = True
        self.pipeCollision = False
        self.layoutDirection = EnumLayoutDirection.HORIZONTAL.value

    def common_properties(self):
        """
        Return all common node properties.

        Returns:
            dict: common node properties.
                eg.
                    {'nodeGraphQt.nodes.FooNode': {
                        'my_property': {
                            'widget_type': 0,
                            'tab': 'Properties',
                            'items': ['foo', 'bar', 'test'],
                            'range': (0, 100)
                            }
                        }
                    }
        """
        return self.__common_node_props

    def set_node_common_properties(self, attrs:dict):
        """
        Store common node properties.

        Args:
            attrs (dict): common node properties.
                eg.
                    {'nodeGraphQt.nodes.FooNode': {
                        'my_property': {
                            'widget_type': 0,
                            'tab': 'Properties',
                            'items': ['foo', 'bar', 'test'],
                            'range': (0, 100)
                            }
                        }
                    }
        """
        for node_type in attrs.keys():
            _node_props = attrs[node_type]

            if node_type not in self.__common_node_props.keys():
                self.__common_node_props[node_type] = _node_props
                continue

            for prop_name, prop_attrs in _node_props.items():
                _common_props = self.__common_node_props[node_type]
                if prop_name not in _common_props.keys():
                    _common_props[prop_name] = prop_attrs
                    continue
                _common_props[prop_name].update(prop_attrs)

    def get_node_common_properties(self, node_type):
        """
        Return all the common properties for a registered node.

        Args:
            node_type (str): node type.

        Returns:
            dict: node common properties.
        """
        return self.__common_node_props.get(node_type)


if __name__ == '__main__':
    p = PortModel(None)
    # print(p.to_dict)

    n = NodeModel()
    n.inputs[p.name] = p
    n.add_property('foo', 'bar')

    print('-' * 100)
    print('property keys\n')
    print(list(n.properties.keys()))
    print('-' * 100)
    print('to_dict\n')
    for k, v in n.to_dict[n.id].items():
        print(k, v)
