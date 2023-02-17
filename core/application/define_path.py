# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : define_path.py
# ------------------------------------------------------------------------------
#
# File          : define_path.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os, pathlib

_CORE_ROOT = pathlib.Path(__file__).parent.parent
_ROOT = _CORE_ROOT.parent
CORE_PATH = _CORE_ROOT.resolve()
_CORE_APPLICATION_PATH = _CORE_ROOT.joinpath('application')
CORE_APPLICATION_PATH = _CORE_APPLICATION_PATH.resolve()

_CORE_GUI_PATH = _CORE_ROOT.joinpath('gui')
CORE_GUI_PATH = _CORE_GUI_PATH.resolve()

_CORE_I18N_PATH = _CORE_ROOT.joinpath('i18n')
CORE_I18N_PATH = _CORE_I18N_PATH.resolve()

_PROJECT_PATH = _ROOT.joinpath('project')
PROJECT_PATH = _PROJECT_PATH.resolve()

_ADDONS_PATH = _CORE_ROOT.joinpath('addons')
ADDONS_PATH = _ADDONS_PATH.resolve()

_SOLUTIONS_PATH = _ROOT.joinpath('solutions')
SOLUTIONS_PATH = _SOLUTIONS_PATH.resolve()
