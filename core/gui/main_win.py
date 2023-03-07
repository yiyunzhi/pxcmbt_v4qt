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
from collections.abc import Iterable
from pubsub import pub
import yaml
import core.gui.qtads as QtAds
from core.application.zI18n import zI18n
from core.application.define_path import PROJECT_PATH
from core.application.class_application_context import ApplicationContext
from core.application.define import APP_NAME, APP_VERSION, EnumAppMsg, RECENT_MAX_LEN
from core.application.class_project import Project
from .qtimp import QtCore, QtGui, QtWidgets
from .core.class_base import ZView, ZViewModifier
from .core.define_path import LOGO_PATH
from .core.define import EnumLayoutModifierPolicy, EnumGuiViewName, EnumLayoutModifierTarget
from .core.class_icon_repository import IconRepository
from .components.widget_busy_indicator import QBusyIndicator
from .navigation.define import EnumMainMenuIDs, EnumAppModeMenuIDs
from .ui.dlg_create_project import CreateProjectDialog
from .utils.helper import get_qApp
from .qttheme import apply_theme
from . import GUI_VIEW_FACTORY

logging.basicConfig()
_logger = logging.getLogger()
_app_ctx = ApplicationContext()


class OPIProgressDialog:
    def __init__(self, title='in progressing...', cancelable=False, cancel_text='cancel', min_val=0, max_val=100, parent=None):
        self.pg: QtWidgets.QProgressDialog = None
        self.parent = parent
        self.minVal = min_val
        self.maxVal = max_val
        self.title = title
        self.cancelable = cancelable
        self.cancelText = cancel_text

    def set_value(self, val):
        self.pg.setValue(val)

    def set_label(self, val):
        self.pg.setLabelText(val)

    def __enter__(self):
        self.pg = QtWidgets.QProgressDialog(self.title, self.cancelText, self.minVal, self.maxVal, self.parent)
        self.pg.setWindowTitle(self.title)
        self.pg.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        if not self.cancelable:
            self.pg.setCancelButton(None)
        self.pg.setValue(0)
        self.pg.show()
        get_qApp().processEvents()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pg.done(self.maxVal)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._iconRepo: IconRepository = IconRepository()
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
        self.currentFocusedWidget = None
        self.previousInFocusWidget = None
        self.projectTreeViewPaneArea = None
        self.currentAppMode = None
        # menubar
        self.menuViewMenu = None
        # self.setMenu
        # self.menuBar = APPMenubarManager(self.menuBar(), self)
        self.init_menubar()
        self.toolbar = self.init_toolbar()
        # setup mode toolbar
        # self.appModeToolbar = AppModeSelectSideBar(self)
        self.appModeToolbar = None
        self.init_app_mode_sel_bar()

        # status bar
        self.statusBar().showMessage("Ready")
        # bind event
        self.dockManager.sigFocusedDockWidgetChanged.connect(self.on_dock_widget_focused_changed)
        pub.subscribe(self.on_project_topic_received, 'project')
        pub.subscribe(self.on_help_topic_received, 'help')
        pub.subscribe(self.on_busy_state_change_required, EnumAppMsg.sigAppBusyStateChangeRequired)
        # panes
        # self.create_perspective_ui()
        self.dockManagerState = None
        self.busyIndicator = QBusyIndicator(self, modality=QtCore.Qt.WindowModality.ApplicationModal)

    def set_busy(self, state=True):
        if state:
            self.busyIndicator.start()
        else:
            self.busyIndicator.stop()

    def on_dock_widget_focused_changed(self, from_w, to_w):
        self.currentFocusedWidget = to_w
        self.previousInFocusWidget = from_w
        # todo: change the menu state by given focused windows

    def on_busy_state_change_required(self, state):
        self.set_busy(state)

    def on_project_topic_received(self, topic=pub.AUTO_TOPIC, **msg_data):
        _topic_node_name = topic.getNodeName()
        if _topic_node_name == 'new':
            self._create_new_project()
        elif _topic_node_name == 'open':
            _path = msg_data.get('path')
            if _path:
                _path = os.path.join(_path[0], _path[1] + '.proj')
            self._open_project(_path)

    def on_help_topic_received(self, topic=pub.AUTO_TOPIC, **msg_data):
        _topic_node_name = topic.getNodeName()
        if _topic_node_name == 'open':
            self._open_help_content()

    def _create_new_project(self):
        _dlg = CreateProjectDialog(self)
        _dlg.resize(480, 360)
        _res = _dlg.exec()
        if _res == QtWidgets.QDialog.DialogCode.Accepted:
            _ret = self._do_create_project(**_dlg.get_project_info())
            if _ret:
                self.update_window_title()

    def _open_project(self, path: str = None):
        _msg = QtWidgets.QMessageBox(self)
        _msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        _msg.setWindowTitle(zI18n.t('app.error'))
        if path is None:
            path = str(PROJECT_PATH)
        if not os.path.exists(path):
            _msg.setText(zI18n.t('err.not_exist_f').format(path))
            _msg.exec()
            return
        if os.path.isfile(path) and path.endswith('.proj'):
            _project_path = path
        elif os.path.isdir(path):
            _file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, zI18n.t('app.project_open').capitalize(),
                                                                  path, 'MBT Project File (*.proj)')
            _project_path = _file_name
        else:
            _msg.setText(zI18n.t('err.unknown_format_f').format(path))
            _msg.exec()
            return
        _msg.deleteLater()
        if not _project_path:
            return
        if _app_ctx.project is not None and _app_ctx.project.projectEntryFilePath == _project_path:
            return
        self._do_open_project(_project_path)
        self.update_window_title()

    def _record_the_recent_project(self, project: Project):
        _rl = list()
        _setting = QtCore.QSettings()
        _setting.beginGroup('recentFiles')
        _size = _setting.beginReadArray('files')
        for i in range(_size):
            _setting.setArrayIndex(i)
            _rl.append([_setting.value('name'), _setting.value('date'), _setting.value('path')])
        _setting.endArray()
        _filtered = list(filter(lambda x: x[0] == project.name, _rl))
        if _filtered:
            for x in _filtered:
                x[1] = project.header.lastUpdatedAt
        else:
            _rl.insert(0, [project.name, project.header.lastUpdatedAt, project.projectPath])
        _setting.beginWriteArray('files')
        _rl = _rl[0:RECENT_MAX_LEN]
        for i in range(len(_rl)):
            _setting.setArrayIndex(i)
            _setting.setValue('name', _rl[i][0])
            _setting.setValue('date', _rl[i][1])
            _setting.setValue('path', _rl[i][2])
        _setting.endArray()
        _setting.endGroup()
        _setting.sync()
        pub.sendMessage(EnumAppMsg.sigProjectStateChanged)

    def _do_save_current_project(self):
        # todo: finish this, if current has project then save it firstly
        # todo: how to check if content is changed??
        pass

    def _do_open_project(self, project_path):
        self._do_save_current_project()
        with OPIProgressDialog(parent=self) as pg:
            pg.set_value(50)
            if _app_ctx.project is None:
                _proj = Project('__tmp__5tdw/xt')
                _proj.load_project(project_path)
                _app_ctx.project = _proj
            else:
                _app_ctx.project.load_project(project_path)
            self.update_app_mode_toolbar_state()
            self._record_the_recent_project(_app_ctx.project)

    def _do_create_project(self, name, path):
        self._do_save_current_project()
        with OPIProgressDialog(parent=self) as pg:
            pg.set_value(20)
            _proj = Project(name)
            _proj.set_workspace_path(path)
            _proj.save_project()
            pg.set_value(30)
            _proj.save_all()
            _app_ctx.project = _proj
            pg.set_value(70)
            self.update_app_mode_toolbar_state()
            self._record_the_recent_project(_proj)
        return True

    def _do_save_project(self):
        pass

    def _open_help_content(self):
        pass

    def set_progress(self):
        pass

    def update_window_title(self):
        _project_name = '' if _app_ctx.project is None else _app_ctx.project.name
        self.setWindowTitle('%s %s - %s' % (APP_NAME, APP_VERSION, _project_name))

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
                _old_l = self.projectTreeViewPaneArea.dockWidgets()
                for x in _old_l:
                    x.toggleView(False)
                if widget not in self.projectTreeViewPaneArea.dockWidgets():
                    self.dockManager.addDockWidget(area, widget, self.projectTreeViewPaneArea)
                else:
                    if widget.isClosed():
                        widget.toggleView(True)

    def init_app_mode_sel_bar(self):
        self.appModeToolbar = GUI_VIEW_FACTORY.create_view(EnumGuiViewName.APP_MODE_SEL_SIDEBAR, parent=self)
        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self.appModeToolbar)
        self.appModeToolbar.setAllowedAreas(QtCore.Qt.ToolBarArea.LeftToolBarArea)
        self.appModeToolbar.setMovable(False)
        self.appModeToolbar.zViewManager.set_content(None)
        self.appModeToolbar.zViewManager.sigChangeMainViewRequired.connect(self.on_view_manager_change_main_view_required)
        self.appModeToolbar.zViewManager.ensure_view()
        self.update_app_mode_toolbar_state()

    def init_menubar(self):
        _mb = GUI_VIEW_FACTORY.create_view(EnumGuiViewName.APP_MENU_BAR, parent=self)
        _mb.zViewManager.set_content(None)
        self.setMenuBar(_mb)
        self.menuViewMenu = _mb.zViewManager.get_ref(EnumMainMenuIDs.VIEW_WINDOWS)

    def update_app_mode_toolbar_state(self):
        if _app_ctx.project is None:
            self.appModeToolbar.zViewManager.set_state('noProject')
        else:
            self.appModeToolbar.zViewManager.set_state('projectLoaded')

    def init_toolbar(self):
        _toolbar = QtWidgets.QToolBar('File', self)
        _toolbar.setIconSize(QtCore.QSize(20,20))
        _toolbar.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground,True)
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, _toolbar)
        _toolbar.setAllowedAreas(QtCore.Qt.ToolBarArea.TopToolBarArea)
        _toolbar.setMovable(False)
        # todo: open, save, saveas saveall | undo redo

        _action_new = QtGui.QAction('!New', self)
        _new_icon = self._iconRepo.get_icon(_action_new, icon_ns=None, icon_name='icons:new_file.svg', setter='setIcon')
        _action_new.setIcon(_new_icon)

        _action_open = QtGui.QAction('!Open', self)
        _open_icon = self._iconRepo.get_icon(_action_open, icon_ns=None, icon_name='icons:open.svg', setter='setIcon')
        _action_open.setIcon(_open_icon)
        #_action_open.setEnabled(False)

        _action_save = QtGui.QAction('!Save', self)
        _save_icon = self._iconRepo.get_icon(_action_save, icon_ns=None, icon_name='icons:save.svg', setter='setIcon')
        _action_save.setIcon(_save_icon)

        _action_save_as = QtGui.QAction(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton), '!SaveAs', self)
        _save_as_icon = self._iconRepo.get_icon(_action_save_as, icon_ns=None, icon_name='icons:save_as.svg', setter='setIcon')
        _action_save_as.setIcon(_save_as_icon)

        _action_save_all = QtGui.QAction(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveAllButton), '!SaveAll', self)
        _save_all_icon = self._iconRepo.get_icon(_action_save_all, icon_ns=None, icon_name='icons:save_all.svg', setter='setIcon')
        _action_save_all.setIcon(_save_all_icon)

        _action_undo = QtGui.QAction(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowBack), '!Undo', self)
        _undo_icon = self._iconRepo.get_icon(_action_undo, icon_ns=None, icon_name='icons:undo.svg', setter='setIcon')
        _action_undo.setIcon(_undo_icon)

        _action_redo = QtGui.QAction(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowForward), '!Redo', self)
        _redo_icon = self._iconRepo.get_icon(_action_redo,icon_ns=None, icon_name='icons:redo.svg', setter='setIcon')
        _action_redo.setIcon(_redo_icon)

        _toolbar.addAction(_action_new)
        _toolbar.addAction(_action_open)
        _toolbar.addAction(_action_save)
        _toolbar.addAction(_action_save_as)
        _toolbar.addAction(_action_save_all)
        _toolbar.addSeparator()
        _toolbar.addAction(_action_undo)
        _toolbar.addAction(_action_redo)
        return _toolbar

    def init_statusbar(self):
        pass

    def get_current_app_mode_action(self) -> QtGui.QAction:
        return self.appModeToolbar.zViewManager.activeModeAction

    def on_menubar_action_triggered(self, event: QtGui.QAction):
        if event.data().uid == EnumMainMenuIDs.EDIT_UNDO:
            if self.currentFocusedWidget is not None and isinstance(self.currentFocusedWidget, ZView):
                _undo_stack = self.currentFocusedWidget.zViewManager.undo_stack
                if _undo_stack.canUndo():
                    _msg_b = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, 'undo', 'do you wanna undo: <{}>'.format(_undo_stack.undoText()),
                                                   QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, self)
                    if _msg_b.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
                        _undo_stack.undo()
        elif event.data().uid == EnumMainMenuIDs.EDIT_REDO:
            if self.currentFocusedWidget is not None and isinstance(self.currentFocusedWidget, ZView):
                _undo_stack = self.currentFocusedWidget.zViewManager.undo_stack
                if _undo_stack.canRedo():
                    _msg_b = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Information, 'undo', 'do you wanna undo: <{}>'.format(_undo_stack.redoText()),
                                                   QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, self)
                    if _msg_b.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
                        _undo_stack.redo()

    def on_view_manager_change_main_view_required(self, category, data):
        if category == 'viewModify':
            self.handle_view_modify(data)
        elif category == 'setViewTitle':
            self.handle_change_view_title(data)
        elif category == 'removeViews':
            self.handle_remove_views(data)
        elif category == 'registerWithProject':
            _app_ctx.project.register_with_project(data)

    def find_z_view_by_view_id(self, view_id) -> ZView:
        for x in self.dockManager.dockWidgets():
            if isinstance(x, ZView):
                if x.zViewManager.view_id == view_id:
                    return x

    def handle_remove_views(self, view_ids: list):
        for x in view_ids:
            _z_view = self.find_z_view_by_view_id(x)
            if _z_view:
                if isinstance(_z_view, QtAds.CDockWidget):
                    self.dockManager.removeDockWidget(_z_view)
                _z_view.deleteLater()

    def handle_change_view_title(self, view_title_dict: dict):
        for k, v in view_title_dict.items():
            _zview = self.find_z_view_by_view_id(k)
            if _zview:
                _zview.title = v

    def handle_view_modify(self, modifiers):
        # fixme: handle for the modifier is not dockable???
        if not isinstance(modifiers, Iterable):
            modifiers = [modifiers]
        assert all([isinstance(x, ZViewModifier) for x in modifiers]), 'ZViewModifier type is required.'
        for modifier in modifiers:
            _view = GUI_VIEW_FACTORY.create_view(modifier.viewName, parent=self.dockManager, **modifier.options)
            if _view is None:
                _err = 'can not create the view with name {}'.format(modifier.viewName)
                _mb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Critical, 'Error', _err, parent=self)
                _mb.show()
                _logger.error(_err)
                return
            if _view not in self.dockManager.dockWidgets():
                _view.setMinimumSizeHintMode(QtAds.EnumMinimumSizeHintMode.FROM_DOCK_WIDGET)
                if isinstance(_view, ZView):
                    _ccid = _view.zViewManager.content_container.get_id()
                    _view.zViewManager.sigChangeMainViewRequired.connect(self.on_view_manager_change_main_view_required)
                    _content = None
                    if _app_ctx.project and _app_ctx.project.is_content_container_file_assigned(_ccid):
                        _content = _app_ctx.project.get_content_by_ccid(_ccid)
                    _view.zViewManager.set_content(_content)
            else:
                pass
            if modifier.target == EnumLayoutModifierTarget.CENTER_WIDGET:
                _cw = self.dockManager.centralWidget()
                if _cw is None:
                    self.menuViewMenu.addAction(_view.toggleViewAction())
                    self.dockManager.setCentralWidget(_view)
                else:
                    _cw_da = _cw.dockAreaWidget()
                    _cw_da_w = _cw_da.dockWidgets()
                    _cw_da_ow = _cw_da.openedDockWidgets()
                    if _view not in _cw_da_w:
                        self.menuViewMenu.addAction(_view.toggleViewAction())
                        if modifier.policy == EnumLayoutModifierPolicy.APPEND:
                            self.dockManager.addDockWidget(QtAds.EnumDockWidgetArea.CENTER, _view, _cw_da)
                        elif modifier.policy == EnumLayoutModifierPolicy.REPLACE:
                            self.dockManager.setCentralWidget(_view)
                    elif _view not in _cw_da_ow:
                        # toggle view is enough for an singleton instance.
                        _view.toggleView(_view.isClosed())
            elif modifier.target == EnumLayoutModifierTarget.FLOAT_RIGHT:
                if _view in self.dockManager.floatingWidgets():
                    if _view.isClosed():
                        _view.toggleView(True)
                else:
                    self.dockManager.addDockWidgetFloating(_view)
            else:
                if modifier.target == EnumLayoutModifierTarget.PROJECT_TREE_VIEW:
                    if modifier.policy == EnumLayoutModifierPolicy.APPEND:
                        self._add_widget_to_project_view_pane(_view, QtAds.EnumDockWidgetArea.CENTER)
                    elif modifier.policy == EnumLayoutModifierPolicy.REPLACE:
                        self._replace_widget_to_project_view_pane(_view, QtAds.EnumDockWidgetArea.CENTER)

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
            _app_ctx.paletteAppliedFlag = True
            self.busyIndicator.color = _app_ctx.app_theme_context.get('colors').get('primaryColor')
            pub.sendMessage('theme.themeChanged', theme=_app_ctx.app_theme, palette=self.palette())
            _setting = QtCore.QSettings()
            _setting.beginGroup('theme')
            _setting.setValue('name',_app_ctx.app_theme)
            _setting.endGroup()
            event.accept()
        super().changeEvent(event)

    @staticmethod
    def set_theme(theme_name='auto', q_app=None):
        if _app_ctx.app_theme != theme_name:
            _q_app = QtWidgets.QApplication.instance() if q_app is None else q_app
            _theme_context = apply_theme(_q_app, densityScale='-1', custom_styles=_app_ctx.app_css, theme=theme_name)
            QtGui.QPixmapCache.clear()
            _app_ctx.app_theme = theme_name
            _app_ctx.app_theme_context = _theme_context
            q_app.processEvents()
