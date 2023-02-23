# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : qtimp.py
# ------------------------------------------------------------------------------
#
# File          : qtimp.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from PySide6 import QtCore, QtGui, QtWidgets,__version__ as QTVersion,QtOpenGLWidgets

from core.application.core.base import Serializable
from core.application.core.class_factory import ClassFactory


class SerializableQObject(type(QtCore.QObject), type(Serializable)):
    pass
