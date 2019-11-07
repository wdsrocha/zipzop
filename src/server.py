import sys
import json

from qtpy.QtNetwork import QTcpServer
from qtpy.QtWidgets import QApplication, QLabel

"""Schema

client
    type login
    data {
        nickname
        public_key
    }

    type logoff
    data

    type say
    data {
        [
            
        ]
        message
    }

server
    type login
    data {

        [public_key]
    }


"""


class Server(QTcpServer):
    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.clients = {}
        self.id_ = 1
        self.newConnection.connect(self.newClient)

    def newClient(self):
        client = self.nextPendingConnection()
        client.readyRead.connect(self.readData)
        client.disconnected.connect(self.disconnectClient)
        self.clients[client] = {'nickname': f'guest {self.id_}'}
        self.id_ += 1

    def disconnectClient(self):
        client = self.sender()
        nickname = self.clients[client]['nickname']
        self.sendToAll(f'say {nickname} has left the chat.')
        self.clients.pop(client)

    def readData(self):
        client = self.sender()
        print(json.loads(client.readLine().data().decode('utf-8')))
        return 0
        # print(json.loads(client.readLine().data().decode('utf-8')))
        print(client)
        try:
            data = client.readLine().data().decode('utf-8').split()
            print(data)
            request = data[0]
            if request == 'login':
                nickname = " ".join(data[1:])
                if not self.isRepeatedNickname(nickname):
                    self.clients[client]['nickname'] = nickname
                nickname = self.clients[client]['nickname']
                self.sendToAll(f'say {nickname} has joined the chat.')
            elif request == 'say':
                nickname = self.clients[client]['nickname']
                message = f'say <{nickname}>: {" ".join(data[1:])}'
                self.sendToAll(message)
        except Exception as e:
            print(e)
            print(json.loads(client.read().decode('utf-8')))

    def send(self, client, message):
        client.write(message.encode('utf-8'))

    def sendToAll(self, message):
        for client in self.clients:
            self.send(client, message)

    def isRepeatedNickname(self, nickname):
        for clientData in self.clients.values():
            if clientData['nickname'] == nickname:
                return True
        return False


if __name__ == "__main__":
    app = QApplication([])

    server = Server()
    port = 8080
    server.listen(port=port)

    port_label = QLabel(f'Server listening on port {port}.')
    port_label.setMargin(30)
    port_label.show()

    sys.exit(app.exec_())
