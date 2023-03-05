# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_tree.py
# ------------------------------------------------------------------------------
#
# File          : class_tree.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.application.core.base import ZTreeNodeMixin
from core.application.utils_helper import util_get_uuid_string


class UUIDTreeNode(ZTreeNodeMixin):
    def __init__(self, **kwargs):
        self.uuid = kwargs.get('uuid', util_get_uuid_string())
