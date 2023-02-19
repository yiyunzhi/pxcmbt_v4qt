import os, sys
from core.gui.qtimp import QtGui, QtWidgets, QtCore
from core.application.zI18n import zI18n
from core.application.class_application_context import APP_CONTEXT
from core.application.define_path import CORE_I18N_PATH
from core.gui.qttheme import apply_theme
from core.gui.patch.low_level_sys_ui import llSetDarkWinTitlebar
from core.gui.splash import ZSplashScreen
from core.gui.utils.mb_exception_hook import UncaughtHook
from core.gui.main_win import MainWindow

if __name__ == '__main__':
    _root_path = os.path.dirname(__file__)
    app = QtWidgets.QApplication(sys.argv)
    _splash = ZSplashScreen(5)
    _splash.show()
    _splash.set_message('setup application...', 1)
    QtCore.QCoreApplication.setOrganizationName("PxCEMBT")
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
    with open(os.path.join(_root_path, 'mbt_style.css'), 'r', encoding='utf-8') as f:
        APP_CONTEXT.app_css = f.read()

    _splash.set_message('mainWindow setup...', 4)
    _win = MainWindow()
    _win.set_theme('auto', app)
    _win.resize(1280, 720)
    APP_CONTEXT.mainWin = _win
    # app.processEvents()

    # _splash.set_message('do 1', 2)
    # _splash.set_message('do 2', 3)

    # _splash.set_message('finish', 5)
    _splash.finish(_win)
    _win.show()
    # QtCore.QTimer.singleShot(500, lambda: _win.set_theme('auto', app))
    llSetDarkWinTitlebar(_win.winId())
    sys.exit(app.exec())
