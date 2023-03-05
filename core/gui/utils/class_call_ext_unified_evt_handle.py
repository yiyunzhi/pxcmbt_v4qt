# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_call_ext_unified_evt_handle.py
# ------------------------------------------------------------------------------
#
# File          : class_call_ext_unified_evt_handle.py
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
from core.application.class_application_context import ApplicationContext
from core.gui.qtimp import QtCore


class OSUnifiedEventHandleExecException(Exception): pass


class CallExternalUnifiedEventHandle:
    def __init__(self):
        self._prefix = '>'
        self._prog = None

    def is_handleable(self, handle_name: str):
        return handle_name.startswith(self._prefix)

    def on_exec_started(self, *args):
        _app_ctx=ApplicationContext()
        _app_ctx.set_app_busy(False)

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
            _app_ctx = ApplicationContext()
            _app_ctx.set_app_busy(True)
            if method_name == '{}os.start_program'.format(self._prefix):
                self._prog.start(kwargs.get('program'), kwargs.get('arguments'))
            elif method_name == '{}os.start_command'.format(self._prefix):
                # self._prog.startDetached('cmd')
                _ret = os.system(kwargs.get('command'))
                self.on_exec_started()
        except Exception as e:
            self.on_exec_finish(-1, QtCore.QProcess.ExitStatus.CrashExit)
            raise OSUnifiedEventHandleExecException(e)
        finally:
            pass
