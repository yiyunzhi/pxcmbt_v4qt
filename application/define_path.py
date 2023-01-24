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

_ROOT = pathlib.Path(__file__).parent.parent
BASE_PATH = _ROOT.resolve()
_APPLICATION_PATH = _ROOT.joinpath('application')
APPLICATION_PATH = _APPLICATION_PATH.resolve()

_GUI_PATH = _ROOT.joinpath('gui')
GUI_PATH = _GUI_PATH.resolve()

_I18N_PATH = _ROOT.joinpath('i18n')
I18N_PATH = _I18N_PATH.resolve()
