# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_overlay_disable_item.py
# ------------------------------------------------------------------------------
#
# File          : class_overlay_disable_item.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from gui import QtGui, QtCore, QtWidgets

from ..core.define import Z_VAL_NODE_WIDGET


class XDisabledItem(QtWidgets.QGraphicsItem):
    """
    Node disabled overlay item.

    Args:
        parent (NodeItem): the parent node item.
        text (str): disable overlay text.
    """

    def __init__(self, parent=None, text=None):
        super(XDisabledItem, self).__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET + 2)
        self.setVisible(False)
        self.proxyMode = False
        self.color = (0, 0, 0, 255)
        self.text = text

    def boundingRect(self):
        return self.parentItem().boundingRect()

    def paint(self, painter, option, widget):
        """
        Draws the overlay disabled X item on top of a node item.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        _margin = 20
        _rect = self.boundingRect()
        _dis_rect = QtCore.QRectF(_rect.left() - (_margin / 2),
                                  _rect.top() - (_margin / 2),
                                  _rect.width() + _margin,
                                  _rect.height() + _margin)
        if not self.proxyMode:
            _pen = QtGui.QPen(QtGui.QColor(*self.color), 8)
            _pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            painter.setPen(_pen)
            painter.drawLine(_dis_rect.topLeft(), _dis_rect.bottomRight())
            painter.drawLine(_dis_rect.topRight(), _dis_rect.bottomLeft())

        _bg_color = QtGui.QColor(*self.color)
        _bg_color.setAlpha(100)
        _bg_margin = -0.5
        _bg_rect = QtCore.QRectF(_dis_rect.left() - (_bg_margin / 2),
                                 _dis_rect.top() - (_bg_margin / 2),
                                 _dis_rect.width() + _bg_margin,
                                 _dis_rect.height() + _bg_margin)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        painter.setBrush(_bg_color)
        painter.drawRoundedRect(_bg_rect, 5, 5)

        if not self.proxyMode:
            _point_size = 4.0
            _pen = QtGui.QPen(QtGui.QColor(155, 0, 0, 255), 0.7)
        else:
            _point_size = 8.0
            _pen = QtGui.QPen(QtGui.QColor(155, 0, 0, 255), 4.0)

        painter.setPen(_pen)
        painter.drawLine(_dis_rect.topLeft(), _dis_rect.bottomRight())
        painter.drawLine(_dis_rect.topRight(), _dis_rect.bottomLeft())

        _point_pos = (_dis_rect.topLeft(), _dis_rect.topRight(),
                      _dis_rect.bottomLeft(), _dis_rect.bottomRight())
        painter.setBrush(QtGui.QColor(255, 0, 0, 255))
        for p in _point_pos:
            p.setX(p.x() - (_point_size / 2))
            p.setY(p.y() - (_point_size / 2))
            _point_rect = QtCore.QRectF(
                p, QtCore.QSizeF(_point_size, _point_size))
            painter.drawEllipse(_point_rect)

        if self.text and not self.proxyMode:
            _font = painter.font()
            _font.setPointSize(10)

            painter.setFont(_font)
            _font_metrics = QtGui.QFontMetrics(_font)
            _font_width = _font_metrics.boundingRect(self.text).width()
            _font_height = _font_metrics.height()
            _txt_w = _font_width * 1.25
            _txt_h = _font_height * 2.25
            _text_bg_rect = QtCore.QRectF((_rect.width() / 2) - (_txt_w / 2),
                                          (_rect.height() / 2) - (_txt_h / 2),
                                          _txt_w, _txt_h)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 0.5))
            painter.setBrush(QtGui.QColor(*self.color))
            painter.drawRoundedRect(_text_bg_rect, 2, 2)

            _text_rect = QtCore.QRectF((_rect.width() / 2) - (_font_width / 2),
                                       (_rect.height() / 2) - (_font_height / 2),
                                       _txt_w * 2, _font_height * 2)

            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 1))
            painter.drawText(_text_rect, self.text)

        painter.restore()
