# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_slicer_item.py
# ------------------------------------------------------------------------------
#
# File          : class_slicer_item.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import math

from core.gui.qtimp import QtCore, QtGui, QtWidgets

from ..core.define import Z_VAL_NODE_WIDGET


class PipeSlicerItem(QtWidgets.QGraphicsPathItem):
    """
    Base item used for drawing the pipe connection slicer.
    """

    def __init__(self):
        super(PipeSlicerItem, self).__init__()
        self.setZValue(Z_VAL_NODE_WIDGET + 2)

    def paint(self, painter, option, widget=None):
        """
        Draws the slicer pipe.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        #_color = QtGui.QColor(*EnumPipeSlicerStyleProperty.COLOR.value)
        _color = QtGui.QColor('#000000')
        _p1 = self.path().pointAtPercent(0)
        _p2 = self.path().pointAtPercent(1)
        _size = 6.0
        _offset = _size / 2
        _arrow_size = 4.0

        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)

        _font = painter.font()
        _font.setPointSize(12)
        painter.setFont(_font)
        _text = 'slice'
        _text_x = painter.fontMetrics().boundingRect(_text).width() / 2
        _text_y = painter.fontMetrics().boundingRect(_text).height() / 1.5
        _text_pos = QtCore.QPointF(_p1.x() - _text_x, _p1.y() - _text_y)
        _text_color = QtGui.QColor('#000000')
        _text_color.setAlpha(80)
        painter.setPen(QtGui.QPen(
            _text_color, 2, QtCore.Qt.PenStyle.SolidLine
        ))
        painter.drawText(_text_pos, _text)

        painter.setPen(QtGui.QPen(
            _color, 2, QtCore.Qt.PenStyle.DashDotLine
        ))
        painter.drawPath(self.path())

        _pen = QtGui.QPen(
            _color, 2, QtCore.Qt.PenStyle.SolidLine
        )
        _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        _pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
        painter.setPen(_pen)
        painter.setBrush(_color)

        _rect = QtCore.QRectF(_p1.x() - _offset, _p1.y() - _offset, _size, _size)
        painter.drawEllipse(_rect)

        _arrow = QtGui.QPolygonF()
        _arrow.append(QtCore.QPointF(-_arrow_size, _arrow_size))
        _arrow.append(QtCore.QPointF(0.0, -_arrow_size * 0.9))
        _arrow.append(QtCore.QPointF(_arrow_size, _arrow_size))

        _transform = QtGui.QTransform()
        _transform.translate(_p2.x(), _p2.y())
        _radians = math.atan2(_p2.y() - _p1.y(),
                             _p2.x() - _p1.x())
        _degrees = math.degrees(_radians) - 90
        _transform.rotate(_degrees)

        painter.drawPolygon(_transform.map(_arrow))
        painter.restore()

    def draw_path(self, p1, p2):
        _path = QtGui.QPainterPath()
        _path.moveTo(p1)
        _path.lineTo(p2)
        self.setPath(_path)
