import os, sys
from core.gui.qtimp import QtGui, QtWidgets, QtCore
from core.application.zI18n import zI18n
from core.application.class_application_context import ApplicationContext
from core.application.define_path import CORE_I18N_PATH
from core.application.define import APP_NAME, APP_VERSION
from core.gui.qttheme import apply_theme
from core.gui.patch.low_level_sys_ui import llSetDarkWinTitlebar
from core.gui.splash import ZSplashScreen
from core.gui.utils.mb_exception_hook import UncaughtHook
from core.gui.main_win import MainWindow
from core.gui.core.class_i18n_repository import I18nRepository
from core.gui.core.class_icon_repository import IconRepository
from core.gui import GUI_VIEW_FACTORY

if __name__ == '__main__':
    _root_path = os.path.dirname(__file__)
    app = QtWidgets.QApplication(sys.argv)
    _splash = ZSplashScreen(5)
    _splash.show()
    _splash.set_message('setup application...', 1)
    QtCore.QCoreApplication.setOrganizationName("PxC")
    QtCore.QCoreApplication.setOrganizationDomain("phoenixcontact.com")
    QtCore.QCoreApplication.setApplicationName(APP_NAME)
    QtCore.QCoreApplication.setApplicationVersion(APP_VERSION)
    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.Format.IniFormat)
    print('--->QSettingsFileName:', QtCore.QSettings().fileName())
    # create a global instance of our class to register the hook
    _qt_exception_hook = UncaughtHook()
    app.setProperty('uncaughtHook', _qt_exception_hook)

    _splash.set_message('localization apply...', 2)
    zI18n.load_path.append(CORE_I18N_PATH)
    zI18n.set('fallback', 'en')
    zI18n.set('enable_memoization', True)
    SUPPORTED_LANG_BCP47 = ['en', 'de']
    _lang_code = QtCore.QLocale().system().bcp47Name()
    zI18n.set('locale', _lang_code)
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    # sys.argv += ['-platform', 'windows:darkmode=2']

    _splash.set_message('style apply...', 3)
    _app_ctx: ApplicationContext = ApplicationContext()
    _app_ctx.zViewFactory = GUI_VIEW_FACTORY
    with open(os.path.join(_root_path, 'mbt_style.css'), 'r', encoding='utf-8') as f:
        _app_ctx.app_css = f.read()

    _splash.set_message('mainWindow setup...', 4)
    _app_ctx.iconResp = IconRepository(app)
    _app_ctx.i18nResp = I18nRepository()
    _win = MainWindow()
    _win.set_theme('auto', app)
    _win.resize(1280, 720)
    _app_ctx.mainWin = _win
    _app_ctx.app = app

    for k, v in _app_ctx.mbt_solution_manager.solutions.items():
        v.run_setup(_app_ctx)
    # app.processEvents()

    # _splash.set_message('do 1', 2)
    # _splash.set_message('do 2', 3)

    # _splash.set_message('finish', 5)
    _splash.finish(_win)
    _win.show()
    # QtCore.QTimer.singleShot(500, lambda: _win.set_theme('auto', app))
    llSetDarkWinTitlebar(_win.winId())
    sys.exit(app.exec())
