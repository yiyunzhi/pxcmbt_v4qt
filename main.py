import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLabel, QApplication, QMainWindow
from gui.qtads.dock_manager import CDockManager
from gui.qtads.dock_widget import CDockWidget
from gui.qtads.define import EnumDockWidgetArea

class mainFrame(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self)
        self.qLabel = QLabel(self)
        self.qLabel.setText('ABCSJIWJIFJW')
        self.dw = CDockWidget(parent=self,title='Test')
        self.dw.setWidget(self.qLabel)
        self.dM = CDockManager(self)
        self.dM.addDockWidget(EnumDockWidgetArea.TOP, self.dw)


app = QApplication(sys.argv)
window = mainFrame()
window.show()
app.exec()
