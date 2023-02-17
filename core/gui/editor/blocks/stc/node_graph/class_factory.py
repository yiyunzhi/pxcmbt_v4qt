# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_node_factory.py
# ------------------------------------------------------------------------------
#
# File          : class_node_factory.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import ClassFactory
from .define import (CLASS_FACTORY_NS_KEY)

STC_NODE_FACTORY = ClassFactory(CLASS_FACTORY_NS_KEY)
STC_NODE_VIEW_FACTORY = ClassFactory(CLASS_FACTORY_NS_KEY)
STC_GRAPH_VIEW_FACTORY = ClassFactory(CLASS_FACTORY_NS_KEY)
