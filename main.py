import os
import sys, typing
import logging
from PySide6.QtCore import Qt, QTimer, QDir, QSignalBlocker, QCoreApplication, QObject
from PySide6.QtGui import QCloseEvent, QIcon, QAction
from PySide6.QtWidgets import (QApplication, QLabel, QCalendarWidget, QFrame, QTreeView, QWidget, QBoxLayout,
                               QTableWidget, QFileSystemModel, QPlainTextEdit, QToolBar, QMainWindow,
                               QWidgetAction, QComboBox, QSizePolicy, QInputDialog, QVBoxLayout, QHBoxLayout)
from application.define import APP_NAME, APP_VERSION
import gui.qtads as QtAds
from gui.core.define_path import LOGO_PATH
from gui.core.define import evtAppThemeChanged
from PySide6 import QtWidgets, QtCore, QtGui
from application.core.class_app_mode_select_action import HierarchyActionModel
from gui.components.tb_app_mode_sel import AppModeSelectSideBar
from gui.core.class_base import ThemeStyledUiObject

logging.basicConfig()
_logger = logging.getLogger('gui.qtads.dock_manager')
_logger2 = logging.getLogger('gui.qtads.dock_container_widget')
_logger3 = logging.getLogger('gui.qtads.dock_area_widget')
_logger.setLevel(logging.DEBUG)
_logger2.setLevel(logging.DEBUG)
_logger3.setLevel(logging.DEBUG)


class WelcomePane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__(i18n.t('app.welcome'), parent)
        self.mainLayout = QVBoxLayout(self)
        self.testW = QLabel(i18n.t('app.Welcome'), self)
        self.mainLayout.addWidget(self.testW)
        # bind event
        # layout
        self.setLayout(self.mainLayout)


class ProjectPane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__(i18n.t('app.Project'), parent)
        self.mainLayout = QVBoxLayout(self)
        self.testW = QLabel(i18n.t('app.Project'), self)
        self.mainLayout.addWidget(self.testW)
        self.setWindowTitle('app.ProjectKK')
        # bind event
        # layout
        self.setLayout(self.mainLayout)

    # def changeEvent(self, event: QtCore.QEvent) -> None:
    #
    #     if event.type() == QtCore.QEvent.Type.StyleChange:
    #         print('---->ProjectPane receive theme changed', event,self.sender())

    def customEvent(self, event: QtCore.QEvent) -> None:
        from gui.core.define import evtAppThemeChanged
        if event.type() == evtAppThemeChanged:
            print('---->ProjectPane custom event:', event)


class ProjectPropPane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__(i18n.t('app.ProjProp'), parent)
        self.mainLayout = QVBoxLayout(self)
        self.testW = QLabel(i18n.t('app.ProjProp'), self)
        self.mainLayout.addWidget(self.testW)
        # bind event
        # layout
        self.setLayout(self.mainLayout)


class ConsolePane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__(i18n.t('app.Console'), parent)
        self.mainLayout = QVBoxLayout(self)
        self.testW = QLabel(i18n.t('app.Console'), self)
        self.mainLayout.addWidget(self.testW)
        # bind event
        # layout
        self.setLayout(self.mainLayout)


class RightUtilPane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__(i18n.t('app.RightUtil'), parent)
        self.mainLayout = QVBoxLayout(self)
        self.testW = QLabel(i18n.t('app.RightUtil'), self)
        self.mainLayout.addWidget(self.testW)
        # bind event
        # layout
        self.setLayout(self.mainLayout)


class MainWindow(QMainWindow):
    # todo: add statusbar, menubar, top toolbar
    def __init__(self, parent=None):
        super().__init__(parent)
        # init local
        self.setLanguage(self.locale().language())
        #  app icon
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(LOGO_PATH)))
        self.update_window_title()
        # setup mode toolbar
        self.appModeToolbar = AppModeSelectSideBar(self)
        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self.appModeToolbar)
        self.appModeToolbar.setAllowedAreas(QtCore.Qt.ToolBarArea.LeftToolBarArea)
        self.appModeToolbar.setMovable(False)
        _mh = HierarchyActionModel(label='welcome')
        _mm = HierarchyActionModel(label='model',iconNs='fa',icon='ph.cpu')
        _mb = HierarchyActionModel(label='blocks',iconNs='fa',icon='mdi6.toy-brick')
        _mc = HierarchyActionModel(label='docu',iconNs='fa',icon='ph.folder-notch-open')
        _me = HierarchyActionModel(label='extends',iconNs='fa',icon='ph.puzzle-piece')
        _mb1 = HierarchyActionModel(label='blocks1', parent=_mb)
        _mb2 = HierarchyActionModel(label='blocks2', parent=_mb)
        _mhlp = HierarchyActionModel(label='help',iconNs='fa',icon='mdi6.help-box')
        self.appModeToolbar.addModeAction(_mh)
        self.appModeToolbar.addModeAction(_mm)
        self.appModeToolbar.addModeAction(_mb)
        self.appModeToolbar.addModeAction(_me)
        self.appModeToolbar.addModeAction(_mc)
        self.appModeToolbar.addSpacer()
        self.appModeToolbar.addSeparator()
        self.appModeToolbar.addModeAction(_mhlp)
        # menubar
        _mb = self.menuBar()
        menu = QtWidgets.QMenu('File', self)  # title and parent
        db_action = QAction("Open file", self)  # title and parent
        db_action.setStatusTip("Select a file to use as a database")
        # db_action.triggered.connect(self.open_new_db)
        menu.addAction(db_action)
        _mb.addMenu(menu)

        menu = QtWidgets.QMenu('setting', self)  # title and parent
        _action = QAction("setLanguageZh", self)  # title and parent
        _action.setStatusTip("language chinese")
        _action.triggered.connect(lambda x: self.setLanguage(QtCore.QLocale.Language.Chinese))
        menu.addAction(_action)
        _action = QAction("setLanguageDe", self)  # title and parent
        _action.setStatusTip("language German")
        _action.triggered.connect(lambda x: self.setLanguage(QtCore.QLocale.Language.German))
        menu.addAction(_action)
        _action = QAction("setThemeDark", self)  # title and parent
        _action.setStatusTip("setThemeDark")
        _action.triggered.connect(lambda x: self.setTheme('dark'))
        menu.addAction(_action)
        _action = QAction("setThemeLight", self)  # title and parent
        _action.setStatusTip("setThemeLight")
        _action.triggered.connect(lambda x: self.setTheme('default'))
        menu.addAction(_action)
        _mb.addMenu(menu)
        # status bar
        self.statusBar().showMessage("Ready")
        # docking system
        QtAds.CDockManager.setConfigFlag(QtAds.EnumDockMgrConfigFlag.OpaqueSplitterResize, True)
        QtAds.CDockManager.setConfigFlag(QtAds.EnumDockMgrConfigFlag.XmlCompressionEnabled, False)
        QtAds.CDockManager.setConfigFlag(QtAds.EnumDockMgrConfigFlag.FocusHighlighting, True)
        self.dockManager = QtAds.CDockManager(self)

        # default central widget
        self.welcomePane = WelcomePane(self)
        self.centralDockArea = self.dockManager.setCentralWidget(self.welcomePane)
        self.centralDockArea.setAllowedAreas(QtAds.EnumDockWidgetArea.OUTER_DOCK_AREAS)

        # self.modeSelectSideBar = AppModeSelectSideBar(self)
        # self.modeSelectSideBar.setMinimumSizeHintMode(QtAds.EnumMinimumSizeHintMode.FROM_DOCK_WIDGET)
        # _sa = self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.LEFT, self.modeSelectSideBar)
        # _sa.setAllowedAreas(QtAds.EnumDockWidgetArea.NO_AREA)

        # project pane
        self.projectPane = ProjectPane(self)
        self.projectPaneDockArea = self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.LEFT, self.projectPane)
        self.projectPaneDockArea.setAllowedAreas(QtAds.EnumDockWidgetArea.OUTER_DOCK_AREAS)
        self.projectPaneDockArea.setDockAreaFlag(QtAds.EnumDockAreaFlag.HideSingleWidgetTitleBar, True)
        # project prop pane
        self.projectPropPane = ProjectPropPane(self)
        self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.BOTTOM, self.projectPropPane, self.projectPaneDockArea)

        # right util pane
        self.utilPane = RightUtilPane(self)
        self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.RIGHT, self.utilPane, self.centralDockArea)
        # console pane
        self.consolePane = ConsolePane(self)
        self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.BOTTOM, self.consolePane, self.centralDockArea)
        # # create other dock widgets
        # table = QTableWidget()
        # table.setColumnCount(3)
        # table.setRowCount(10)
        # table_dock_widget = QtAds.CDockWidget("Table 1")
        # table_dock_widget.setWidget(table)
        #
        # table_dock_widget.setMinimumSizeHintMode(QtAds.EnumMinimumSizeHintMode.FROM_DOCK_WIDGET)
        # table_dock_widget.resize(250, 150)
        # table_dock_widget.setMinimumSize(200, 150)
        # table_area = self.dock_manager.addDockWidget(QtAds.EnumDockWidgetArea.LEFT, table_dock_widget)
        # self.menuView.addAction(table_dock_widget.toggleViewAction())
        #
        # table = QTableWidget()
        # table.setColumnCount(5)
        # table.setRowCount(1020)
        # table_dock_widget = QtAds.CDockWidget("Table 2")
        # table_dock_widget.setWidget(table)
        # table_dock_widget.setMinimumSizeHintMode(QtAds.EnumMinimumSizeHintMode.FROM_DOCK_WIDGET)
        # table_dock_widget.resize(250, 150)
        # table_dock_widget.setMinimumSize(200, 150)
        # table_area = self.dock_manager.addDockWidget(QtAds.EnumDockWidgetArea.BOTTOM, table_dock_widget, table_area)
        # self.menuView.addAction(table_dock_widget.toggleViewAction())
        #
        # properties_table = QTableWidget()
        # properties_table.setColumnCount(3)
        # properties_table.setRowCount(10)
        # properties_dock_widget = QtAds.CDockWidget("Properties")
        # properties_dock_widget.setWidget(properties_table)
        # properties_dock_widget.setMinimumSizeHintMode(QtAds.EnumMinimumSizeHintMode.FROM_DOCK_WIDGET)
        # properties_dock_widget.resize(250, 150)
        # properties_dock_widget.setMinimumSize(200, 150)
        # self.dock_manager.addDockWidget(QtAds.EnumDockWidgetArea.RIGHT, properties_dock_widget, central_dock_area)
        # self.menuView.addAction(properties_dock_widget.toggleViewAction())

        # self.create_perspective_ui()

    def update_window_title(self):
        self.setWindowTitle('%s %s - ' % (APP_NAME, APP_VERSION))

    def create_perspective_ui(self):
        save_perspective_action = QAction("Create Perspective", self)
        save_perspective_action.triggered.connect(self.save_perspective)
        perspective_list_action = QWidgetAction(self)
        self.perspective_combobox = QComboBox(self)
        self.perspective_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.perspective_combobox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # self.perspective_combobox.activated.connect(self.load_perspective)
        self.perspective_combobox.textActivated.connect(self.dock_manager.openPerspective)
        perspective_list_action.setDefaultWidget(self.perspective_combobox)
        self.toolBar.addSeparator()
        self.toolBar.addAction(perspective_list_action)
        self.toolBar.addAction(save_perspective_action)

    def load_perspective(self, idx):
        self.dock_manager.openPerspective(self.perspective_combobox.itemText(idx))

    def save_perspective(self):
        perspective_name, ok = QInputDialog.getText(self, "Save Perspective", "Enter Unique name:")
        if not ok or not perspective_name:
            return

        self.dock_manager.addPerspective(perspective_name)
        blocker = QSignalBlocker(self.perspective_combobox)
        self.perspective_combobox.clear()
        self.perspective_combobox.addItems(self.dock_manager.perspectiveNames())
        self.perspective_combobox.setCurrentText(perspective_name)

    def closeEvent(self, event: QCloseEvent):
        self.dockManager.deleteLater()
        super().closeEvent(event)

    def setLanguage(self, language: QtCore.QLocale.Language):
        _qApp = QtWidgets.QApplication.instance()
        _q_local = QtCore.QLocale(language)
        self.setLocale(_q_local)
        i18n.set('locale', _q_local.bcp47Name())
        _qApp.postEvent(self, QtCore.QEvent(QtCore.QEvent.Type.LanguageChange))

    def setTheme(self, theme_name='auto'):
        # todo: if current is the expect then ignore
        _app = QtWidgets.QApplication.instance()
        apply_theme(app, densityScale='-1', custom_styles=_app_css, update_palette=True, theme=theme_name)
        for x in _app.allWidgets():
            if isinstance(x, ThemeStyledUiObject):
                _app.postEvent(x, QtCore.QEvent(QtCore.QEvent.Type(evtAppThemeChanged)))


if __name__ == '__main__':
    import i18n, time
    from gui.qttheme import apply_theme
    from gui.patch.low_level_sys_ui import llSetDarkWinTitlebar
    from gui.splash import ZSplashScreen
    from gui.utils.mb_exception_hook import UncaughtHook

    useExternalTheme = True
    useMaterialTheme = 2

    i18n.load_path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'i18n'))

    i18n.set('fallback', 'en')
    i18n.set('enable_memoization', True)
    SUPPORTED_LANG_BCP47 = ['en', 'de']
    _lang_code = QtCore.QLocale().system().bcp47Name()
    i18n.set('locale', _lang_code)

    # sys.argv += ['-platform', 'windows:darkmode=2']
    app = QApplication(sys.argv)

    """
        Android: Material Style
        Linux: Fusion Style
        macOS: macOS Style
        Windows: Windows Style
        
        https://doc.qt.io/qtforpython/overviews/qtquickcontrols2-styles.html#styling-qt-quick-controls
    """
    # create a global instance of our class to register the hook
    _qt_exception_hook = UncaughtHook()
    app.setProperty('uncaughtHook', _qt_exception_hook)
    _splash = ZSplashScreen(5)
    _splash.show()
    app.processEvents()
    _splash.set_message('init style', 1)
    with open('./mbt_style.css', 'r', encoding='utf-8') as f:
        _app_css = f.read()
    #apply_theme(app, densityScale='-1', custom_styles=_app_css, update_palette=True, theme='dark')
    #app.processEvents()
    _splash.set_message('do 1', 2)
    _splash.set_message('do 2', 3)
    w = MainWindow()
    w.resize(1280, 720)
    w.setTheme('auto')
    w.show()
    _splash.set_message('finish', 5)
    _splash.finish(w)
    llSetDarkWinTitlebar(w.winId())
    sys.exit(app.exec())
