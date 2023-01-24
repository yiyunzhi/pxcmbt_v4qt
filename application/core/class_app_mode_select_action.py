# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_app_mode_select_action.py
# ------------------------------------------------------------------------------
#
# File          : class_app_mode_select_action.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import anytree


class HierarchyActionModel(anytree.NodeMixin):
    def __init__(self, **kwargs):
        self.i18nNs = kwargs.get('i18nNs', 'app')
        self.oid = kwargs.get('oid', 0)
        self.label = kwargs.get('label')
        self.iconNs = kwargs.get('iconNs', 'fa')
        self.iconName = kwargs.get('icon', 'mdi6.view-dashboard')
        self.state = kwargs.get('state', False)
        self.shortcut = kwargs.get('shortcut', None)
        self.handle = kwargs.get('handle', None)
        self.parent = kwargs.get('parent')

    def getLabel(self):
        return '%s.%s' % (self.i18nNs, self.label)

    def getIconInfo(self):
        if self.iconNs is None or self.iconName is None:
            return None
        return self.iconNs,self.iconName
