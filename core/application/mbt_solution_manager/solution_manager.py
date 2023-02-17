# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : solution_manager.py
# ------------------------------------------------------------------------------
#
# File          : solution_manager.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .solution_scanner import MBTSolutionScanner
from .solution import MBTSolution
from core.application.zI18n import zI18n


class SolutionResolveException(Exception):
    pass


class SolutionRegisterException(Exception):
    pass


class SolutionAssertException(Exception):
    pass


class MBTSolutionsManager:
    def __init__(self, app_ctx):
        self.appCtx = app_ctx
        self.scanner = MBTSolutionScanner()
        self.solutions = dict()

    def add_solution(self, solution: MBTSolution):
        _k = '%s.%s' % (solution.solution_def.namespace, solution.solution_def.type)
        if _k in self.solutions:
            raise SolutionRegisterException(zI18n.t('SOLUTION_ALREADY_EXIST'))
        self.solutions.update({_k: solution})

    def resolve_solutions(self, path):
        _cur_p = ''
        _res, _slt_info = self.scanner.scan(path)
        if not _res:
            raise SolutionResolveException('%s' % _slt_info)
        try:
            for p, mi in _slt_info.items():
                _cur_p = p
                _slt = MBTSolution(module_path=p, module=mi[0], solution_def=mi[1])
                self.add_solution(_slt)
        except Exception as e:
            raise SolutionAssertException(zI18n.t('FMT_UNKNOWN_SOLUTION_AT', path=_cur_p))
