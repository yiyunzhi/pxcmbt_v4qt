# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_qbytearray.py
# ------------------------------------------------------------------------------
#
# File          : _test_qbytearray.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from PySide6 import QtCore
import base64

_b=QtCore.QByteArray(b'\x01\x02\x03\xFE\xDD')
_e=bytes(_b.toBase64()).decode('utf-8')
print(_e,bytes(_b.toBase64()).decode('utf-8'))
_r=QtCore.QByteArray.fromBase64(_e.encode('utf-8'))
print(_r)