import os, pathlib, anytree
from dataclasses import dataclass, field as data_field
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from application.class_base import Serializable
from application.utils_helper import util_remove_folder
from application.io.class_yaml_file_io import AppYamlInfFileIO, AppYamlObjFileIO
from .define import (APP_PROJECT_PATH,
                     BASE_PATH,
                     EnumProjectItemFlag,
                     EnumProjectItemRole,
                     EnumProjectNodeFileAttr)
from .class_application_config import APP_CONFIG
from .utils_helper import util_get_uuid_string
from .class_tree_model import TreeModelAnyTreeNode, TreeModel


class ProjectNodeContent:
    def __init__(self):
        self.projectNode = None

    def get_child_node_by_role(self, role):
        _node = self.projectNode
        _filter = list(
            filter(lambda x: x.role == role, _node.children))
        return _filter[0] if _filter else None

    def exe_cmd(self, **kwargs):
        return True,''


class ProjectTreeNode(TreeModelAnyTreeNode):
    def __init__(self, **kwargs):
        TreeModelAnyTreeNode.__init__(self, **kwargs)
        self.uuid = kwargs.get('uuid', util_get_uuid_string())
        self.role = kwargs.get('role')
        _flag = kwargs.get('flag', EnumProjectItemFlag.FLAG_DEFAULT)
        self.flag = 0
        if isinstance(_flag, list):
            for x in _flag:
                self.add_flag(x)
        else:
            assert isinstance(_flag, int), 'invalid flag. %s' % _flag
            self.flag = _flag
        self.icon = kwargs.get('icon', self.icon)
        self.description = kwargs.get('description', 'no description')
        self.contextMenu = kwargs.get('contextMenu')
        self.fileAttr = kwargs.get('fileAttr', EnumProjectNodeFileAttr.FOLDER)
        self.fileExtend = kwargs.get('fileExtend')
        self.fileName = kwargs.get('fileName', self.label.lower())
        self.content = None
        _content = kwargs.get('content')
        self.set_content(_content)

    def set_content(self, content):
        if content is not None:
            assert isinstance(content, ProjectNodeContent), 'ProjectNodeContent is required, given <%s>' % type(content)
            self.content = content
            self.content.projectNode = self

    def clear_content(self):
        self.content = None

    def update_describable_data(self, name, description):
        if self.has_flag(EnumProjectItemFlag.DESCRIBABLE):
            self.label = name
            self.description = description
            if self.content is not None:
                if hasattr(self.content, 'generalInfo'):
                    self.content.set_general_info(name, description)

    def get_file_name(self):
        if self.fileAttr != EnumProjectNodeFileAttr.LINK:
            if self.fileName.startswith('.'):
                return getattr(self, self.fileName[1::])
            else:
                self.fileName = self.label.lower()
                return self.fileName
        else:
            return self.fileName

    def get_file_path(self):
        if self.fileAttr == EnumProjectNodeFileAttr.FOLDER:
            _parent_path = self.path
        else:
            _parent_path = self.path[0:-1]
        return os.path.join(*[x.get_file_name() for x in _parent_path])

    def get_file_info(self):
        _file_path = self.get_file_path()
        _file_base_name = None
        if self.fileAttr == EnumProjectNodeFileAttr.FOLDER:
            return _file_path, _file_base_name
        elif self.fileAttr == EnumProjectNodeFileAttr.FILE:
            _file_base_name = self.get_file_name() + self.fileExtend
            return _file_path, _file_base_name
        elif self.fileAttr == EnumProjectNodeFileAttr.LINK:
            _file_path = os.path.join(BASE_PATH, self.fileName)
            return os.path.split(_file_path)
        else:
            return _file_path, _file_base_name

    def has_flag(self, flag):
        return (self.flag & flag) != 0

    def add_flag(self, flag):
        self.flag |= flag

    def reset_flag(self):
        self.flag = 0


class ProjectTreeModel(TreeModel):
    def __init__(self):
        TreeModel.__init__(self, ProjectTreeNode)
        self.name = 'ProjectTreeModel'

    def remove_node(self, node):
        node.parent = None


@dataclass
class ProjectMeta(Serializable):
    serialize_tag = '!ProjectMeta'
    ipodEngineRequirements: list = data_field(default_factory=list)

    @property
    def serializer(self):
        return {
            'ipodEngineRequirements': self.ipodEngineRequirements
        }

    def add_ipod_engine_ref(self, uid):
        if uid not in self.ipodEngineRequirements:
            self.ipodEngineRequirements.append(uid)

    def remove_ipod_engine_ref(self, uid):
        if uid in self.ipodEngineRequirements:
            self.ipodEngineRequirements.remove(uid)


class Project:

    def __init__(self, name):
        self.name = name
        self.meta = ProjectMeta()
        self.workspacePath = APP_PROJECT_PATH
        self.projectPath = os.path.join(APP_PROJECT_PATH, name)
        self.projectEntryFilePath = os.path.join(self.projectPath, self.name + APP_CONFIG.scProjExt)
        self.projectTreeModel = ProjectTreeModel()
        self.projectTreeRoot = None
        self._noSavableRole = [EnumProjectItemRole.RACK_SESSION_DEV_ITEM]
        self.mainPerspective = None

    def set_workspace_path(self, path):
        self.workspacePath = path
        self.projectPath = os.path.join(path, self.name)
        self.projectEntryFilePath = os.path.join(self.projectPath, self.name + APP_CONFIG.scProjExt)

    def is_ipod_engine_required(self, engine_id):
        return engine_id in self.meta.ipodEngineRequirements

    def add_ipod_engine_ref(self, engine_id):
        self.meta.add_ipod_engine_ref(engine_id)

    def remove_ipod_engine_ref(self, engine_id):
        self.meta.remove_ipod_engine_ref(engine_id)

    def do_create_project_file(self):
        assert self.projectTreeRoot is not None
        _eps = anytree.findall(self.projectTreeRoot, lambda x: not x.children)
        for node in _eps:
            self.create_project_node_file(node)

    def do_save_project_node(self):
        _file_io = AppYamlInfFileIO(self.projectPath, self.name + APP_CONFIG.scProjExt)
        # export exclusive the attribute contextMenu
        _exporter = DictExporter(attriter=lambda attr: [(k, v) for k, v in attr if k not in ['contextMenu', 'content']],
                                 childiter=lambda children: [child for child in children if child.role not in [
                                     EnumProjectItemRole.RACK_SESSION_DEV_ITEM.value]])
        _d = {'meta': self.meta,
              'project': _exporter.export(self.projectTreeRoot),
              'perspective': self.mainPerspective}
        _file_io.write(_d)
        return True

    def do_load_project(self):
        _file_io = AppYamlInfFileIO(self.projectPath, self.name + APP_CONFIG.scProjExt)
        _file_io.read()
        _project_d = _file_io.body.kwargs.get('project')
        _perspective = _file_io.body.kwargs.get('perspective')
        self.meta = _file_io.body.kwargs.get('meta')
        if not _project_d:
            return False
        self.projectTreeModel = ProjectTreeModel()
        self.projectTreeRoot = DictImporter(ProjectTreeNode).import_(_project_d)
        self.projectTreeRoot.parent = self.projectTreeModel.p_root
        self.mainPerspective = _perspective
        return True

    def save_perspective(self, main_perspective_str: str):
        if main_perspective_str is not None:
            self.mainPerspective = main_perspective_str
            self.do_save_project_node()

    def create_project_node_file(self, node, f_io_cls=None):
        if node is not None:
            if node.has_flag(EnumProjectItemFlag.SAVABLE):
                _file_path, _file_name = node.get_file_info()
                _file_path = os.path.join(self.workspacePath, _file_path)
                pathlib.Path(_file_path).mkdir(exist_ok=True, parents=True)
                if _file_name:
                    if f_io_cls is None:
                        _file_path = os.path.join(_file_path, _file_name)
                        with open(_file_path, 'w') as f:
                            f.write('')
                    else:
                        _f_io = f_io_cls(_file_path, _file_name)
                        _f_io.write(None)

    def remove_project_node_file(self, node):
        if node is not None:
            if node.has_flag(EnumProjectItemFlag.REMOVABLE):
                _file_path, _file_name = node.get_file_info()
                _file_path = os.path.join(self.workspacePath, _file_path)
                if _file_name:
                    _file_path = os.path.join(self.workspacePath, _file_path, _file_name)
                    pathlib.Path(_file_path).unlink()
                else:
                    util_remove_folder(_file_path)

    def do_save_project_node_content(self, node, io_cls=None, recursive=False):
        if node is None:
            node = self.projectTreeModel.p_root
        if node.has_flag(EnumProjectItemFlag.SAVABLE) and node.fileAttr == EnumProjectNodeFileAttr.FILE:
            _file_path, _file_name = node.get_file_info()
            _file_path = os.path.join(self.workspacePath, _file_path)
            if io_cls is None:
                _io = AppYamlObjFileIO(_file_path, _file_name)
            else:
                _io = io_cls(_file_path, _file_name)
            if not recursive:
                _io.write(node.content)
            del _io
        return True
