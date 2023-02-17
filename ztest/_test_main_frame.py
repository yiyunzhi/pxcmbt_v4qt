# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_main_frame.py
# ------------------------------------------------------------------------------
#
# File          : _test_main_frame.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import i18n, os
from pubsub import pub
from gui import QtCore, QtWidgets
from gui.qttheme import apply_theme
from application.define_path import I18N_PATH

i18n.load_path.append(I18N_PATH)

i18n.set('fallback', 'en')
i18n.set('enable_memoization', True)
SUPPORTED_LANG_BCP47 = ['en', 'de']
_lang_code = QtCore.QLocale().system().bcp47Name()
i18n.set('locale', _lang_code)
QtCore.QCoreApplication.setOrganizationName("PxCEMBT")
QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
app = QtWidgets.QApplication()
_css=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'mbt_style.css')
with open(_css, 'r', encoding='utf-8') as f:
    _app_css = f.read()
apply_theme(app, densityScale='-1', custom_styles=_app_css, update_palette=True, theme='dark')


class TestFrame(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1024, 720)
        self.changeLang(self.locale().language())
        self.wdg = QtWidgets.QWidget(self)
        self.testTb=QtWidgets.QToolBar(self)
        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self.testTb)
        self.testTb.setAllowedAreas(QtCore.Qt.ToolBarArea.LeftToolBarArea)
        self.testTb.setMovable(False)
        _action_change_theme_default=self.testTb.addAction('TemDefault')
        _action_change_theme_default.triggered.connect(lambda x:self.changeTheme('default'))
        _action_change_theme_dark=self.testTb.addAction('TemDark')
        _action_change_theme_dark.triggered.connect(lambda x:self.changeTheme('dark'))
        _action_change_lang_de=self.testTb.addAction('LangDE')
        _action_change_lang_de.triggered.connect(lambda x:self.changeLang('de'))
        _action_change_lang_en=self.testTb.addAction('LangEN')
        _action_change_lang_en.triggered.connect(lambda x: self.changeLang('en'))

        self.mainLayout = QtWidgets.QHBoxLayout(self.wdg)
        self.wdg.setLayout(self.mainLayout)
        self.setCentralWidget(self.wdg)

    def changeLang(self, lang):
        _qApp = QtWidgets.QApplication.instance()
        _q_local = QtCore.QLocale(lang)
        self.setLocale(_q_local)
        i18n.set('locale', _q_local.bcp47Name())
        # _qApp.postEvent(self, QtCore.QEvent(QtCore.QEvent.Type.LanguageChange))
        pub.sendMessage('locale.localeChange', locale=_q_local)

    def changeTheme(self, theme):
        _app = QtWidgets.QApplication.instance()
        apply_theme(app, densityScale='-1', custom_styles=_app_css, update_palette=True, theme=theme)
        pub.sendMessage('theme.themeChanged', theme=theme)
