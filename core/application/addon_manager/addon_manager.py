# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : addon_manager.py
# ------------------------------------------------------------------------------
#
# File          : addon_manager.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .addon_scanner import AddonsScanner


class AddonsManager:
    def __init__(self, app_ctx):
        self.appCtx = app_ctx
        self.scanner = AddonsScanner()

    def resolve_addons(self, path):
        self.scanner.scan(path)

    def init_addons(self):
        pass
