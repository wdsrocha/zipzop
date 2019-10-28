from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox
import sys
from ui_client import Ui_Client
from qtpy.QtNetwork import QTcpSocket


from login_widget import LoginWidget
from chat_widget import ChatWidget

class Client(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.loginWidget = LoginWidget()
        self.chatWidget = ChatWidget()
        self.setCentralWidget(self.loginWidget)

        self.socket = QTcpSocket()

        self.setupConnections()

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
            self.send(f'login {self.nickname}')
            self.loginWidget.setParent(None)
            self.setCentralWidget(self.chatWidget)

    def send(self, message):
        self.socket.write(message.encode('utf-8'))

    def sendUserMessage(self):
        userMessage = self.chatWidget.ui.lineEdit.text()
        message = f'say {userMessage}'
        self.send(message)
        self.chatWidget.ui.lineEdit.clear()
        self.chatWidget.ui.lineEdit.setFocus()

    def readData(self):
        server = self.sender()
        data = server.readLine().data().decode('utf-8').split()
        response = data[0]
        if response == 'say':
            self.chatWidget.ui.textBrowser.append(' '.join(data[1:]))

    def displayConnectionError(self):
        QMessageBox.information(self, '', 'Could not connect to host')

    def closeEvent(self, event):
        self.socket.disconnectFromHost()


if __name__ == "__main__":
    app = QApplication([])

    client = Client()
    client.show()

    sys.exit(app.exec_())
