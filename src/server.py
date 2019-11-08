import sys
import json


from qtpy.QtNetwork import QTcpServer, QTcpSocket
from qtpy.QtWidgets import QApplication, QLabel


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
        return json.loads(client.readLine().data().decode('utf-8'))

    def readData(self):
        client = self.sender()
        message = self.read(client)

        if message['type'] == 'login':
            nickname = message['data']['nickname']
            self.clients[client]['nickname'] = nickname
            nicknames = [data['nickname'] for data in self.clients.values()]
            self.send(client, {
                'type': 'login_response',
                'data': {
                    'nicknames': nicknames
                }
            })
            self.sendToAll({
                'type': 'login_announce',
                'data': {
                    'nickname': nickname,
                    'text': f'{nickname} has joined the chat.'
                }
            })
        elif message['type'] == 'logoff':
            nickname = self.clients[client]['nickname']
            self.sendToAll({
                'type': 'logoff_announce',
                'data': {
                    'nickname': nickname,
                    'text': f'{nickname} has left the chat.'
                }
            })
        elif message['type'] == 'say':
            self.sendToAll({
                'type': 'say',
                'data': {
                    'nickname': self.clients[client]['nickname'],
                    'text': message['data']['text'],
                    'key': message['data']['key']
                }
            })


if __name__ == "__main__":
    app = QApplication([])

    server = Server()
    port = 8080
    server.listen(port=port)

    port_label = QLabel(f'Server listening on port {port}.')
    port_label.setMargin(30)
    port_label.show()
    port_label.setWindowTitle('Server')

    sys.exit(app.exec_())
