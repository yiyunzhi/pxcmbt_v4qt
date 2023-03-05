# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : solution.py
# ------------------------------------------------------------------------------
#
# File          : solution.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from addict import Dict


class MBTSolution:
    """
    solutionDef expect a dict likes:
        'icon': None,
        'namespace': 'StateChart',
        'type': 'stc',
        'version': '1.0.1',
        'editor': '',
    """
    EXPECT_DEF_KEY = ['icon', 'namespace', 'type', 'version', 'view', 'builtinEntitiesPath', 'setup', 'uuid']

    def __init__(self, **kwargs):
        self._module = kwargs.get('module')
        assert self._module is not None
        self._modulePath = kwargs.get('module_path')
        _solutionDef = kwargs.get('solution_def', dict())
        assert all([k in _solutionDef for k in self.EXPECT_DEF_KEY])
        self._solutionDef = Dict(_solutionDef)

    @property
    def module_(self):
        return self._module

    @property
    def module_path(self):
        return self._modulePath

    @property
    def solution_def(self):
        return self._solutionDef

    @property
    def is_valid(self):
        return self._solutionDef.get('setup') is not None

    @property
    def name(self):
        return '{} v{}'.format(self._solutionDef.get('namespace'), self._solutionDef.get('version'))

    @property
    def uuid(self):
        return self._solutionDef['uuid']

    @property
    def icon_info(self):
        return self._solutionDef.get('icon')

    def run_setup(self, app_ctx):
        if self.is_valid:
            self._solutionDef.get('setup')(app_ctx)
