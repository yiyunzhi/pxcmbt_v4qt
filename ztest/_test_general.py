import yaml
from core.gui.qtimp import Serializable
from core.gui.node_graph.class_node_graph import NodeGraph
from core.gui.editor.blocks import STCStateNode
print(yaml)
with open(r'd:/fwf.yaml') as data_file:
    _layout_data = yaml.load(data_file, Loader=yaml.CFullLoader)
    print(_layout_data)