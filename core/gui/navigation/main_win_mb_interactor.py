# -*- coding: utf-8 -*-
import os
# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : main_win_mb_interactor.py
# ------------------------------------------------------------------------------
#
# File          : main_win_mb_interactor.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import typing
from core.application.define import EnumAppMsg
from core.application.class_application_context import APP_CONTEXT
from core.gui.qtimp import QtGui, QtCore
from .define import EnumMainMenuIDs

if typing.TYPE_CHECKING:
    from .main_win_mb_mgr import APPMenubarManager


class OSUnifiedEventHandleExecException(Exception): pass


class CallExternalUnifiedEventHandle:
    def __init__(self):
        self._prefix = '>'
        self._prog = None

    def is_handleable(self, handle_name: str):
        return handle_name.startswith(self._prefix)

    def on_exec_started(self, *args):
        APP_CONTEXT.set_app_busy(False)

    def on_exec_finish(self, exit_code, exit_state):
        self._prog.deleteLater()
        self._prog = None

    def exec(self, q_object, method_name, **kwargs):
        if self._prog is not None:
            self._prog.deleteLater()
            self._prog = None
        self._prog = QtCore.QProcess(q_object)
        self._prog.started.connect(self.on_exec_started)
        # self._prog.finished.connect(self.on_exec_finish)
        try:
            APP_CONTEXT.set_app_busy(True)
            if method_name == '{}os.start_program'.format(self._prefix):
                self._prog.start(kwargs.get('program'),kwargs.get('arguments'))
            elif method_name == '{}os.start_command'.format(self._prefix):
                # self._prog.startDetached('cmd')
                _ret = os.system(kwargs.get('command'))
                self.on_exec_started()
        except Exception as e:
            self.on_exec_finish(-1, QtCore.QProcess.ExitStatus.CrashExit)
            raise OSUnifiedEventHandleExecException(e)
        finally:
            pass


class APPMenubarInteractor:
    def __init__(self, menubar_mgr: 'APPMenubarManager'):
        self.mgr = menubar_mgr
        self.mgr.mb.triggered.connect(self.on_menubar_action_triggered)
        self.ceUnifiedEventHandler = CallExternalUnifiedEventHandle()

    def on_menubar_action_triggered(self, event: QtGui.QAction):
        _node = event.data()
        _handle = _node.handle
        if _handle is None:
            return
        if self.ceUnifiedEventHandler.is_handleable(_handle['method']):
            self.ceUnifiedEventHandler.exec(self.mgr.container, _handle['method'], **_handle['kwargs'])
        print('---->on_menubar_action_triggered:', _node.uid)
