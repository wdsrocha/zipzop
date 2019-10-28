from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QFormLayout, QLineEdit, QPushButton, QSizePolicy,
                            QVBoxLayout, QWidget)


class Ui_LoginWidget:
    def setupUi(self, widget: QWidget):
        self.addressLineEdit = QLineEdit('localhost')
        self.portLineEdit = QLineEdit('8080')
        self.nicknameLineEdit = QLineEdit()

        formLayout = QFormLayout()
        formLayout.addRow('&Nickname', self.nicknameLineEdit)
        formLayout.addRow('Host &address', self.addressLineEdit)
        formLayout.addRow('Host &port', self.portLineEdit)

        self.pushButton = QPushButton('&Chat!')
        self.pushButton.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pushButton.setDefault(True)

        layout = QVBoxLayout(widget)
        layout.addLayout(formLayout)
        layout.addWidget(
            self.pushButton, 1, Qt.AlignTop | Qt.AlignRight)
