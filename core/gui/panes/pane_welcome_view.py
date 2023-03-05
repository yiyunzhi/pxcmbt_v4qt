# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pane_welcome.py
# ------------------------------------------------------------------------------
#
# File          : pane_welcome.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from pubsub import pub
from core.application.core.base import singleton
from core.application.class_application_context import ApplicationContext
from core.application.define import EnumAppMsg
from core.gui.qtimp import QtWidgets, QtCore
import core.gui.qtads as QtAds
from core.gui.core.class_base import ZView
from core.gui.components.widget_recent_file_list import RecentFileListWidget


class _WelcomePane(QtWidgets.QWidget, ZView):
    TITLE_LABEL_STYLE = """
        QLabel {
            text-transform: uppercase;
            font-size: 16px;
            font-weight: bolder;
            border-bottom: 1px solid palette(windowtext);
            border-radius:0px;
        }
    """
    DESCRIPTION_LABEL_STYLE = """
            QLabel {
                font-size: 12px;
                color: #777;
            }
        """

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        ZView.__init__(self)
        self._appCtx = ApplicationContext()
        _btn_icon_option = {'color': self.palette().highlight().color()}
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.labelStart = QtWidgets.QLabel('Start', self)
        self.labelRecent = QtWidgets.QLabel('Recent', self)
        self.labelHelp = QtWidgets.QLabel('Help', self)
        self.labelStart.setFixedWidth(64)
        self.labelRecent.setFixedWidth(64)
        self.labelHelp.setFixedWidth(64)

        self.labelNewProj = QtWidgets.QLabel('create a project use the default project setting.', self)
        self.labelNewProj.setWordWrap(True)

        self.btnIconSize = QtCore.QSize(22, 22)
        self.btnNewProj = QtWidgets.QPushButton(self)  # icon,text,parent
        self.btnNewProj.setIconSize(self.btnIconSize)
        self.btnNewProj.setFlat(True)
        _icon = self._appCtx.iconResp.get_icon(self.btnNewProj, icon_ns='fa', icon_name='mdi6.plus', setter='setIcon', options=_btn_icon_option)
        self.btnNewProj.setIcon(_icon)
        self.btnNewProj.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.labelOpenProj = QtWidgets.QLabel('open a project. a dialog will be showed up then a project\ncould be selected and loaded up.', self)
        self.labelOpenProj.setWordWrap(True)
        self.btnOpenProj = QtWidgets.QPushButton(self)  # icon,text,parent
        self.btnOpenProj.setIconSize(self.btnIconSize)
        self.btnOpenProj.setFlat(True)
        _icon = self._appCtx.iconResp.get_icon(self.btnOpenProj, icon_ns='fa', icon_name='mdi6.folder-open-outline', setter='setIcon', options=_btn_icon_option)
        self.btnOpenProj.setIcon(_icon)
        self.btnOpenProj.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        self.recentFilesList = RecentFileListWidget(self)
        self._init_recent_file_list()

        self.btnOpenHelp = QtWidgets.QPushButton(self)  # icon,text,parent
        self.btnOpenHelp.setIconSize(self.btnIconSize)
        self.btnOpenHelp.setFlat(True)
        _icon = self._appCtx.iconResp.get_icon(self.btnOpenHelp, icon_ns='fa', icon_name='mdi6.help-box', setter='setIcon', options=_btn_icon_option)
        self.btnOpenHelp.setIcon(_icon)
        self.btnOpenHelp.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.labelStart.setStyleSheet(self.TITLE_LABEL_STYLE)
        self.labelRecent.setStyleSheet(self.TITLE_LABEL_STYLE)
        self.labelHelp.setStyleSheet(self.TITLE_LABEL_STYLE)
        self.labelNewProj.setStyleSheet(self.DESCRIPTION_LABEL_STYLE)
        self.labelOpenProj.setStyleSheet(self.DESCRIPTION_LABEL_STYLE)
        # bind event
        # todo: subsribe the project open, delete event, read from setting then update recentFilesList
        self.recentFilesList.sigItemClicked.connect(self.on_open_recent_file_requested)
        self.btnNewProj.clicked.connect(self.on_new_project_required)
        self.btnOpenProj.clicked.connect(self.on_open_project_required)
        self.btnOpenHelp.clicked.connect(self.on_open_help_required)
        pub.subscribe(self.on_project_state_changed, EnumAppMsg.sigProjectStateChanged)
        # layout
        self.mainLayout.setContentsMargins(25, 15, 5, 5)
        self.mainLayout.addWidget(self.labelStart, 0, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.btnNewProj, 1, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.labelNewProj, 1, 1, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.btnOpenProj, 2, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.labelOpenProj, 2, 1, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.labelRecent, 3, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.recentFilesList, 4, 0, 2, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.labelHelp, 6, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.btnOpenHelp, 7, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setRowStretch(0 | 1 | 2 | 3 | 4 | 5 | 6 | 7, 1)
        self.mainLayout.setColumnStretch(0 | 1, 1)
        self.setLayout(self.mainLayout)

    def _init_recent_file_list(self):
        _rl = list()
        _setting = QtCore.QSettings()
        _setting.beginGroup('recentFiles')
        _size = _setting.beginReadArray('files')
        for i in range(_size):
            _setting.setArrayIndex(i)
            _rl.append((_setting.value('name'), _setting.value('date'), _setting.value('path')))
        _setting.endArray()
        _setting.endGroup()
        self.recentFilesList.set_content(_rl)

    def on_project_state_changed(self, topic=pub.AUTO_TOPIC, **msg_data):
        self._init_recent_file_list()

    def on_open_recent_file_requested(self, path):
        pub.sendMessage('project.open', path=path)

    def on_new_project_required(self, evt):
        pub.sendMessage('project.new')

    def on_open_project_required(self, evt):
        pub.sendMessage('project.open')

    def on_open_help_required(self, evt):
        pub.sendMessage('help.open')


@singleton
class WelcomeDockPane(QtAds.CDockWidget, ZView):
    def __init__(self, parent):
        QtAds.CDockWidget.__init__(self, '', parent)
        ZView.__init__(self)
        self.zViewTitle = 'welcome'
        self.setFeature(QtAds.EnumDockWidgetFeature.DELETE_CONTENT_ON_CLOSE, False)
        _widget = _WelcomePane(self)
        self.setWidget(_widget)

    @ZView.title.setter
    def title(self, title):
        self.zViewTitle = title
        self.setWindowTitle(title)
