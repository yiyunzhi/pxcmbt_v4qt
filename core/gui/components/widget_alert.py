# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_alert.py
# ------------------------------------------------------------------------------
#
# File          : widget_alert.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtCore, QtGui, QtWidgets
import core.gui.qtawesome as qta


class AlertWidget(QtWidgets.QWidget):
    AlertTypeError = 0
    AlertTypeWarning = 1
    AlertTypeSuccess = 2
    CssClass = ['danger', 'warning', 'success']

    def __init__(self, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('zAlertWidget')
        self.autoCloseMs = kwargs.get('auto_close_ms', 3500)
        self.closeable = kwargs.get('closeable', True)
        self.alertType = kwargs.get('alert_type', self.AlertTypeError)
        self.setProperty('class', self.CssClass[self.alertType])
        self.title = kwargs.get('title', '')
        self.subTitle = kwargs.get('sub_title', '')
        self.description = kwargs.get('description', '')
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.prefixLayout = QtWidgets.QVBoxLayout(self)
        self.contentLayout = QtWidgets.QVBoxLayout(self)
        self.actionLayout = QtWidgets.QVBoxLayout(self)
        if self.closeable:
            self.closeButton = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton),
                                                     '', self)
            self.closeButton.setObjectName('closeButton')
            self.closeButton.setFlat(True)
            self.closeButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.prefixIconHolder=QtWidgets.QLabel('',self)
        self.titleLabel = QtWidgets.QLabel(self.title, self)
        self.titleLabel.setProperty('class', 'title')
        self.subTitleLabel = QtWidgets.QLabel(self.subTitle, self)
        self.subTitleLabel.setProperty('class', 'sub-title')
        self.descriptionLabel = QtWidgets.QLabel(self.description, self)
        self.descriptionLabel.setProperty('class', 'description')
        self.descriptionLabel.setWordWrap(True)
        self.contentLayout.setSpacing(0)
        self.actionLayout.setSpacing(0)
        self.prefixIconHolder.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.prefixIconHolder.setPixmap(self._get_prefix_icon().pixmap(QtCore.QSize(24,24)))
        # bind event
        self._timer = QtCore.QTimer(self)
        if self.closeable:
            self.closeButton.clicked.connect(self._on_close_button_clicked)
        # layout
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setLayout(self.mainLayout)
        self.mainLayout.addLayout(self.prefixLayout)
        self.mainLayout.addSpacing(5)
        self.mainLayout.addLayout(self.contentLayout)
        self.mainLayout.addLayout(self.actionLayout)
        self.prefixLayout.addWidget(self.prefixIconHolder)
        self.contentLayout.addWidget(self.titleLabel)
        self.contentLayout.addWidget(self.subTitleLabel)
        if not self.title:
            self.titleLabel.setVisible(False)
        if not self.subTitle:
            self.subTitleLabel.setVisible(False)
        self.contentLayout.addSpacing(5)
        self.contentLayout.addWidget(self.descriptionLabel,0,QtCore.Qt.AlignmentFlag.AlignVCenter)
        if self.closeable:
            self.actionLayout.addWidget(self.closeButton, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        # setup
        if self.autoCloseMs > 0:
            self._timer.singleShot(self.autoCloseMs, self._on_time_out)

    def _get_prefix_icon(self):
        if self.alertType == self.AlertTypeError:
            return self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical)
        elif self.alertType == self.AlertTypeWarning:
            return self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning)
        elif self.alertType == self.AlertTypeSuccess:
            return self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation)

    def _close(self):
        self.deleteLater()

    def _on_time_out(self):
        self._close()

    def _on_close_button_clicked(self, evt):
        self._close()
