# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_application_context.py
# ------------------------------------------------------------------------------
#
# File          : class_application_context.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .core.base import singleton
from .core.class_uid_object_mapper import UidObjectMapper
from .define_path import ADDONS_PATH, SOLUTIONS_PATH
from .addon_manager.addon_manager import AddonsManager
from .mbt_solution_manager.solution_manager import MBTSolutionsManager


class AppCtxInitException(Exception):
    pass


@singleton
class ApplicationContext:
    def __init__(self):
        self._editorMapper = UidObjectMapper()
        self._app = None
        self._addonsManager = AddonsManager(self)
        self._solutionManager = MBTSolutionsManager(self)
        self.setup()

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, app_instance):
        self._app = app_instance

    @property
    def addons_manager(self):
        return self._addonsManager

    @property
    def mbt_solution_manager(self):
        return self._solutionManager

    def setup(self):
        try:
            self._addonsManager.resolve_addons(ADDONS_PATH)
            self._solutionManager.resolve_solutions(SOLUTIONS_PATH)
        except Exception as e:
            raise AppCtxInitException('Application context init error.\n%s' % e)


APP_CONTEXT = ApplicationContext()
