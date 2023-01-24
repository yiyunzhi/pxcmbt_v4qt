import sys, logging
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QListWidget, QPlainTextEdit
from PySide6 import QtCore
from gui.qtads.dock_manager import CDockManager
from gui.qtads.dock_widget import CDockWidget
from gui.qtads.define import EnumDockWidgetArea
from gui.qtads import CDockAreaWidget

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s \t%(levelname)-10s %(thread)d %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")


class PaneDiskInfo(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QVBoxLayout()
        self.list = QListWidget(self)
        self.mainLayout.addWidget(self.list)
        self.setLayout(self.mainLayout)
        for x in QtCore.QStorageInfo.mountedVolumes():
            self.list.addItem('%s : %s Total: %s' % (x.displayName(), x.name(), x.bytesTotal()))


_TEXT = """
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, 
sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea 
takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, 
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero 
eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem 
ipsum dolor sit amet.
"""


class PaneText(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QVBoxLayout()
        self.list = QPlainTextEdit(self)
        self.mainLayout.addWidget(self.list)
        self.setLayout(self.mainLayout)
        self.list.setPlainText(_TEXT)


class mainFrame(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self)
        self.resize(1024, 720)
        self.dockManager = CDockManager(self)

        self.dw = CDockWidget(parent=self.dockManager, title='DiskInfo')
        self.diskInfoPane = PaneDiskInfo(self.dw)

        self.dw.setWidget(self.diskInfoPane)

        self.dw2 = CDockWidget(parent=self.dockManager, title='QLabel2')
        self.textPane = PaneText(self.dw2)
        self.dw2.setWidget(self.textPane)

        self.dw3 = CDockWidget(parent=self.dockManager, title='QLabel3')

        self.textPane2 = PaneText(self.dw3)
        self.dw3.setWidget(self.textPane2)

        # normal add dock without da
        # self.dockManager.addDockWidget(EnumDockWidgetArea.TOP, self.dw2)
        # self.dockManager.addDockWidget(EnumDockWidgetArea.TOP, self.dw)
        # normal add addDockWidgetTab without da
        # self.dockManager.addDockWidgetTab(EnumDockWidgetArea.CENTER,self.dw2)
        # self.dockManager.addDockWidgetTab(EnumDockWidgetArea.CENTER,self.dw)
        # add floating
        # self.dockManager.addDockWidgetFloating(self.dw3)
        # self.dockManager.addDockWidget(EnumDockWidgetArea.TOP, self.dw2)
        # add dock with da
        # _da=self.dockManager.addDockWidget(EnumDockWidgetArea.CENTER, self.dw)
        # self.dockManager.addDockWidget(EnumDockWidgetArea.CENTER, self.dw2,_da)
        # self.dockManager.addDockWidget(EnumDockWidgetArea.CENTER, self.dw3,_da)
        # add dock with new da
        # _dc=self.dockManager.dockContainers()
        # or
        # _dc=self.dockManager
        self.dockManager.addDockArea(CDockAreaWidget(self.dockManager, self.dockManager), EnumDockWidgetArea.CENTER)
        _da = self.dockManager.dockArea(0)
        self.dockManager.addDockWidgetTabToArea(self.dw, _da)
        self.dockManager.addDockWidgetTabToArea(self.dw2, _da)
        self.dockManager.addDockWidget(EnumDockWidgetArea.BOTTOM, self.dw3)


# sys.argv+=['-platform','windows:darkmode=2']
app = QApplication(sys.argv)
window = mainFrame()
window.show()
sys.exit(app.exec())
