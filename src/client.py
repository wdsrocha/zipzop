import json
import sys

import rsa
from qtpy.QtCore import Qt
from qtpy.QtNetwork import QTcpSocket
from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox

from chat_widget import ChatWidget
from fernet_algorithm import FernetAlgorithm
from login_widget import LoginWidget
from utils import rsa_to_str, str_to_rsa


class Client(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.loginWidget = LoginWidget()
        self.chatWidget = ChatWidget()
        self.setCentralWidget(self.loginWidget)

        self.fernetAlgorithm = FernetAlgorithm()

        # fk = fernet key
        # pbk = public key
        # pvk = private key
        self.fk = self.fernetAlgorithm.key
        self.pbk, self.pvk = rsa.newkeys(1024, poolsize=4)

        self.buddies = {}

        self.socket = QTcpSocket()

        self.setupConnections()

        # tests
        self.chatWidget.ui.listWidget.doubleClicked.connect(self.show_buddies)

    def show_buddies(self):
        print(f'Buddies of {self.nickname} are:')
        for nickname, fk in self.buddies.items():
            print(f'{nickname}: {fk}')
        print()

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
                    'nickname': self.nickname,
                    'public_key': self.pbk.save_pkcs1().decode('utf-8')
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
        token = self.fernetAlgorithm.encrypt(text).decode('utf-8')

        self.send({
            'type': 'say',
            'data': {
                'text': token
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

            efks = []
            for nickname, pbk in zip(data['nicknames'], data['public_keys']):
                pbk = rsa.PublicKey.load_pkcs1(pbk.encode('utf-8'))
                efks.append(rsa_to_str(rsa.encrypt(self.fk, pbk)))

            self.send({
                'type': 'b0',
                'data': {
                    'from': self.nickname,
                    'to': data['nicknames'],
                    'encrypted_fernet_keys': efks
                }
            })

        elif type_ == 'logoff_announce':
            items = self.chatWidget.ui.listWidget.findItems(
                data['nickname'], Qt.MatchExactly)
            for item in items:
                row = self.chatWidget.ui.listWidget.row(item)
                self.chatWidget.ui.listWidget.takeItem(row)
            self.chatWidget.ui.textBrowser.append(data['text'])

            self.buddies.pop(data['nickname'])

            self.fernetAlgorithm = FernetAlgorithm()
            self.fk = self.fernetAlgorithm.key

            efks = []
            for nickname, user_data in self.buddies.items():
                pbk = user_data['public_key']
                pbk = rsa.PublicKey.load_pkcs1(pbk.encode('utf-8'))
                efks.append(rsa_to_str(rsa.encrypt(self.fk, pbk)))

            self.send({
                'type': 'c0',
                'data': {
                    'from': self.nickname,
                    'encrypted_fernet_keys': efks
                }
            })

        elif type_ == 'login_announce':
            self.chatWidget.ui.listWidget.addItem(data['nickname'])
            self.chatWidget.ui.textBrowser.append(data['text'])

            nickname = data['nickname']
            pbk = data['public_key']

            self.buddies[nickname] = {}

            pbk = rsa.PublicKey.load_pkcs1(pbk.encode('utf-8'))
            efk = rsa.encrypt(self.fk, pbk)

            self.send({
                'type': 'a0',
                'data': {
                    'from': self.nickname,
                    'to': nickname,
                    'encrypted_fernet_key': rsa_to_str(efk)
                }
            })

        elif type_ == 'a1':
            nickname = data['nickname']
            efk = str_to_rsa(data['encrypted_fernet_key'])
            fk = rsa.decrypt(efk, self.pvk)
            self.buddies[nickname] = {}
            self.buddies[nickname]['fernet_key'] = fk

        elif type_ == 'say':
            nickname = data['nickname']
            text = data['text'].encode('utf-8')

            fk = self.buddies[nickname]['fernet_key']
            print(text)
            print(type(text))
            text = self.fernetAlgorithm.decrypt(text, fk).decode('utf-8')
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
