# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_dialogs.py
# ------------------------------------------------------------------------------
#
# File          : class_dialogs.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os
from gui import QtWidgets

_current_user_directory = os.path.expanduser('~')


def _set_dir(file):
    global _current_user_directory
    if os.path.isdir(file):
        _current_user_directory = file
    elif os.path.isfile(file):
        _current_user_directory = os.path.split(file)[0]


class FileDialog(object):

    @staticmethod
    def getSaveFileName(parent=None, title='Save File', file_dir=None,
                        ext_filter='*'):
        if not file_dir:
            file_dir = _current_user_directory
        _file_dlg = QtWidgets.QFileDialog.getSaveFileName(
            parent, title, file_dir, ext_filter)
        _file = _file_dlg[0] or None
        if _file:
            _set_dir(_file)
        return _file_dlg

    @staticmethod
    def getOpenFileName(parent=None, title='Open File', file_dir=None,
                        ext_filter='*'):
        if not file_dir:
            file_dir = _current_user_directory
        _file_dlg = QtWidgets.QFileDialog.getOpenFileName(
            parent, title, file_dir, ext_filter)
        _file = _file_dlg[0] or None
        if _file:
            _set_dir(_file)
        return _file_dlg


class FeedbackDialog(object):

    @staticmethod
    def message_dialog(text='', title='Message'):
        _dlg = QtWidgets.QMessageBox()
        _dlg.setWindowTitle(title)
        _dlg.setInformativeText(text)
        _dlg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        _dlg.exec_()

    @staticmethod
    def question_dialog(text='', title='Are you sure?'):
        _dlg = QtWidgets.QMessageBox()
        _dlg.setWindowTitle(title)
        _dlg.setInformativeText(text)
        _dlg.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        _result = _dlg.exec_()
        return bool(_result == QtWidgets.QMessageBox.StandardButton.Yes)
