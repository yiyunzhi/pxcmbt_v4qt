# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_project.py
# ------------------------------------------------------------------------------
#
# File          : class_project.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os
import pathlib
import anytree
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from core.application.utils_helper import util_date_time_now, util_get_computer_name, util_get_uuid_string
from core.application.core.base import Serializable, ContentContainer
from core.application.io.class_yaml_file_io import AppYamlFileIO
from .define_path import PROJECT_PATH
from .define import AppConfig, APP_VERSION


class ProjectHeader(Serializable):
    serializeTag = '!ProjectHeader'

    def __init__(self, **kwargs):
        self.createdAt = kwargs.get('created_at', util_date_time_now())
        self.appVersion = kwargs.get('app_version', APP_VERSION)
        self.projectIOVersion = kwargs.get('project_io_version', 4)
        self.lastUpdatedAt = kwargs.get('last_updated_at', util_date_time_now())
        self.originalHostName = kwargs.get('original_host_name', util_get_computer_name())
        self.hostName = kwargs.get('host_name', util_get_computer_name())
        self.version = kwargs.get('host_name', util_get_computer_name())
        self.userFields = kwargs.get('user_fields')

    def update(self):
        self.lastUpdatedAt = util_date_time_now()
        self.hostName = util_get_computer_name()

    def is_compatible(self, app_version, project_io_version):
        return self.appVersion == app_version and self.projectIOVersion == project_io_version

    @property
    def serializer(self):
        return {'created_at': self.createdAt,
                'last_updated_at': self.lastUpdatedAt,
                'original_host_name': self.originalHostName,
                'host_name': self.hostName,
                'app_version': self.appVersion,
                'project_io_version': self.projectIOVersion,
                'user_fields': self.userFields
                }


class ProjectRegisterContentContainerError(Exception):
    pass


class ProjectVisitContentContainerError(Exception):
    pass


class ProjectFileNode(anytree.NodeMixin):
    def __init__(self, **kwargs):
        self.fileId = kwargs.get('fileId', util_get_uuid_string())
        self.ccid = kwargs.get('ccid')
        self.parent = kwargs.get('parent')

    def get_file_path(self):
        _path = [x.fileId for x in self.path if x.fileId != '__root__']
        return pathlib.Path(*_path)


class Project:
    def __init__(self, name, version='4'):
        self.name = name
        self.version = version
        self.workspacePath = PROJECT_PATH
        self.projectPath = os.path.join(PROJECT_PATH, name)
        self.projectEntryFilePath = os.path.join(self.projectPath, self.name + AppConfig.projEntryFileExt)
        self.fileNodeRoot = ProjectFileNode(fileId='__root__')
        self.contentContainers = dict()
        self.header = ProjectHeader(project_io_version=self.version)
        self.error = ''
        self.persistFileExtension = '.mbt'

    def register_with_project(self, obj: ContentContainer, parent: ContentContainer = None):
        assert isinstance(obj, ContentContainer), 'ContentContainer type required'
        if parent is not None:
            assert isinstance(parent, ContentContainer), 'ContentContainer type required'
        _id = obj.get_id()
        if self.is_content_container_registered(_id):
            raise ProjectRegisterContentContainerError('ContentContainer id already registered.')
        self.contentContainers.update({_id: obj})
        if not self.is_content_container_file_assigned(_id):
            if parent is None:
                _parent = self.fileNodeRoot
            else:
                _parent = self.get_file_node_by_ccid(parent.get_id())
                if _parent is None:
                    raise ProjectVisitContentContainerError('ContentContainer id: {} not registered.'.format(parent.get_id()))
            ProjectFileNode(parent=_parent, file_id=util_get_uuid_string(), ccid=_id)
        # else:
        #    obj.set(self.load_content_by_ccid(_id))

    def is_content_container_registered(self, ccid):
        return ccid in self.contentContainers

    def is_content_container_file_assigned(self, ccid):
        return len(anytree.findall(self.fileNodeRoot, lambda x: x.ccid == ccid)) > 0


    def set_workspace_path(self, path):
        self.workspacePath = path
        self.projectPath = os.path.join(path, self.name)
        self.projectEntryFilePath = os.path.join(self.projectPath, self.name + AppConfig.projEntryFileExt)

    def load_project(self, project_path):
        try:
            _path = pathlib.Path(project_path)
            _file_path = _path.parents[0]
            _work_path = _file_path.parent
            _file_name = _path.name
            _project_name = _path.stem
            _file_io = AppYamlFileIO(_file_path, _project_name, extend='.proj')
            _ret = _file_io.read()
            if not _ret:
                self.error = _file_io.error
                return _ret
            self.name = _project_name
            self.set_workspace_path(_work_path)
            self.header = _file_io.data.get('header')
            self.fileNodeRoot = DictImporter(ProjectFileNode).import_(_file_io.data.get('project'))
            self.reset_cc_content()
            self.header.update()
            return True
        except Exception as e:
            self.error = 'cant load project file'
            return False

    def save_project(self):
        self.header.update()
        _file_name = self.name + AppConfig.projEntryFileExt
        pathlib.Path(self.projectPath).mkdir(exist_ok=True, parents=True)
        _file_io = AppYamlFileIO(self.projectPath, _file_name)
        _d = {'header': self.header,
              'project': DictExporter().export(self.fileNodeRoot),
              'perspective': None}
        _file_io.write(_d)
        return True

    def _do_read_file_node(self, node: ProjectFileNode):
        _path = pathlib.Path(self.projectPath).joinpath(node.get_file_path())
        _file_io = AppYamlFileIO(_path, _path.name, self.persistFileExtension)
        _ret = _file_io.read()
        if not _ret:
            self.error = _file_io.error
            return None
        else:
            return _file_io.data

    def _do_save_file_node(self, node: ProjectFileNode):
        _file_path = os.path.join(self.projectPath, node.get_file_path())
        _cc_node = self.contentContainers.get(node.ccid)
        pathlib.Path(_file_path).mkdir(exist_ok=True, parents=True)
        _file_io = AppYamlFileIO(_file_path, node.fileId, self.persistFileExtension)
        _file_io.write(_cc_node.get())

    def save_all(self):
        for k, v in self.contentContainers.items():
            _file_node = self.get_file_node_by_ccid(k)
            if _file_node:
                self._do_save_file_node(_file_node)

    def reset_cc_content(self):
        for k, v in self.contentContainers.items():
            _content = self.get_content_by_ccid(k)
            v.manager.set_content(_content)

    def get_content_by_ccid(self, ccid):
        _file_node = self.get_file_node_by_ccid(ccid)
        if _file_node is None:
            return None
        return self._do_read_file_node(_file_node)

    def get_file_node_by_ccid(self, ccid) -> ProjectFileNode:
        return anytree.find(self.fileNodeRoot, lambda x: x.ccid == ccid)

    def has_content_changed(self):
        return False
