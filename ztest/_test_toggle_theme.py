import sys

from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QMainWindow, QWidget

import gui.qtthemeG as theme

app = QApplication(sys.argv)
theme.setup_theme("dark")

main_win = QMainWindow()

combo_box = QComboBox()
combo_box.addItems(theme.get_themes())
combo_box.currentTextChanged.connect(theme.setup_theme)

layout = QHBoxLayout()
layout.addWidget(combo_box)

central_widget = QWidget()
central_widget.setLayout(layout)
main_win.setCentralWidget(central_widget)

main_win.show()

app.exec()

# further information see: https://pyqtdarktheme.readthedocs.io/en/latest/how_to_use.html