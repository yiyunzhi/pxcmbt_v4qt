# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_tester_project_tree_mc.py
# ------------------------------------------------------------------------------
#
# File          : pane_tester_project_tree_mc.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.core.class_base import ZViewManager, ZViewContentContainer, Content


class TesterProjectNodeContentContainer(ZViewContentContainer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = None
        self.iconNs = None
        self.iconName = None
        self.domainRoot = None

    def sort(self):
        pass

    def delete(self, nid):
        pass

    def add(self, obj):
        pass

    def transform_data(self):
        return {}


class TesterProjectNodeTreeManager(ZViewManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_content(self, content: Content):
        super().set_content(content)
        self.view.update()

    def restore_content(self):
        pass

    def ensure_view(self):
        if self.view is None:
            return