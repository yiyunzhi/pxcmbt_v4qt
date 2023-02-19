# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_recent_file_list.py
# ------------------------------------------------------------------------------
#
# File          : widget_recent_file_list.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from core.gui.qtimp import QtGui, QtCore, QtWidgets


class RecentFileItemWidget(QtWidgets.QWidget):
    sigClicked = QtCore.Signal(str)

    def __init__(self, name: str, date: str, path: str, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        self._mouseBtnPressed = False
        self.setObjectName('RecentFileItemWidget')
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.nameLabel = QtWidgets.QLabel(name, self)
        self.dateLabel = QtWidgets.QLabel(date, self)
        self.pathLabel = QtWidgets.QLabel(path, self)
        self.nameLabel.setProperty('class', 'title')
        self.dateLabel.setProperty('class', 'content')
        self.pathLabel.setProperty('class', 'content')
        self.setStyleSheet("""
            .title{font-size:14px;font-weight: bold;}
            .content{font-size:12px;color: #777;}
        """)
        # bind event

        self.installEventFilter(self)
        # layout
        self.mainLayout.setContentsMargins(5, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.nameLabel, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.dateLabel, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.pathLabel, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.insertStretch(-1, 1)
        self.setLayout(self.mainLayout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched is self:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                self._mouseBtnPressed = True
            elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and self._mouseBtnPressed:
                self._mouseBtnPressed = False
                if self.contentsRect().contains(self.mapFromGlobal(QtGui.QCursor.pos())):
                    self.sigClicked.emit(self.pathLabel.text())
        return False


class RecentFileListWidget(QtWidgets.QWidget):
    sigItemClicked = QtCore.Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        # bind event
        # layout
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(5, 0, 0, 0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setStyleSheet('#RecentFileItemWidget:hover {border-left: 3px solid palette(highlight);}#RecentFileItemWidget{margin-left:0px;}')

    def on_item_clicked(self, evt):
        self.sigItemClicked.emit(evt)

    def set_content(self, items):
        _children = self.mainLayout.findChildren(RecentFileItemWidget, '', QtCore.Qt.FindChildOption.FindDirectChildrenOnly)
        for x in _children:
            x.disconnect(self)
            x.deleteLater()
        for x in items:
            _w = RecentFileItemWidget(*x, parent=self)
            _w.sigClicked.connect(self.on_item_clicked)
            self.mainLayout.addWidget(_w)
