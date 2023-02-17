# -*- coding: utf-8 -*-
import os.path

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       :
# Sourcefile(s) : dlg_create_project.py
# ------------------------------------------------------------------------------
#
# File          : dlg_create_project.py
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
from application.define_path import PROJECT_PATH
from gui import QtWidgets, QtCore
from gui.core.class_base import ThemeStyledUiObject, I18nUiObject
from gui.components.widget_file_browser import FileBrowserWidget
from core.gui.components.widget_header import HeaderWidget


class CreateProjectDialog(QtWidgets.QDialog, ThemeStyledUiObject, I18nUiObject):
    def __init__(self, parent):
        super().__init__(parent)
        ThemeStyledUiObject.__init__(self)
        I18nUiObject.__init__(self)
        _title=self.i18nUsageRegistry.get_i18n('dlg', 'create_project_title')
        self.setWindowTitle(_title)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.formLayout = QtWidgets.QGridLayout(self)
        self.headerWidget = HeaderWidget(self)
        self.headerWidget.set_content(_title,
                                      description=self.i18nUsageRegistry.get_i18n('dlg', 'create_project_description'))
        self.projectNameLabel = QtWidgets.QLabel(self)
        self.projectPathLabel = QtWidgets.QLabel(self)
        self.projectNameEdit = QtWidgets.QLineEdit(self)
        self.projectPathEdit = FileBrowserWidget(self, str(PROJECT_PATH))
        self.projectPathEdit.set_left_label_visible(False)
        self.i18nUsageRegistry.register(self.projectNameLabel, 'app', 'project_name', func_to_set='setText', do_update=True)
        self.i18nUsageRegistry.register(self.projectPathLabel, 'app', 'project_path', func_to_set='setText', do_update=True)
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        # bind event
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.projectPathEdit.filePathBrowserBtn.clicked.connect(self.on_file_browser_required)
        # layout
        self.formLayout.addWidget(self.projectNameLabel, 0, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.formLayout.addWidget(self.projectNameEdit, 1, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.formLayout.addWidget(self.projectPathLabel, 2, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.formLayout.addWidget(self.projectPathEdit, 3, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.formLayout.setRowStretch(0 | 1 | 2 | 3, 1)
        self.mainLayout.addWidget(self.headerWidget)
        self.mainLayout.addSpacing(25)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addSpacing(25)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)

    def get_project_info(self):
        return {'name': self.projectNameEdit.text(), 'path': self.projectPathEdit.filePathEdit.text()}

    def on_file_browser_required(self, evt):
        _res = QtWidgets.QFileDialog.getExistingDirectory(self, self.projectPathLabel.text().capitalize(),
                                                          str(PROJECT_PATH),
                                                          options=QtWidgets.QFileDialog.Option.ShowDirsOnly)
        self.projectPathEdit.filePathEdit.setText(_res)

    def on_theme_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        pass

    def on_locale_changed(self, topic: pub.Topic = pub.AUTO_TOPIC, **msg_data):
        self.i18nUsageRegistry.update_i18n_text(self.projectNameLabel)
        self.i18nUsageRegistry.update_i18n_text(self.projectPathLabel)
        self.headerWidget.set_content(self.i18nUsageRegistry.get_i18n('dlg', 'create_project_title'),
                                      description=self.i18nUsageRegistry.get_i18n('dlg', 'create_project_description'))

    def accept(self) -> None:
        _msg = QtWidgets.QMessageBox(self)
        _msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        _msg.setWindowTitle(self.i18nUsageRegistry.get_i18n('app', 'error'))
        if self.projectNameEdit.text().strip() == '' or self.projectPathEdit.filePathEdit.text().strip() == '':
            _msg.setText(self.i18nUsageRegistry.get_i18n('err', 'empty_f').format('%s/%s' % (self.projectNameLabel.text(), self.projectPathLabel.text())))
            _msg.exec_()
            self.projectNameEdit.setFocus()
            return
        if os.path.exists(os.path.join(self.projectPathEdit.filePathEdit.text(),self.projectNameEdit.text())):
            _msg.setText(self.i18nUsageRegistry.get_i18n('err', 'exist_f').format('%s ' % self.projectNameEdit.text()))
            _msg.exec_()
            self.projectNameEdit.setFocus()
            return
        _msg.deleteLater()
        super().accept()
