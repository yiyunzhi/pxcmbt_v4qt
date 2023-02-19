# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : icon_provider.py
# ------------------------------------------------------------------------------
#
# File          : icon_provider.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtCore, QtGui
from .define import EnumADSIcon

class IconProviderMgr:
    _this: 'CIconProvider'
    userIcons: dict

    def __init__(self, _this):
        self._this = _this
        self.userIcons=dict()


class CIconProvider:
    def __init__(self):
        self._mgr = IconProviderMgr(self)

    def customIcon(self, icon_id:EnumADSIcon):
        return self._mgr.userIcons.get(icon_id)

    def registerCustomIcon(self, icon_id, icon: QtGui.QIcon):
        self._mgr.userIcons[icon_id]=icon
