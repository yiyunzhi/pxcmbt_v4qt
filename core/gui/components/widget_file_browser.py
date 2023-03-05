# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_file_browser.py
# ------------------------------------------------------------------------------
#
# File          : widget_file_browser.py
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
from core.application.class_application_context import ApplicationContext
from core.application.zI18n import zI18n
from core.gui.qtimp import QtWidgets


class FileBrowserWidget(QtWidgets.QWidget):
    def __init__(self, parent, default_path=''):
        super().__init__(parent)
        self._appCtx = ApplicationContext()
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.mainLayout.setSpacing(5)
        self.leftLabel = QtWidgets.QLabel(zI18n.t('app.path'), self)
        self.filePathEdit = QtWidgets.QLineEdit(self)
        self.filePathEdit.setText(default_path)
        self.filePathBrowserBtn = QtWidgets.QPushButton(self)
        _icon = self._appCtx.iconResp.get_icon(self.filePathBrowserBtn, icon_ns='fa', icon_name='ri.more-fill', setter='setIcon')
        self.filePathBrowserBtn.setIcon(_icon)
        # layout
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.leftLabel, 0, 0)
        self.mainLayout.addWidget(self.filePathEdit, 0, 1)
        self.mainLayout.addWidget(self.filePathBrowserBtn, 0, 2)
        self.mainLayout.setColumnStretch(1, 50)
        self.setLayout(self.mainLayout)

    def set_left_label_visible(self, visible):
        self.leftLabel.setVisible(visible)
        if not visible:
            self.mainLayout.setColumnStretch(0, 0)
        else:
            self.mainLayout.setColumnStretch(0, 20)
