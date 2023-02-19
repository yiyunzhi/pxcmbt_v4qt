import sys
from core.gui.qtimp import QtGui, QtCore, QtWidgets
from core.gui.core.class_base import ThemeStyledUiObject,I18nUiObject

_customEvt=QtCore.QEvent.registerEventType()
class TestPane(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.testW = QtWidgets.QLabel('app.RightUtil', self)
        self.mainLayout.addWidget(self.testW)
        # bind event
        # layout
        self.setLayout(self.mainLayout)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.StyleChange:
            print('---->theme changed', event, self.sender())

        super().changeEvent(event)
    def customEvent(self, event: QtCore.QEvent) -> None:
        super().customEvent(event)
        print('--->customEvent',event)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cw=TestPane(self)
        self.setCentralWidget(self.cw)
        self.btn=QtWidgets.QPushButton('TRIGGER',self)
        self.btn.clicked.connect(self.onTriggered)

    def onTriggered(self,evt):
        print('change theme')

        app.setStyleSheet('')
        app.setStyleSheet('QWidget {border: 1px solid red;}')
        _app=QtWidgets.QApplication.instance()
        for x in app.allWidgets():
            print(x.__module__,x)
            _app.postEvent(x, QtCore.QEvent(QtCore.QEvent.Type(_customEvt)))
        #_p=QtGui.QPalette()
        #_p.setColor(QtGui.QPalette.ColorRole.Text,QtGui.QColor('red'))
        #app.setPalette(_p)

app = QtWidgets.QApplication(sys.argv)

"""
    Android: Material Style
    Linux: Fusion Style
    macOS: macOS Style
    Windows: Windows Style

    https://doc.qt.io/qtforpython/overviews/qtquickcontrols2-styles.html#styling-qt-quick-controls
"""

w = MainWindow()
w.resize(1280, 720)
w.show()

sys.exit(app.exec())
