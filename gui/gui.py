import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QTextEdit, QVBoxLayout
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QIcon



class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui/gui.ui', self)
        self.setWindowTitle("Jump Prototyper")
        self.setWindowIcon(QIcon('gui/ui_images/appicon.ico'))
        self.setFixedSize(self.size())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet(open('gui/cssfiles/stylesheet.css').read())

    window = MyApp()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print(' Closing Window ... ')
