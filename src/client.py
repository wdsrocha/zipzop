import json
import sys

from qtpy.QtCore import Qt
from qtpy.QtNetwork import QTcpSocket
from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox

from chat_widget import ChatWidget
from fernet_algorithm import FernetAlgorithm
from login_widget import LoginWidget
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
            self.chatWidget.ui.lineEdit.setFocus()
            self.chatWidget.setMinimumWidth(500)
            self.chatWidget.setMinimumHeight(300)
            self.setWindowTitle(f'Client - {self.nickname}')

    def sendUserMessage(self):
        text = self.chatWidget.ui.lineEdit.text()
        text = f'<{self.nickname}>: {text}'
        token = str(self.fernetAlgorithm.encrypt(text))
        key = str(self.fernetAlgorithm.key)

        self.send({
            'type': 'say',
            'data': {
                'text': token,
                'key': key
            }
        })
        self.chatWidget.ui.lineEdit.clear()
        self.chatWidget.ui.lineEdit.setFocus()

    def readData(self):
        string = self.sender().readLine().data().decode('utf-8')
        stack = 0
        messages = []
        left = 0
        for right, c in enumerate(string):
            if c == '{':
                stack += 1
            elif c == '}':
                stack -= 1
            if stack == 0:
                messages.append(string[left:right + 1])
                left = right + 1

        for message in messages:
            self.handleData(json.loads(message))

    def handleData(self, message):
        type_ = message['type']
        data = message['data']

        if type_ == 'login_response':
            for nickname in data['nicknames']:
                if nickname != self.nickname:
                    self.chatWidget.ui.listWidget.addItem(nickname)
        elif message['type'] == 'logoff_announce':
            items = self.chatWidget.ui.listWidget.findItems(
                data['nickname'], Qt.MatchExactly)
            for item in items:
                row = self.chatWidget.ui.listWidget.row(item)
                self.chatWidget.ui.listWidget.takeItem(row)
            self.chatWidget.ui.textBrowser.append(data['text'])
        elif message['type'] == 'login_announce':
            self.chatWidget.ui.listWidget.addItem(data['nickname'])
            self.chatWidget.ui.textBrowser.append(data['text'])
        elif message['type'] == 'say':
            text = message['data']['text']
            key = message['data']['key']

            text = str.encode(text[2:len(text)-1])
            key = str.encode(key[2:len(key)-1])

            text = self.fernetAlgorithm.decrypt(text, key).decode('utf-8')
            self.chatWidget.ui.textBrowser.append(text)

    def displayConnectionError(self):
        QMessageBox.information(self, '', 'No connection to host')
        self.close()

    def closeEvent(self, event):
        self.send({
            'type': 'logoff',
            'data': {
                'nickname': self.nickname
            }
        })
        self.socket.disconnectFromHost()


if __name__ == "__main__":
    app = QApplication([])

    client = Client()
    client.setWindowTitle('Client')
    client.show()

    sys.exit(app.exec_())
