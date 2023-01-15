# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : resize_handler.py
# ------------------------------------------------------------------------------
#
# File          : resize_handler.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from PySide6 import QtCore, QtWidgets, QtGui


class ResizeHandlerMgr:
    _this: 'CResizeHandle'
    handlePosition: QtCore.Qt.Edge
    target: QtWidgets.QWidget
    mouseOffset: int
    pressed: bool
    minSize: int
    maxSize: int
    rubberBand: QtWidgets.QRubberBand
    opaqueResize: bool
    handleWidth: int

    def __init__(self, _this):
        self._this = _this
        self.handlePosition = QtCore.Qt.Edge.LeftEdge
        self.target = None
        self.mouseOffset = 0
        self.pressed = False
        self.minSize = 0
        self.maxSize = 1
        self.rubberBand = None
        self.opaqueResize = False
        self.handleWidth = 4

    def pick(self, pos: QtCore.QPoint):
        return pos.x() if self._this.orientation() == QtCore.Qt.Orientation.Horizontal else pos.y()

    def isHorizontal(self):
        return self._this.orientation() == QtCore.Qt.Orientation.Horizontal

    def setRubberBand(self, pos: int):
        if self.rubberBand is None:
            self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Shape.Line, self.target.parentWidget())
        _geo = self._this.geometry()
        _tl = self.target.mapTo(self.target.parentWidget(), _geo.topLeft())
        if self.handlePosition in [QtCore.Qt.Edge.LeftEdge, QtCore.Qt.Edge.RightEdge]:
            _tl.setX(_tl.x() + pos)
        elif self.handlePosition in [QtCore.Qt.Edge.TopEdge, QtCore.Qt.Edge.BottomEdge]:
            _tl.setY(_tl.y() + pos)
        _geo.moveTopLeft(_tl)
        self.rubberBand.setGeometry(_geo)
        self.rubberBand.show()

    def doResizing(self, event: QtGui.QMouseEvent, force: bool = False):
        _pos = self.pick(event.pos()) - self.mouseOffset
        _old_geo = self.target.geometry()
        _new_geo = _old_geo
        if self.handlePosition == QtCore.Qt.Edge.LeftEdge:
            _new_geo.adjusted(_pos, 0, 0, 0)
            _size = max(self.minSize, min(_new_geo.width(), self.maxSize))
            _pos += _new_geo.width() - _size
            _new_geo.setWidth(_size)
            _new_geo.moveTopRight(_old_geo.topRight())
        elif self.handlePosition == QtCore.Qt.Edge.RightEdge:
            _new_geo.adjusted(0, 0, _pos, 0)
            _size = max(self.minSize, min(_new_geo.width(), self.maxSize))
            _pos -= _new_geo.width() - _size
            _new_geo.setWidth(_size)
        elif self.handlePosition == QtCore.Qt.Edge.TopEdge:
            _new_geo.adjusted(0, _pos, 0, 0)
            _size = max(self.minSize, min(_new_geo.height(), self.maxSize))
            _pos += _new_geo.height() - _size
            _new_geo.setHeight(_size)
            _new_geo.moveBottomLeft(_old_geo.bottomLeft())
        elif self.handlePosition == QtCore.Qt.Edge.BottomEdge:
            _new_geo.adjusted(0, 0, 0, _pos)
            _size = max(self.minSize, min(_new_geo.height(), self.maxSize))
            _pos -= _new_geo.height() - _size
            _new_geo.setHeight(_size)
        if self._this.opaqueResize() or force:
            self.target.setGeometry(_new_geo)
        else:
            self.setRubberBand(_pos)


class CResizeHandle(QtWidgets.QFrame):
    def __init__(self, h_pos: QtCore.Qt.Edge, parent):
        super().__init__(parent)
        self._mgr = ResizeHandlerMgr(self)
        self._mgr.target = parent
        self.setHandlePosition(h_pos)

    def setHandlePosition(self, hp: QtCore.Qt.Edge):
        self._mgr.handlePosition=hp
        if hp in [QtCore.Qt.Edge.LeftEdge,QtCore.Qt.Edge.RightEdge]:
            self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
        elif hp in [QtCore.Qt.Edge.TopEdge,QtCore.Qt.Edge.BottomEdge]:
            self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
        self.setMaxResizeSize(self.parentWidget().height() if self._mgr.isHorizontal()  else self.parentWidget().width() )
        if not self._mgr.isHorizontal():
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Fixed)
        else:
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)

    def handlePosition(self):
        return self._mgr.handlePosition

    def orientation(self):
        if self._mgr.handlePosition in [QtCore.Qt.Edge.LeftEdge, QtCore.Qt.Edge.RightEdge]:
            return QtCore.Qt.Orientation.Horizontal
        elif self._mgr.handlePosition in [QtCore.Qt.Edge.TopEdge, QtCore.Qt.Edge.BottomEdge]:
            return QtCore.Qt.Orientation.Vertical
        return QtCore.Qt.Orientation.Vertical

    def sizeHint(self) -> QtCore.QSize:
        _res=QtCore.QSize()
        if self._mgr.handlePosition in [QtCore.Qt.Edge.LeftEdge, QtCore.Qt.Edge.RightEdge]:
            _res=QtCore.QSize(self._mgr.handleWidth,self._mgr.target.height())
        elif self._mgr.handlePosition in [QtCore.Qt.Edge.TopEdge, QtCore.Qt.Edge.BottomEdge]:
            _res=QtCore.QSize(self._mgr.target.width(),self._mgr.handleWidth)
        return _res

    def isResizing(self):
        return self._mgr.pressed

    def setMinResizeSize(self, size: int):
        self._mgr.minSize=size

    def setMaxResizeSize(self, size: int):
        self._mgr.maxSize=size

    def setOpaqueResize(self, opaque: bool = True):
        self._mgr.opaqueResize=opaque

    def opaqueResize(self):
        return self._mgr.opaqueResize

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not (event.buttons() & QtCore.Qt.MouseButton.LeftButton):
            return
        self._mgr.doResizing(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._mgr.mouseOffset = self._mgr.pick(event.pos())
            self._mgr.pressed = True
            self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton and not self.opaqueResize():
            if self._mgr.rubberBand is not None:
                self._mgr.rubberBand.deleteLater()
            self._mgr.doResizing(event, True)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._mgr.pressed = False
            self.update()
