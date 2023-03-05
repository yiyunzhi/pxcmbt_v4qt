# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : edit_stc_view.py
# ------------------------------------------------------------------------------
#
# File          : edit_stc_view.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtGui, QtWidgets, QtCore
import core.gui.qtads as QtAds
from core.gui.core.class_base import ZView


class _STCEditorView(QtWidgets.QWidget, ZView):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        ZView.__init__(self)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel('STC EDITOR', self)
        self.mainLayout.addWidget(self.label)
        self.setLayout(self.mainLayout)


class STCEditorView(QtAds.CDockWidget, ZView):
    def __init__(self, parent=None):
        QtAds.CDockWidget.__init__(self, '', parent)
        ZView.__init__(self)
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_ON_CLOSE, False)
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE, False)
        _widget = _STCEditorView(self)
        self.setWidget(_widget)

    @ZView.title.setter
    def title(self, title):
        self.setWindowTitle(title)

    def set_view_manager(self, view_mgr):
        super().set_view_manager(view_mgr)
        if self.widget() and isinstance(self.widget(), ZView):
            self.widget().set_view_manager(view_mgr)
