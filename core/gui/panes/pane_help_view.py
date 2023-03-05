# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_welcome.py
# ------------------------------------------------------------------------------
#
# File          : pane_welcome.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from pubsub import pub
from core.application.core.base import singleton
from core.gui.qtimp import QtWidgets, QtCore
import core.gui.qtads as QtAds
from core.gui.core.class_base import ZView


class _HelpPane(QtWidgets.QWidget, ZView):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        ZView.__init__(self)
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.labelStart = QtWidgets.QLabel('Help', self)

        # bind event

        # layout
        self.mainLayout.setContentsMargins(25, 15, 5, 5)
        self.mainLayout.addWidget(self.labelStart, 0, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.mainLayout)


@singleton
class HelpDockPane(QtAds.CDockWidget, ZView):
    def __init__(self, parent):
        QtAds.CDockWidget.__init__(self, 'help', parent)
        ZView.__init__(self)
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE, False)
        _widget = _HelpPane(self)
        self.setWidget(_widget)
