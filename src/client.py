import sys

from qtpy.QtNetwork import QTcpSocket
from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox

import json

from chat_widget import ChatWidget
from login_widget import LoginWidget

from fernet_algorithm import FernetAlgorithm
from rsa_algorithm import RsaAlgorithm


class Client(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.loginWidget = LoginWidget()
        self.chatWidget = ChatWidget()
        self.setCentralWidget(self.loginWidget)

        self.fernetAlgorithm = FernetAlgorithm()

        self.socket = QTcpSocket()

        self.setupConnections()

    def send(self, message: dict):
        self.socket.write(json.dumps(message).encode('utf-8'))

    def read(self, socket) -> dict:
        return json.loads(socket.readLine().data().decode('utf-8'))

    def setupConnections(self):
        self.loginWidget.ui.pushButton.clicked.connect(self.connectToHost)
        self.socket.readyRead.connect(self.readData)
        self.socket.error.connect(self.displayConnectionError)
        self.chatWidget.ui.pushButton.clicked.connect(self.sendUserMessage)

    def connectToHost(self):
        hostAddress = self.loginWidget.ui.addressLineEdit.text()
        port = int(self.loginWidget.ui.portLineEdit.text())
        self.socket.connectToHost(hostAddress, port)
        if self.socket.waitForConnected(1000):
            self.nickname = self.loginWidget.ui.nicknameLineEdit.text()
            self.send({
                'type': 'login',
                'data': {
                    'nickname': self.nickname
                }
            })

            # ui
            self.loginWidget.setParent(None)
            self.setCentralWidget(self.chatWidget)
            self.chatWidget.setMinimumWidth(500)
            self.chatWidget.setMinimumHeight(300)

    def sendUserMessage(self):
        text = self.chatWidget.ui.lineEdit.text()
        text = f'<{self.nickname}>: {text}'



        self.send({
            'type': 'say',
            'data': {
                'text': text
            }
        })
        self.chatWidget.ui.lineEdit.clear()
        self.chatWidget.ui.lineEdit.setFocus()

    def readData(self):
        message = self.read(self.sender())

        if message['type'] == 'logoff_response':
            pass
        elif message['type'] == 'login_announce':
            text = message['data']['text']
            self.chatWidget.ui.textBrowser.append(text)
        elif message['type'] == 'say':
            text = message['data']['text']
            self.chatWidget.ui.textBrowser.append(text)

    def displayConnectionError(self):
        QMessageBox.information(self, '', 'Could not connect to host')

    def closeEvent(self, event):
        self.socket.disconnectFromHost()


if __name__ == "__main__":
    app = QApplication([])

    client = Client()
    client.show()

    sys.exit(app.exec_())
