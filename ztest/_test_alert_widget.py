# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_alert_widget.py
# ------------------------------------------------------------------------------
#
# File          : _test_alert_widget.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import sys
from core.gui.qtimp import QtCore, QtGui, QtWidgets
from core.gui.components.widget_alert import AlertWidget
from ztest._test_main_frame import app, TestFrame
from core.gui.core.class_icon_repository import IconRepository
from core.gui.core.class_i18n_repository import I18nRepository

ir = IconRepository(app)
i18n = I18nRepository()


class TestWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.errAlert = AlertWidget(self,
                                    auto_close_ms=2000,
                                    alert_type=AlertWidget.AlertTypeError,
                                    title='Error',
                                    sub_title='error',
                                    description='this is a error,this is a errorthis is a errorthis is a errorthis is a errorthis is a error')
        self.warningAlert = AlertWidget(self,
                                        auto_close_ms=3000,
                                        alert_type=AlertWidget.AlertTypeWarning,
                                        title='Warning',
                                        sub_title='Warning',
                                        description='this is a Warning')
        self.successAlert = AlertWidget(self,
                                        auto_close_ms=4000,
                                        alert_type=AlertWidget.AlertTypeSuccess,
                                        title='Success',
                                        sub_title='Success',
                                        description='this is a Success')
        self.successAlert2 = AlertWidget(self,
                                         auto_close_ms=0,
                                         alert_type=AlertWidget.AlertTypeSuccess,
                                         title='Success2',
                                         sub_title='Success2',
                                         description='this is a Success')
        self.successAlert3 = AlertWidget(self,
                                         auto_close_ms=0,
                                         alert_type=AlertWidget.AlertTypeSuccess,
                                         description='this is a Success description without title and subtitle')
        self.successAlert4 = AlertWidget(self,
                                         auto_close_ms=0,
                                         closeable=False,
                                         alert_type=AlertWidget.AlertTypeSuccess,
                                         description='this is a Success description without title and subtitle and not closable')
        self.mainLayout.addWidget(self.errAlert)
        self.mainLayout.addWidget(self.warningAlert)
        self.mainLayout.addWidget(self.successAlert)
        self.mainLayout.addWidget(self.successAlert2)
        self.mainLayout.addWidget(self.successAlert3)
        self.mainLayout.addWidget(self.successAlert4)


_main_frame = TestFrame()
_tw = TestWidget(_main_frame)
_main_frame.setCentralWidget(_tw)
_main_frame.show()
sys.exit(app.exec())
