import os, yaml
from core.application.core.base import YAMLObject
from .class_base import AppFileIO

NODE_CONTENT_LOADER = YAMLObject.loader
NODE_CONTENT_DUMPER = YAMLObject.dumper


class AppYamlFileIO(AppFileIO):

    def __init__(self, file_path, file_name, extend='.yaml'):
        AppFileIO.__init__(self)
        self.extend = extend
        self.data = None
        self.filePath = file_path
        self.fileName = file_name
        self.error = ''

    def read(self, loader=NODE_CONTENT_LOADER):
        self.error = ''
        _full_path = self.get_full_path()
        if not self.is_file_exist():
            self.error = 'file %s not exist' % _full_path
            return False
        with open(_full_path) as f:
            _data = yaml.load(f, Loader=loader)
            if _data is None:
                self.error = 'data is empty'
                return False
            self.data = _data
            return True

    def write(self, data, dumper=NODE_CONTENT_DUMPER):
        _file_full_path = self.get_full_path()
        with open(_file_full_path, "w") as f:
            yaml.dump(data, f, Dumper=dumper)

    def get_full_path(self):
        if '.' in self.fileName:
            _file_name = self.fileName
        else:
            _file_name = self.fileName + self.extend
        return os.path.join(self.filePath, _file_name)

    def is_file_exist(self):
        _full_path = self.get_full_path()
        return os.path.exists(_full_path)
