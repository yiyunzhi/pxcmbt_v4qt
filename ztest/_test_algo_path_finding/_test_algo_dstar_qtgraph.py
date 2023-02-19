# -*- coding: utf-8 -*-
import sys

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_algo_dstar_qtgraph.py
# ------------------------------------------------------------------------------
#
# File          : _test_algo_dstar_qtgraph.py
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
from core.gui.qtimp import QtGui, QtCore, QtWidgets
from ztest._test_algo_dstar_np import Map, DStar, Cell


class LiveWire(QtWidgets.QGraphicsPathItem):
    def __init__(self, parent):
        super().__init__(parent)
        self._sourcePos = QtCore.QPoint(0, 0)
        self._currentPos = QtCore.QPoint(0, 0)

        self.pathFindMap = Map(0, 0)
        self.pathFindMap.debug = True
        self.pathFinder = DStar(self.pathFindMap)
        self.pathFinderCellSize = 50

    def paint(self, painter, option, widget=None) -> None:
        _pen = QtGui.QPen(QtGui.QColor('red'), 2)
        painter.save()
        painter.setPen(_pen)
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        painter.drawPath(self.path())
        painter.restore()

    def draw_path(self, start_pos, cursor_pos=None):
        _pos1 = start_pos
        if cursor_pos:
            _pos2 = cursor_pos
            self._currentPos = _pos2
        else:
            return
        _line = QtCore.QLineF(_pos1, _pos2)
        _path = QtGui.QPainterPath()
        _path.moveTo(_line.x1(), _line.y1())

        _path.lineTo(_pos2)
        self.setPath(_path)

    def reset_path(self):
        _path = QtGui.QPainterPath(QtCore.QPointF(0.0, 0.0))
        self.setPath(_path)

    def _mapToGlobal(self, pt):
        return self.scene().views()[0].mapFromScene(pt)

    def update_map_rect(self, rect: QtCore.QRect, obstacles: [QtGui.QPainterPath]):
        if not obstacles or True:
            self.pathFindMap = Map(10,10)
            self.pathFindMap.debug = True
            self.pathFinder = DStar(self.pathFindMap)
        else:
            pass



            for x in obstacles:
                print([(x.elementAt(i).x,x.elementAt(i).y) for i in range(x.elementCount())])
                # for p in x.toSubpathPolygons():
                #     _xp = self.mapFromScene(p)
                #     _ptl = [(pp.toPoint() / self.pathFinderCellSize).toTuple() for pp in _xp.toList()]
                #
                #     print('--->xbr tlpoint:', _ptl)
                #     self.pathFindMap.set_obstacle(_ptl)

        _start_cell=self.pathFindMap.cellArray[0][0]
        _end_cell=self.pathFindMap.cellArray[int((self.pathFindMap.row-1)/2)][self.pathFindMap.col-1]
        self.pathFindMap.print_map()
        print(_start_cell, _end_cell,self.pathFindMap.row,self.pathFindMap.col)
        print('---' * 20)
        self.pathFinder.run(_start_cell, _end_cell)


class TestView(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setScene(QtWidgets.QGraphicsScene(self))
        self._lastScenePos = QtCore.QPoint(0, 0)
        self._liveWire = LiveWire(None)
        self._liveWire.setVisible(False)
        self._liveRect = QtWidgets.QGraphicsRectItem(1, 1, 0, 0)
        self._liveRect.setVisible(False)
        self.scene().addItem(self._liveRect)
        self.scene().addItem(self._liveWire)
        self._obstacle1 = QtWidgets.QGraphicsRectItem(0, 0, 50, 100)
        self._obstacle2 = QtWidgets.QGraphicsRectItem(75, 60, 100, 50)
        self.scene().addItem(self._obstacle1)
        self.scene().addItem(self._obstacle2)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._liveWire.setVisible(True)
        self._liveRect.setVisible(True)
        self._liveWire._sourcePos = self.mapToScene(event.position().toPoint())
        self._liveWire.draw_path(self._liveWire._sourcePos, self._liveWire._sourcePos)
        super(TestView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._liveWire.setVisible(False)
        self._liveRect.setVisible(False)
        super(TestView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        _pos = self.mapToScene(event.position().toPoint()).toPoint()
        _rect = QtCore.QRect(self._liveWire._sourcePos.toPoint(), _pos)
        self._liveRect.setRect(_rect)
        self._liveWire.draw_path(self._liveWire._sourcePos, _pos)

        _item_under_rect = self.scene().items(_rect, QtCore.Qt.ItemSelectionMode.IntersectsItemShape)
        _live_wire_obstacle_path = list()
        if _item_under_rect:
            for x in _item_under_rect:
                if x in [self._liveRect, self._liveWire]:
                    continue
                _xbr = x.boundingRect().toRect()
                _p = QtGui.QPainterPath()
                _p.moveTo(_xbr.topLeft())
                _p.addRect(_xbr)
                _live_wire_obstacle_path.append(_p)
        if _rect.width() > 200 and _rect.height() > 200:
            self._liveWire.update_map_rect(_rect, _live_wire_obstacle_path)
        super(TestView, self).mouseMoveEvent(event)


app = QtWidgets.QApplication(sys.argv)
v = TestView(None)
v.resize(1000, 720)
v.show()
sys.exit(app.exec())
