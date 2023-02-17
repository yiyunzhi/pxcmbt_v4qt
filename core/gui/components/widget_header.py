# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_header.py
# ------------------------------------------------------------------------------
#
# File          : widget_header.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtWidgets


class HeaderWidget(QtWidgets.QWidget):
    STYLESHEET = """
        QLabel.title{
            font-size: 18px;
            font-weight: bolder;
        }
        QLabel.sub-title{
            font-size: 14px;
            font-weight: bolder;
        }
        QLabel.description{
            font-size: 12px;
            color: #777;
        }
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setProperty('class', 'title')
        self.subTitleLabel = QtWidgets.QLabel(self)
        self.subTitleLabel.setProperty('class', 'sub-title')
        self.descriptionLabel = QtWidgets.QLabel(self)
        self.descriptionLabel.setProperty('class', 'description')
        self.descriptionLabel.setWordWrap(True)
        # properties
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setStyleSheet(self.STYLESHEET)
        # layout
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.subTitleLabel)
        self.mainLayout.addWidget(self.descriptionLabel)

    def set_content(self, title: str, sub_title: str = None, description: str = None):
        self.titleLabel.setText(title)
        if sub_title is None:
            self.subTitleLabel.setVisible(False)
        else:
            self.subTitleLabel.setVisible(True)
            self.subTitleLabel.setText(sub_title)
        if description is None:
            self.descriptionLabel.setVisible(False)
        else:
            self.descriptionLabel.setVisible(True)
            self.descriptionLabel.setText(description)
