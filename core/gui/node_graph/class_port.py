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
from collections import defaultdict
from core.gui.qtimp import Serializable, ClassFactory


class PortObject(Serializable):
    """
    Data dump for a port object.
    """
    serializeTag = '!PortObject'

    def __init__(self, **kwargs):
        self.type_ = kwargs.get('type')
        self.name = kwargs.get('name', 'port')
        self.label = kwargs.get('label')
        # todo: use flag to management
        self.multiConnection = kwargs.get('multi_connection')
        self.visible = kwargs.get('visible', True)
        self.locked = kwargs.get('locked', False)
        self.connectedPorts = defaultdict(list)
        _view_cls_name = kwargs.get('view_cls_name')
        if _view_cls_name is None:
            raise RuntimeError(
                'No graphics item name specified for the node object!'
            )
        _view_cls = ClassMapper.get_class_by_name(_view_cls_name)
        if _view_cls is None:
            raise RuntimeError(
                'No graphics item class specified for the node object!'
            )
        self._view = _view_cls(self)

    def __repr__(self):
        return '<{}(\'{}\') object at {}>'.format(
            self.__class__.__name__, self.name, hex(id(self)))

    @property
    def serializer(self):
        return {'type': self.type_,
                'name': self.name,
                'label': self.label,
                'multi_connection': self.multiConnection,
                'visible': self.visible,
                'locked': self.locked,
                'connectedPorts': self.connectedPorts
                }

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
