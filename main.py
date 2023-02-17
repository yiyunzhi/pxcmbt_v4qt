import os
import sys
import logging
from pubsub import pub
import yaml
from PySide6.QtCore import QSignalBlocker
from PySide6.QtGui import QCloseEvent, QAction
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow,
                               QWidgetAction, QComboBox, QSizePolicy, QInputDialog, QVBoxLayout)
from application.define import APP_NAME, APP_VERSION
import gui.qtads as QtAds
from gui.core.define_path import LOGO_PATH, CFG_APP_MODE_ACTION_YAML_PATH
from PySide6 import QtWidgets, QtCore, QtGui
from application.core.class_hierarchy_action_model import HierarchyActionModel
from gui.components.tb_app_mode_sel import AppModeSelectSideBar
from gui.core.define import EnumMainMenuIDs, EnumAppModeMenuIDs
from core.gui.components.mb_app import APPMenubarManager
from gui.ui.dlg_create_project import CreateProjectDialog
from application.core.base import singleton
from application.define_path import PROJECT_PATH

from gui.utils.class_i18n_text_usage_registry import I18nTextUsageRegistry

logging.basicConfig()
_logger = logging.getLogger('gui.qtads.dock_manager')
_logger2 = logging.getLogger('gui.qtads.dock_container_widget')
_logger3 = logging.getLogger('gui.qtads.dock_area_widget')
_logger.setLevel(logging.DEBUG)
_logger2.setLevel(logging.DEBUG)
_logger3.setLevel(logging.DEBUG)

MAX_RECENT_FILES = 3


class DefaultCentralPane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__(i18n.t('app.welcome'), parent)
        self.mainLayout = QVBoxLayout(self)
        self.testW = QLabel(i18n.t('app.Welcome'), self)
        self.mainLayout.addWidget(self.testW)
        # bind event
        # layout
        self.setLayout(self.mainLayout)


@singleton
class BlocksProjectTreeViewContent(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainLayout = QVBoxLayout(self)
        self.label = QLabel('Blocks', self)
        self.treeView = QtWidgets.QTreeView(self)
        # bind event
        # layout
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)


class ProjectTreeViewPane(QtAds.CDockWidget):
    def __init__(self, parent):
        super().__init__(i18n.t('app.Project'), parent)
        self.setWindowTitle('app.ProjectKK')
        # bind event
        # layout

    def setContent(self, content: QtWidgets.QWidget):
        print('set content:', content)
        self.setWidget(content)
        # todo: highlight the item, which already in dockManager another area opened

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
    # todo: top toolbar???
    def __init__(self, parent=None):
        super().__init__(parent)
        # init local
        self.set_language(self.locale().language())
        #  app icon
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(LOGO_PATH)))
        self.update_window_title()
        # main dock manager
        QtAds.CDockManager.setConfigFlag(QtAds.EnumDockMgrConfigFlag.OpaqueSplitterResize, True)
        QtAds.CDockManager.setConfigFlag(QtAds.EnumDockMgrConfigFlag.XmlCompressionEnabled, False)
        QtAds.CDockManager.setConfigFlag(QtAds.EnumDockMgrConfigFlag.FocusHighlighting, True)
        self.dockManager = QtAds.CDockManager(self)
        self.currentAppMode = None
        # menubar
        self.menuViewMenu = None
        self.menuBarManger = APPMenubarManager(self.menuBar(), self)
        self.init_menubar()
        # setup mode toolbar
        self.appModeToolbar = AppModeSelectSideBar(self)
        self.init_app_mode_sel_bar()

        # status bar
        self.statusBar().showMessage("Ready")
        # bind event
        pub.subscribe(self.on_project_topic_received, 'project')
        pub.subscribe(self.on_help_topic_received, 'help')
        # todo: open project success the appMode Model checked
        # todo: add subscriber for openProjectDialog
        # todo: add subscriber for openProject
        # todo: add subscriber for newProject
        # todo: add subscriber for open help
        # panes

        # self.modeSelectSideBar = AppModeSelectSideBar(self)
        # self.modeSelectSideBar.setMinimumSizeHintMode(QtAds.EnumMinimumSizeHintMode.FROM_DOCK_WIDGET)
        # _sa = self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.LEFT, self.modeSelectSideBar)
        # _sa.setAllowedAreas(QtAds.EnumDockWidgetArea.NO_AREA)

        # project pane
        self.projectTreeViewPaneArea = None
        # self.projectTreeViewPane = ProjectTreeViewPane(self)
        # self.projectPaneDockArea = self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.LEFT, self.projectTreeViewPane)
        # self.projectPaneDockArea.setAllowedAreas(QtAds.EnumDockWidgetArea.OUTER_DOCK_AREAS)
        # self.projectPaneDockArea.setDockAreaFlag(QtAds.EnumDockAreaFlag.HideSingleWidgetTitleBar, True)
        # project prop pane
        # self.projectPropPane = ProjectPropPane(self)
        # self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.BOTTOM, self.projectPropPane, self.projectPaneDockArea)

        # right util pane
        # self.utilPane = RightUtilPane(self)
        # self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.RIGHT, self.utilPane)
        # console pane
        # self.consolePane = ConsolePane(self)
        # self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.BOTTOM, self.consolePane)
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
        self.dockManagerState = None

    def on_project_topic_received(self, topic=pub.AUTO_TOPIC, **msg_data):
        _topic_node_name = topic.getNodeName()
        if _topic_node_name == 'new':
            self._create_new_project()
        elif _topic_node_name == 'open':
            self._open_project(msg_data.get('path'))

    def on_help_topic_received(self, topic=pub.AUTO_TOPIC, **msg_data):
        _topic_node_name = topic.getNodeName()
        if _topic_node_name == 'open':
            self._open_help_content()

    def _create_new_project(self):
        _dlg = CreateProjectDialog(self)
        _dlg.resize(480, 360)
        _res = _dlg.exec()
        if _res == QtWidgets.QDialog.DialogCode.Accepted:
            self._do_create_project(**_dlg.get_project_info())

    def _open_project(self, path: str = None):
        _msg = QtWidgets.QMessageBox(self)
        _msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        _msg.setWindowTitle(I18nTextUsageRegistry.get_i18n('app', 'error'))
        if path is None:
            path = str(PROJECT_PATH)
        if not os.path.exists(path):
            _msg.setText(I18nTextUsageRegistry.get_i18n('err', 'not_exist_f').format(path))
            _msg.exec()
            return
        if os.path.isfile(path) and path.endswith('.proj'):
            _project_path = path
        elif os.path.isdir(path):
            _file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, I18nTextUsageRegistry.get_i18n('app', 'project_open').capitalize(),
                                                                  path, 'MBT Project File (*.proj)')
            _project_path = _file_name
        else:
            _msg.setText(I18nTextUsageRegistry.get_i18n('err', 'unknown_format_f').format(path))
            _msg.exec()
            return
        _msg.deleteLater()
        self._do_open_project(_project_path)

    def _do_open_project(self, project_path):
        # todo: finish this
        print('todo: do open the project')

    def _do_create_project(self, name, path):
        # todo: finish this
        print('todo: do create the project')

    def _open_help_content(self):
        pass

    def update_window_title(self):
        self.setWindowTitle('%s %s - ' % (APP_NAME, APP_VERSION))

    def on_project_view_pane_area_visible_toggled(self, visible):
        pass

    def _add_widget_to_project_view_pane(self, widget: QtAds.CDockWidget, area: QtAds.EnumDockWidgetArea = QtAds.EnumDockWidgetArea.CENTER):
        if widget is None:
            return
        if self.projectTreeViewPaneArea is None:
            self.projectTreeViewPaneArea = self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.LEFT, widget)
            self.projectTreeViewPaneArea.setAllowedAreas(QtAds.EnumDockWidgetArea.OUTER_DOCK_AREAS)
            self.projectTreeViewPaneArea.sigViewToggled.connect(self.on_project_view_pane_area_visible_toggled)
        else:
            if not self.projectTreeViewPaneArea.isVisible():
                self.projectTreeViewPaneArea.toggleView(True)
            if widget is not None:
                if widget not in self.projectTreeViewPaneArea.dockWidgets():
                    self.dockManager.addDockWidget(area, widget, self.projectTreeViewPaneArea)
                else:
                    if widget.isClosed():
                        widget.toggleView(True)

    def _replace_widget_to_project_view_pane(self, widget: QtAds.CDockWidget, area: QtAds.EnumDockWidgetArea = QtAds.EnumDockWidgetArea.CENTER):
        if widget is None:
            return
        if self.projectTreeViewPaneArea is None:
            self._add_widget_to_project_view_pane(widget, area)
        else:
            if not self.projectTreeViewPaneArea.isVisible():
                self.projectTreeViewPaneArea.toggleView(True)
            if widget is not None:
                if widget not in self.projectTreeViewPaneArea.dockWidgets():
                    _old_l = self.projectTreeViewPaneArea.dockWidgets()
                    self.dockManager.addDockWidget(area, widget, self.projectTreeViewPaneArea)
                    for x in _old_l:
                        self.projectTreeViewPaneArea.removeDockWidget(x)
                else:
                    if widget.isClosed():
                        widget.toggleView(True)

    def init_app_mode_sel_bar(self):
        from anytree.importer import DictImporter
        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self.appModeToolbar)
        self.appModeToolbar.setAllowedAreas(QtCore.Qt.ToolBarArea.LeftToolBarArea)
        self.appModeToolbar.setMovable(False)
        with open(CFG_APP_MODE_ACTION_YAML_PATH, 'r', encoding='utf-8') as f:
            _data = yaml.load(f, Loader=yaml.SafeLoader)
            _tree = DictImporter(HierarchyActionModel).import_(_data)
        _active_mode_act = None
        _sorted = sorted(_tree.children, key=lambda x: x.oid)
        for x in _sorted:
            if x.label == '=':
                self.appModeToolbar.addSpacer()
            elif x.label == '-':
                self.appModeToolbar.addSeparator()
            elif x.label == '[]':
                _action_g = QtGui.QActionGroup(self.appModeToolbar)
                _actions = []
                for gi in x.children:
                    _action = self.appModeToolbar.addModeAction(gi, _action_g)
                    if gi.checkable and gi.state:
                        _active_mode_act = _action
                    _actions.append(_action)
                self.appModeToolbar.addActions(_actions)
            else:
                _action = self.appModeToolbar.addModeAction(x)
                if x.checkable and x.state:
                    _active_mode_act = _action
        self.appModeToolbar.actionTriggered.connect(self.on_app_mode_changed)
        if _active_mode_act is not None:
            self.on_app_mode_changed(_active_mode_act)
        self.update_app_mode_toolbar_state()

    def init_menubar(self):
        self.menuBarManger.init_ui()
        self.menuBar().triggered.connect(self.on_menubar_action_triggered)
        self.menuViewMenu = self.menuBarManger.get_ref(EnumMainMenuIDs.VIEW_WINDOWS)

    def update_app_mode_toolbar_state(self):
        if APP_CONTEXT.app is None:
            for x in self.appModeToolbar.actions():
                if x.data():
                    if x.data().uid in [EnumAppModeMenuIDs.MODEL, EnumAppModeMenuIDs.BLOCKS, EnumAppModeMenuIDs.ENV, EnumAppModeMenuIDs.TESTER]:
                        x.setVisible(False)
        else:
            for x in self.appModeToolbar.actions():
                x.setVisible(True)

    def init_toolbar(self):
        pass

    def init_statusbar(self):
        pass

    def on_menubar_action_triggered(self, event: QtGui.QAction):
        print('on_menubar_action_triggered', event.data())

    def on_app_mode_changed(self, evt: QtGui.QAction):
        if not evt.isChecked():
            return
        _data = evt.data()
        self.currentAppMode = _data.uid
        _layout_modifiers = _data.layoutModifiers
        for x in _layout_modifiers:
            self._handle_app_mode_layout_modifier(x)
        # todo: send signal appModeChanged

    def _handle_app_mode_layout_modifier(self, modifier):
        # todo: policy and target as enum defined.
        _w_cls = modifier.import_module()
        if _w_cls is None:
            _logger.error('can not import the require module: %s.%s' % (modifier.module, modifier.class_))
            return
        _w = _w_cls(self.dockManager)
        _w.setMinimumSizeHintMode(QtAds.EnumMinimumSizeHintMode.FROM_DOCK_WIDGET)
        if modifier.target == 'centerWidget':
            _cw = self.dockManager.centralWidget()
            if _cw is None:
                self.menuViewMenu.addAction(_w.toggleViewAction())
                self.dockManager.setCentralWidget(_w)
            else:
                _cw_da = _cw.dockAreaWidget()
                _cw_da_w = _cw_da.dockWidgets()
                _cw_da_ow = _cw_da.openedDockWidgets()
                if _w not in _cw_da_w:
                    self.menuViewMenu.addAction(_w.toggleViewAction())
                    if modifier.policy == 'append':
                        self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.CENTER, _w, _cw_da)
                    elif modifier.policy == 'replace':
                        self.dockManager.setCentralWidget(_w)
                elif _w not in _cw_da_ow:
                    # for the singleton instance
                    _w.toggleView(_w.isClosed())
        else:
            if modifier.target == 'projectTreeView':
                if modifier.policy == 'append':
                    self._add_widget_to_project_view_pane(_w, QtAds.EnumDockWidgetArea.CENTER)
                elif modifier.policy == 'replace':
                    self._replace_widget_to_project_view_pane(_w, QtAds.EnumDockWidgetArea.CENTER)

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

    def set_language(self, language: QtCore.QLocale.Language):
        _qApp = QtWidgets.QApplication.instance()
        _q_local = QtCore.QLocale(language)
        self.setLocale(_q_local)
        i18n.set('locale', _q_local.bcp47Name())
        # _qApp.postEvent(self, QtCore.QEvent(QtCore.QEvent.Type.LanguageChange))
        pub.sendMessage('locale.localeChange', locale=_q_local)

    def set_theme(self, theme_name='auto'):
        # todo: if current is the expect then ignore
        _app = QtWidgets.QApplication.instance()
        apply_theme(app, densityScale='-1', custom_styles=_app_css, update_palette=True, theme=theme_name)
        # for x in _app.allWidgets():
        #     if isinstance(x, ThemeStyledUiObject):
        #         _app.postEvent(x, QtCore.QEvent(QtCore.QEvent.Type(evtAppThemeChanged)))
        pub.sendMessage('theme.themeChanged', theme=theme_name, palette=self.palette())


if __name__ == '__main__':
    import i18n
    from application.class_application_context import APP_CONTEXT
    from application.define_path import I18N_PATH
    from gui.qttheme import apply_theme
    from gui.patch.low_level_sys_ui import llSetDarkWinTitlebar
    from gui.splash import ZSplashScreen
    from gui.utils.mb_exception_hook import UncaughtHook

    useExternalTheme = True
    useMaterialTheme = 2

    i18n.load_path.append(I18N_PATH)

    i18n.set('fallback', 'en')
    i18n.set('enable_memoization', True)
    SUPPORTED_LANG_BCP47 = ['en', 'de']
    _lang_code = QtCore.QLocale().system().bcp47Name()
    i18n.set('locale', _lang_code)
    QtCore.QCoreApplication.setOrganizationName("PxCEMBT")
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
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
    # apply_theme(app, densityScale='-1', custom_styles=_app_css, update_palette=True, theme='dark')
    # app.processEvents()
    _splash.set_message('do 1', 2)
    _splash.set_message('do 2', 3)
    w = MainWindow()
    w.resize(1280, 720)
    w.show()
    w.set_theme('auto')
    _splash.set_message('finish', 5)
    _splash.finish(w)
    llSetDarkWinTitlebar(w.winId())
    sys.exit(app.exec())
