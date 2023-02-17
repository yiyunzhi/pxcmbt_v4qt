# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_minimap_view.py
# ------------------------------------------------------------------------------
#
# File          : class_minimap_view.py
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


class MiniMapGraphicsView(QtWidgets.QGraphicsView):

    def __init__(self, parent, view: QtWidgets.QGraphicsView):
        super().__init__(parent)
        self._dragStartPos = None
        self.mainView = view
        self.setScene(self.mainView.scene())
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setFixedSize(200, 200)
        self.viewport().setFixedSize(self.contentsRect().size())
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setFocusProxy(self.mainView)
        self.band = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Shape.Rectangle, self)
        self.band.setWindowOpacity(0.5)
        self.band.hide()
        self._bind_event()

    def _bind_event(self):
        self.mainView.sigSceneUpdate.connect(self.on_scene_updated)
        self.mainView.sigMovedNodes.connect(self.on_scene_updated)
        self.mainView.sigBackdropNodeUpdated.connect(self.on_scene_updated)
        self.mainView.sigNodeInserted.connect(self.on_scene_updated)

    def on_scene_updated(self, evt=None):
        self.adjustRubberband()
        self.zoomToFit()

    def centerOn(self, pos):
        if self.band.isVisible():
            self.mainView.centerOn(self.mapToScene(pos))
            _rect = self.band.geometry()
            _rect.moveCenter(pos)
            self.band.setGeometry(_rect)

    def mousePressEvent(self, event):
        if self.band.isVisible() and event.button() == QtCore.Qt.MouseButton.LeftButton:
            _rect = self.band.geometry()
            if _rect.contains(event.pos()):
                self._dragStartPos = event.pos()
            else:
                self.centerOn(event.pos())

    def mouseMoveEvent(self, event):
        if self.band.isVisible() and event.buttons() == QtCore.Qt.MouseButton.LeftButton and self._dragStartPos is not None:
            self.centerOn(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.band.isVisible():
            self.viewport().unsetCursor()
            self._dragStartPos = None

    def adjustRubberband(self):
        _scene = self.scene()
        if _scene is None:
            return
        _rect = self.mainView.mapToScene(self.mainView.rect()).boundingRect()
        if not _rect.contains(_scene.sceneRect()):
            rect = self.mapFromScene(_rect).boundingRect()
            self.band.setGeometry(rect)
            self.band.show()
        else:
            self.band.hide()

    def zoomToFit(self):
        self.fitInView(self.scene().sceneRect().adjusted(-20, -20, 20, 20), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
