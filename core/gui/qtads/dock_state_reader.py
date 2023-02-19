# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : dock_state_reader.py
# ------------------------------------------------------------------------------
#
# File          : dock_state_reader.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtCore


class CDockStateReader(QtCore.QXmlStreamReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mFileVersion = 0

    def setFileVersion(self, version):
        self.mFileVersion = version

    def fileVersion(self):
        return self.mFileVersion
