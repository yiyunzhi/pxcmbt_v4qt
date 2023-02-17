# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_node_object.py
# ------------------------------------------------------------------------------
#
# File          : _test_node_object.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import yaml
from gui import QtCore, QtGui, QtWidgets
from application.core.base import Serializable
from gui.node_graph.class_node_object import NodeObject, ClassMapper


@ClassMapper.register('TestView')
class TestView(QtWidgets.QGraphicsView):
    serializeTag = 'TestView'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.node = None

    @property
    def serializer(self):
        return {}


if __name__ == '__main__':
    import yaml, time, sys
    print(ClassMapper._MAP)
    app = QtWidgets.QApplication(sys.argv)
    NodeObject.nodeName = 'testNode'
    o = NodeObject('TestView')
    # n.inputs[p.name] = p
    # n.add_property('foo', 'bar')
    #
    # print('-' * 100)
    # print('property keys\n')
    # print(list(n.properties.keys()))
    # print('-' * 100)
    # print('to_dict\n')
    # for k, v in n.to_dict[n.id].items():
    #     print(k, v)
    print('test serialization')
    _t1 = time.time()
    with open('node_object_serialized.yaml', "w") as f:
        yaml.dump(o, f, Dumper=yaml.CDumper)
    with open('node_object_serialized.yaml', "r", encoding='utf-8') as f:
        _obj = yaml.load(f, Loader=yaml.CFullLoader)
        print(_obj)
    print(time.time() - _t1)
    sys.exit(app.exec())
