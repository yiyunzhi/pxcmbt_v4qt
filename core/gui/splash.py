# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : splash.py
# ------------------------------------------------------------------------------
#
# File          : splash.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from PySide6 import QtCore, QtWidgets, QtGui
from application.define import APP_NAME, APP_VERSION
from .core.define_path import SPLASH_BG_IMAGE_PATH


class ZSplashScreen:
    def __init__(self, step_count=10):
        self.bgImg = QtGui.QPixmap(SPLASH_BG_IMAGE_PATH)
        self.titleTxt = '%s v%s' % (APP_NAME, APP_VERSION)
        self.messageTxtLst = [self.titleTxt, '']
        self.splash = QtWidgets.QSplashScreen(self.bgImg, QtCore.Qt.WindowType.WindowStaysOnTopHint)
        _layout = QtWidgets.QVBoxLayout(self.splash)
        self.progressbar = QtWidgets.QProgressBar(self.splash)
        self.progressbar.setFixedWidth(360)
        self.progressbar.setMaximum(step_count)
        self.progressbar.setFixedHeight(14)
        _layout.addStretch(1)
        _layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        _layout.setContentsMargins(0, 0, 0, 50)
        _layout.addWidget(self.progressbar)
        self.splash.setLayout(_layout)
        # self.splash.setStyleSheet("""
        #     QSplashScreen {background-color: #ffffff;}
        # """)

    def show(self):
        self.splash.show()

    def set_message(self, msg: str, step_count: int):
        self.messageTxtLst.append(msg)
        msg = '\n'.join(self.messageTxtLst)
        self.splash.showMessage(msg)
        self.progressbar.setValue(step_count)

    def finish(self, w: QtWidgets.QMainWindow):
        self.splash.finish(w)
