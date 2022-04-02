import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QTextEdit, QVBoxLayout
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QIcon



class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)
        self.setWindowTitle("Jump Prototyper")
        self.setWindowIcon(QIcon('appicon.ico'))
        self.setFixedSize(self.size())


        # initial values
        self.dirName = ""
        self.jumplist = [
            self.jumpBtn_1,
            self.jumpBtn_2,
            self.jumpBtn_3,
            self.jumpBtn_4,
            self.jumpBtn_5,
            self.jumpBtn_6,
            self.jumpBtn_7,
            self.jumpBtn_8,
            self.jumpBtn_9,
        ]
        self.strafelist = [
            self.strafeBtn_1,
            self.strafeBtn_2,
            self.strafeBtn_3,
            self.strafeBtn_4,
            self.strafeBtn_5,
            self.strafeBtn_6,
            self.strafeBtn_7,
            self.strafeBtn_8,
            self.strafeBtn_9,
        ]
        self.addList = [
            self.addBtn_1,
            self.addBtn_2,
            self.addBtn_3,
            self.addBtn_4,
            self.addBtn_5,
            self.addBtn_6,
            self.addBtn_7,
            self.addBtn_8,
            self.addBtn_9,
        ]
        self.index = 0

        self.addListSettings = [
            {"btnText": "wallshot", "text": "ws"},
            {"btnText": "skip", "text": "sk"},
            {"btnText": "speedshot", "text": "ss"},
            {"btnText": "double", "text": "d"},
            {"btnText": "catch", "text": "sk2"},
            {"btnText": "telesync", "text": "ts"},
        ]
        func_list = []
        for addIndex in range(len(self.addList)):
            btn = self.addList[addIndex]
            if addIndex in range(len(self.addListSettings)):
                btnText = self.addListSettings[addIndex]["btnText"]
                btn.setText( btnText )
                text = self.addListSettings[addIndex]["text"]
                # func_list.append(lambda t=text: print(t))
                btn.clicked.connect(lambda t=text: print(t) )
            else:
                btn.hide()

        for func in func_list:
            func()

    def addJumpOrStrafe( self, text ):
        try:
            if self.index % 2 == 0:
                print(text)
                self.jumplist[int(self.index/2)].setText(text)

            else:
                self.strafelist[int( (self.index-1) /2)].setText(text)
            self.index = self.index + 1
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet(open('stylesheet.css').read())

    window = MyApp()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print(' Closing Window ... ')
