from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QFormLayout, QLineEdit, QPushButton, QSizePolicy,
                            QVBoxLayout, QWidget)


class Ui_LoginWidget:
    def setupUi(self, widget: QWidget):
        self.ipLineEdit = QLineEdit('localhost')
        self.portLineEdit = QLineEdit('8080')
        self.nicknameLineEdit = QLineEdit()

        formLayout = QFormLayout()
        formLayout.addRow('&Nickname', self.nicknameLineEdit)
        formLayout.addRow('Server &IP', self.ipLineEdit)
        formLayout.addRow('Server &port', self.portLineEdit)

        self.connectPushButton = QPushButton('&Connect')
        self.connectPushButton.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.connectPushButton.setDefault(True)

        layout = QVBoxLayout(widget)
        layout.addLayout(formLayout)
        layout.addWidget(
            self.connectPushButton, 1, Qt.AlignTop | Qt.AlignRight)
