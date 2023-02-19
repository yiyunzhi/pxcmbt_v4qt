# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : mb_exception_hook.py
# ------------------------------------------------------------------------------
#
# File          : mb_exception_hook.py
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
import traceback
import logging
from ..qtimp import QtCore, QtWidgets

# basic logger functionality
_logger = logging.getLogger(__name__)
_handler = logging.StreamHandler(stream=sys.stdout)
_logger.addHandler(_handler)


def show_exception_box(log_msg):
    """Checks if a QApplication instance is available and shows a messagebox with the exception message.
    If unavailable (non-console application), log an additional notice.
    """
    if QtWidgets.QApplication.instance() is not None:
        _errorbox = QtWidgets.QMessageBox()
        _errorbox.setText("Oops. An unexpected error occured:\n{0}".format(log_msg))
        _errorbox.exec_()
    else:
        _logger.debug("No QApplication instance available.")


class UncaughtHook(QtCore.QObject):
    _exception_caught = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        # this registers the exception_hook() function as hook with the Python interpreter
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on main thread
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            _exc_info = (exc_type, exc_value, exc_traceback)
            _log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                 '{0}: {1}'.format(exc_type.__name__, exc_value)])
            _logger.critical("Uncaught exception:\n {0}".format(_log_msg), exc_info=_exc_info)

            # trigger message box show
            self._exception_caught.emit(_log_msg)


