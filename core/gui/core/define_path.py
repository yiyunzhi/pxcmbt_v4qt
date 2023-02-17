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
from application.define_path import GUI_PATH

_ASSETS_PATH = pathlib.Path(GUI_PATH).joinpath('assets')
ASSETS_PATH = _ASSETS_PATH.resolve()
_ASSETS_IMAGE_PATH = _ASSETS_PATH.joinpath('image')
ASSETS_IMAGE_PATH = _ASSETS_IMAGE_PATH.resolve()

SPLASH_BG_IMAGE_PATH = _ASSETS_IMAGE_PATH.joinpath('splash.png').resolve()
LOGO_PATH = _ASSETS_IMAGE_PATH.joinpath('logo.png').resolve()

_CONFIG_PATH = pathlib.Path(GUI_PATH).joinpath('config')
CONFIG_PATH = pathlib.Path(GUI_PATH).joinpath('config').resolve()
CFG_APP_MODE_ACTION_YAML_PATH=_CONFIG_PATH.joinpath('cfg_app_mode_action.yaml').resolve()
CFG_APP_MB_YAML_PATH=_CONFIG_PATH.joinpath('cfg_app_mb.yaml').resolve()
# DIR_NAME_IPOD_ENGINES = 'ipod_engines'
# BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# APP_FOLDER_PATH = os.path.join(BASE_PATH, 'application')
# APP_CONFIG_FOLDER_PATH = os.path.join(APP_FOLDER_PATH, 'config')
# APP_LOG_FILE_PATH = os.path.join(BASE_PATH, 'logs', 'app.log')
# APP_CONFIG_FILE_PATH = os.path.join(APP_FOLDER_PATH, 'config', 'app_config.ini')
# APP_PROJECT_PATH = os.path.join(BASE_PATH, 'project')
# APP_DATA_PATH = os.path.join(BASE_PATH, 'data')
# APP_IOD_ACT_RUNNER_TMP_NAME = 'template_iod_act_runner.pyt'
# APP_IPOD_ENGINE_PATH = os.path.join(BASE_PATH, DIR_NAME_IPOD_ENGINES)
# APP_DATA_BUILTIN_PATH = os.path.join(APP_DATA_PATH, 'built_in')
# APP_EXTEND_PATH = os.path.join(BASE_PATH, 'extends')
# APP_EXT_COGENT_PATH = os.path.join(APP_EXTEND_PATH, 'cogent')
# APP_EXT_COGENT_TMP_PATH = os.path.join(APP_EXT_COGENT_PATH, 'templates')
# APP_EXT_COGENT_TMP_IOD_ACT_PATH = os.path.join(APP_EXT_COGENT_TMP_PATH, 'iodaction')
#
# APP_DEFAULT_PERSPECTIVE_PATH = os.path.join(APP_DATA_PATH, 'app_main_perspective')