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
from core.gui.qtimp import QtWidgets
from core.gui.core.class_base import I18nUiObject, ThemeStyledUiObject


class FileBrowserWidget(QtWidgets.QWidget, I18nUiObject, ThemeStyledUiObject):
    def __init__(self, parent, default_path=''):
        super().__init__(parent)
        I18nUiObject.__init__(self)
        ThemeStyledUiObject.__init__(self)
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.mainLayout.setSpacing(5)
        self.leftLabel = QtWidgets.QLabel(self)
        self.filePathEdit = QtWidgets.QLineEdit(self)
        self.filePathEdit.setText(default_path)
        self.filePathBrowserBtn = QtWidgets.QPushButton(self)
        self.iconUsageRegistry.register(self.filePathBrowserBtn, 'fa', 'ri.more-fill')
        self.i18nUsageRegistry.register(self.leftLabel, 'app', 'path', 'setText', True)
        self.filePathBrowserBtn.setIcon(self.iconUsageRegistry.get_icon(self.filePathBrowserBtn,
                                                                        color=self.palette().highlight().color()))
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

    def on_locale_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        self.i18nUsageRegistry.update_i18n_text(self.leftLabel)

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        self.filePathBrowserBtn.setIcon(self.iconUsageRegistry.get_icon(self.filePathBrowserBtn,
                                                                        color=self.palette().highlight().color()))
