# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : solution_scanner.py
# ------------------------------------------------------------------------------
#
# File          : solution_scanner.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import pathlib
import importlib.util
from core.application.zI18n import zI18n


class MBTSolutionScanner:
    def __init__(self):
        pass

    def scan(self, path):
        _res = dict()
        _path = pathlib.Path(path)
        if not _path.exists():
            return False, zI18n.t('SOLUTION_PATH_NOT_EXIST')
        for p in _path.glob('*/__init__.py'):
            _dir_name = p.parts[-2]
            _spec = importlib.util.spec_from_file_location('SOLUTION_PKG_%s' % _dir_name, p.resolve())
            _module = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_module)
            if hasattr(_module, 'SOLUTION_DEF'):
                _res.update({p: (_module, _module.SOLUTION_DEF)})
        return True, _res
