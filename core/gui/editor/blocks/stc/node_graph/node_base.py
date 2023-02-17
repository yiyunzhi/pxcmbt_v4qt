# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : node_base.py
# ------------------------------------------------------------------------------
#
# File          : node_base.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui.node_graph import NodeObject


class BaseSTCNode(NodeObject):

    def __init__(self, **kwargs):
        if 'label' not in kwargs:
            kwargs['label'] = 'NewState'
        NodeObject.__init__(self, **kwargs)
