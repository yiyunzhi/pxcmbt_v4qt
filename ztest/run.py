# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : run.py
# ------------------------------------------------------------------------------
#
# File          : run.py
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
from PySide6 import QtCore, QtGui, QtWidgets
from gui.ui.mainFrame import Ui_MainWindow


class ProjectViewPane(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.addBtn = QtWidgets.QPushButton('Add', self)
        self.mainLayout.addWidget(self.addBtn)
        self.mainLayout.addStretch()
        self.setLayout(self.mainLayout)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(240, 340)
    #
    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(240, 340)


class EditorDockWidget(QtWidgets.QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # todo: add custom titlebarwidget with minimized button
        # self.setTitleBarWidget()
        # QIcon icon = widget->style()->standardIcon(QStyle::SP_TitleBarMaxButton, 0, widget);
        # button->setIcon( icon );
        self.dockLocationChanged.connect(self.on_dock_loc_changed)

    def on_dock_loc_changed(self, area):
        print('---->area changed', area)


class EditorViewPane(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.addBtn = QtWidgets.QPushButton('I AM EDITOR', self)


class AppMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.resize(1024, 720)
        # self.setupUi(self)
        # remove the center widget
        self.takeCentralWidget()
        # enable nested docking
        self.setDockNestingEnabled(True)
        # style stuff

        # default docks layout
        self.projectViewDock = QtWidgets.QDockWidget(self)
        self.consoleViewDock = QtWidgets.QDockWidget(self)
        self.projectPropViewDock = QtWidgets.QDockWidget(self)
        self.editorViewDock = EditorDockWidget(self)
        # self.setCentralWidget(self.editorViewDock)

        self.editorViewDock.setObjectName('editorViewDock')
        self.projectViewDock.setWindowTitle('Project')
        self.projectPropViewDock.setWindowTitle('ProjectProp')
        self.consoleViewDock.setWindowTitle('Console')
        self.editorViewDock.setWindowTitle('Editor')

        self.docks = list()
        # self.setTabPosition(QtCore.Qt.DockWidgetArea.AllDockWidgetAreas, QtWidgets.QTabWidget.TabPosition.North)
        # self.tabifiedDockWidgets()
        self.docks.append(self.projectViewDock)
        self.docks.append(self.projectPropViewDock)
        self.docks.append(self.consoleViewDock)
        self.docks.append(self.editorViewDock)
        self.removeAllDocks()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.projectViewDock)
        self.splitDockWidget(self.projectViewDock, self.editorViewDock, QtCore.Qt.Orientation.Horizontal)
        self.splitDockWidget(self.editorViewDock, self.consoleViewDock, QtCore.Qt.Orientation.Vertical)
        self.splitDockWidget(self.projectViewDock, self.projectPropViewDock, QtCore.Qt.Orientation.Vertical)

        self.projectViewDock.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        self.projectPropViewDock.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)

        self.editorViewDock.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.createPane()
        for x in self.docks:
            x.show()
        self.resizeDocks([self.projectViewDock], [0], QtCore.Qt.Orientation.Horizontal)
        self.resizeDocks([self.projectPropViewDock], [0], QtCore.Qt.Orientation.Horizontal)

    def createPane(self):
        _projectPane = ProjectViewPane(self.projectViewDock)
        _projectPane.addBtn.clicked.connect(self.onAddClicked)
        # _projectPane.resize(240,-1)
        #_projectPane.setMinimumSize(160, 360)
        #_projectPane.resize(320, -1)
        # _projectPane.setBaseSize(240, -1)
        # _projectPane.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        # self.projectViewDock.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        _projectPane.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        self.projectViewDock.setWidget(_projectPane)

        # self.resizeDocks([self.projectViewDock],[240],QtCore.Qt.Orientation.Horizontal)

    def onAddClicked(self, evt):
        _editors = self.findChildren(EditorDockWidget)

        if _editors:
            _first_editor = _editors[0]
            if not _first_editor.isFloating():
                _editor_dw = EditorDockWidget(self)
                _editor_dw.setWindowTitle('NewCreateEditor_%s' % len(_editors))
                _editor_dw.setWidget(EditorViewPane(_editor_dw))
                self.docks.append(_editor_dw)
                self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, _editor_dw, QtCore.Qt.Orientation.Horizontal)
                self.tabifyDockWidget(_first_editor, _editor_dw)

                self.showDocks()
            else:
                print('floating handle')
        else:
            print('no editor, then add dock widget to main frame')

    def removeAllDocks(self):
        for x in self.docks:
            self.removeDockWidget(x)

    def showDocks(self):
        for x in self.docks:
            x.show()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        _old_size = event.oldSize()

        #self.resizeDocks([self.projectViewDock], [0], QtCore.Qt.Orientation.Horizontal)


app = QtWidgets.QApplication(sys.argv)
window = AppMainWindow()
window.show()
app.exec()
