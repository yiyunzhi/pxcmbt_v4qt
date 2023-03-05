# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_font_awesome_icon.py
# ------------------------------------------------------------------------------
#
# File          : _test_font_awesome_icon.py
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
from ztest._test_main_frame import app, TestFrame
from core.gui.core.class_icon_repository import IconRepository
from core.gui.core.class_i18n_repository import I18nRepository

ir = IconRepository(app)
i18n = I18nRepository()


class IconContainerWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.label0 = QtWidgets.QLabel('TestLabel')
        _icon_0 = ir.get_icon(self.label0, icon_ns='fa', icon_name='mdi.home', setter=self.set_label_icon)
        self.set_label_icon(_icon_0, self.label0)
        self.label1 = QtWidgets.QLabel('TestLabel1')
        self.label1.setPixmap(qta.icon('mdi.plus').pixmap(QtCore.QSize(24, 24)))
        self.label2 = QtWidgets.QLabel('TestLabel')
        self.label2.setPixmap(qta.icon('mdi.minus').pixmap(QtCore.QSize(24, 24)))

        self.label3 = QtWidgets.QLabel('')
        _text = i18n.get_i18n(self.label3, i18n_ns='app', i18n_key='welcome', setter=self.label3.setText)
        self.label3.setText(_text)
        # layout
        self.mainLayout.addWidget(self.label0, 0, 0)
        self.mainLayout.addWidget(self.label1, 0, 1)
        self.mainLayout.addWidget(self.label2, 0, 2)
        self.mainLayout.addWidget(self.label3, 1, 0)
        self.setLayout(self.mainLayout)

    def set_label_icon(self, icon, target):
        print('--->set_label_icon:', icon)
        target.setPixmap(icon.pixmap(QtCore.QSize(24, 24)))

    def changeEvent(self, event: QtCore.QEvent) -> None:
        super().changeEvent(event)


_main_win = TestFrame()
_main_win.setCentralWidget(IconContainerWidget(_main_win))
_main_win.show()
app.exec()
