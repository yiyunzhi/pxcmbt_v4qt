# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_qt_theme.py
# ------------------------------------------------------------------------------
#
# File          : _test_qt_theme.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os, sys
from PySide6 import QtWidgets, QtCore, QtGui, QtUiTools
from ztest._test_qt_theme_main_window import Ui_MainWindow


class MainWinC(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # self.setWindowTitle(self.windowTitle())
        self.custom_styles()
        _action1=self.toolBar.addAction('OPEN DIALOG')
        _action1.triggered.connect(self.onOpenDialog)
    def onOpenDialog(self,evt):
        _dlg=QtWidgets.QDialog(self)
        _dlg.setSizeGripEnabled(True)
        _layout=QtWidgets.QHBoxLayout(_dlg)
        _dbtn=QtWidgets.QPushButton('danger',_dlg)
        _wbtn=QtWidgets.QPushButton('warning',_dlg)
        _sbtn=QtWidgets.QPushButton('success',_dlg)
        _label=QtWidgets.QLabel('Beautiful is better than ugly',_dlg)
        _dbtn.setProperty('class', 'danger')
        _wbtn.setProperty('class', 'warning')
        _sbtn.setProperty('class', 'success')
        _layout.addWidget(_dbtn)
        _layout.addWidget(_wbtn)
        _layout.addWidget(_sbtn)
        _layout.addWidget(_label)
        _dlg.setLayout(_layout)
        _dlg.show()

    def custom_styles(self):
        """"""
        for i in range(self.toolBar_vertical.layout().count()):

            try:
                tool_button = (
                    self.toolBar_vertical.layout().itemAt(i).widget()
                )
                tool_button.setMaximumWidth(150)
                tool_button.setMinimumWidth(150)
            except:
                tool_button = (
                    self.toolBar_vertical.layout().item_at(i).widget()
                )
                tool_button.maximum_width = 150
                tool_button.minimum_width = 150
        try:
            for r in range(self.tableWidget.rowCount()):
                self.tableWidget.setRowHeight(r, 36)

            for r in range(self.tableWidget_2.rowCount()):
                self.tableWidget_2.setRowHeight(r, 36)

        except:
            for r in range(self.tableWidget.row_count):
                self.tableWidget.set_row_height(r, 36)

            for r in range(self.tableWidget_2.row_count):
                self.tableWidget_2.set_row_height(r, 36)


from gui.qttheme import apply_theme

theme = 'default'


def take_screenshot():
    pixmap = frame.grab()
    pixmap.save(os.path.join('screenshots', f'{theme}.png'))
    print(f'Saving {theme}')


from gui.patch.low_level_sys_ui import llSetDarkWinTitlebar

app = QtWidgets.QApplication(sys.argv)
frame = MainWinC()
llSetDarkWinTitlebar(frame.winId())
apply_theme(app,densityScale='-1')

frame.resize(1024, 720)
frame.show()
sys.exit(app.exec())
