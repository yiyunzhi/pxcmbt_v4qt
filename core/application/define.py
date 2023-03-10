# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : define.py
# ------------------------------------------------------------------------------
#
# File          : define.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os, enum

APP_NAME = 'PxCE MBT'
APP_VERSION = '4.000'
APP_CONSOLE_TIME_WX_FMT = '%m/%d %H:%M:%S.%l'
APP_CONSOLE_TIME_PY_FMT = '%m/%d %H:%M:%S.%f'
APP_TIME_PY_FMT = '%d/%m/%Y %H:%M:%S'

SIZE_UNITS = {1000: ['KB', 'MB', 'GB'],
              1024: ['KiB', 'MiB', 'GiB']}
MB_ATTACH_LABEL_REGEX = r'^@(.*)@$'

RECENT_MAX_LEN = 3


class EnumAppMsg:
    sigAppModeChanged = 'sigAppModeChanged'
    sigAppThemeChanged = 'sigAppThemeChanged'
    sigAppLanguageChanged = 'sigAppLanguageChanged'
    sigAppBusyStateChangeRequired = 'sigAppBusyStateChangeRequired'
    sigProjectStateChanged = 'sigProjectStateChanged'


class AppConfig:
    projEntryFileExt = '.proj'
