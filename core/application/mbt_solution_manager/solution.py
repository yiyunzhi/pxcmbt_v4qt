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
from attrdict import AttrDict


class MBTSolution:
    """
    solutionDef expect:
        'icon': None,
        'namespace': 'StateChart',
        'type': 'stc',
        'version': '1.0.1',
        'editor': '',
    """
    EXPECT_DEF_KEY = ['icon', 'namespace', 'type', 'version', 'editor', 'builtinEntitiesPath']

    def __init__(self, **kwargs):
        self._module = kwargs.get('module')
        assert self._module is not None
        self._modulePath = kwargs.get('module_path')
        _solutionDef = kwargs.get('solution_def', dict())
        assert all([k in _solutionDef for k in self.EXPECT_DEF_KEY])
        self._solutionDef = AttrDict(_solutionDef)

    @property
    def module_(self):
        return self._module

    @property
    def module_path(self):
        return self._modulePath

    @property
    def solution_def(self):
        return self._solutionDef
