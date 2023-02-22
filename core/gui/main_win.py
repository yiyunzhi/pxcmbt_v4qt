# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : main_win.py
# ------------------------------------------------------------------------------
#
# File          : main_win.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os
import logging
from pubsub import pub
import yaml
from core.gui.qtimp import QtCore, QtGui, QtWidgets
from core.application.define import APP_NAME, APP_VERSION, EnumAppMsg
import core.gui.qtads as QtAds
from core.gui.core.define_path import LOGO_PATH
from core.application.zI18n import zI18n
from core.gui.components.widget_busy_indicator import QBusyIndicator
from core.gui.navigation.main_win_tb_mode_sel import AppModeSelectSideBar
from core.gui.navigation.define import EnumMainMenuIDs, EnumAppModeMenuIDs
from core.gui.navigation.main_win_mb_mgr import APPMenubarManager
from core.gui.ui.dlg_create_project import CreateProjectDialog
from core.application.define_path import PROJECT_PATH
from core.application.class_application_context import APP_CONTEXT
from core.gui.utils.class_i18n_text_usage_registry import I18nTextUsageRegistry
from core.gui.qttheme import apply_theme

logging.basicConfig()
_logger = logging.getLogger()


class MainWindow(QtWidgets.QMainWindow):
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
        pub.subscribe(self.on_busy_state_change_required, EnumAppMsg.sigAppBusyStateChangeRequired)
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
        self.busyIndicator = QBusyIndicator(self, modality=QtCore.Qt.WindowModality.ApplicationModal)

    def set_busy(self, state=True):
        if state:
            self.busyIndicator.start()
        else:
            self.busyIndicator.stop()

    def on_busy_state_change_required(self, state):
        self.set_busy(state)

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
        APP_CONTEXT.app = self
        self.update_app_mode_toolbar_state()

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
        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self.appModeToolbar)
        self.appModeToolbar.setAllowedAreas(QtCore.Qt.ToolBarArea.LeftToolBarArea)
        self.appModeToolbar.setMovable(False)
        _active_mode_act = self.appModeToolbar.setup()
        self.appModeToolbar.actionTriggered.connect(self.on_app_mode_changed)
        if _active_mode_act is not None:
            self.on_app_mode_changed(_active_mode_act)
        self.update_app_mode_toolbar_state()

    def init_menubar(self):
        self.menuBarManger.setup()
        self.menuViewMenu = self.menuBarManger.get_ref(EnumMainMenuIDs.VIEW_WINDOWS)

    def update_app_mode_toolbar_state(self):
        if APP_CONTEXT.app is None:
            for x in self.appModeToolbar.actions():
                if x.data():
                    if x.data().uid in [EnumAppModeMenuIDs.MODEL, EnumAppModeMenuIDs.TESTER]:
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

    def on_app_mode_changed(self, event: QtGui.QAction):
        print('on_app_mode_changed', event.data())
        if not event.isChecked():
            return
        _data = event.data()
        self.currentAppMode = _data.uid
        _layout_modifiers = _data.layoutModifiers
        for x in _layout_modifiers:
            self._handle_app_mode_layout_modifier(x)
        # todo: send signal appModeChanged

    def _handle_app_mode_layout_modifier(self, modifier):
        # todo: policy and target as enum defined.
        _w_cls = modifier.import_module()
        if _w_cls is None:
            _err = 'can not import the require module: %s.%s' % (modifier.module, modifier.class_)
            _mb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Critical, 'Error', _err, parent=self)
            _mb.show()
            _logger.error(_err)
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
        save_perspective_action = QtGui.QAction("Create Perspective", self)
        save_perspective_action.triggered.connect(self.save_perspective)
        perspective_list_action = QtWidgets.QWidgetAction(self)
        self.perspective_combobox = QtWidgets.QComboBox(self)
        self.perspective_combobox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.perspective_combobox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)

        # self.perspective_combobox.activated.connect(self.load_perspective)
        self.perspective_combobox.textActivated.connect(self.dockManager.openPerspective)
        perspective_list_action.setDefaultWidget(self.perspective_combobox)
        self.toolBar.addSeparator()
        self.toolBar.addAction(perspective_list_action)
        self.toolBar.addAction(save_perspective_action)

    def load_perspective(self, idx):
        self.dockManager.openPerspective(self.perspective_combobox.itemText(idx))

    def save_perspective(self):
        perspective_name, ok = QtWidgets.QInputDialog.getText(self, "Save Perspective", "Enter Unique name:")
        if not ok or not perspective_name:
            return

        self.dockManager.addPerspective(perspective_name)
        blocker = QtCore.QSignalBlocker(self.perspective_combobox)
        self.perspective_combobox.clear()
        self.perspective_combobox.addItems(self.dockManager.perspectiveNames())
        self.perspective_combobox.setCurrentText(perspective_name)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.dockManager.deleteLater()
        super().closeEvent(event)

    def set_language(self, language: QtCore.QLocale.Language):
        _qApp = QtWidgets.QApplication.instance()
        _q_local = QtCore.QLocale(language)
        self.setLocale(_q_local)
        zI18n.set('locale', _q_local.bcp47Name())
        # _qApp.postEvent(self, QtCore.QEvent(QtCore.QEvent.Type.LanguageChange))
        pub.sendMessage('locale.localeChange', locale=_q_local)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.Type.PaletteChange:
            APP_CONTEXT.paletteAppliedFlag = True
            self.busyIndicator.color = APP_CONTEXT.app_theme_context.get('colors').get('primaryColor')
            pub.sendMessage('theme.themeChanged', theme=APP_CONTEXT.app_theme, palette=self.palette())
            event.accept()
        super().changeEvent(event)

    @staticmethod
    def set_theme(theme_name='auto', q_app=None):
        if APP_CONTEXT.app_theme != theme_name:
            _q_app = QtWidgets.QApplication.instance() if q_app is None else q_app
            _theme_context = apply_theme(_q_app, densityScale='-1', custom_styles=APP_CONTEXT.app_css, theme=theme_name)
            QtGui.QPixmapCache.clear()
            APP_CONTEXT.app_theme = theme_name
            APP_CONTEXT.app_theme_context = _theme_context
            q_app.processEvents()
