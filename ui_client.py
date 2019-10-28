from qtpy.QtWidgets import QHBoxLayout, QMainWindow, QWidget

from chat_widget import ChatWidget
from login_widget import LoginWidget


class Ui_Client:
    def setupUi(self, mainWindow: QMainWindow):
        layout = QHBoxLayout()
        self.loginWidget = LoginWidget()
        self.chatWidget = ChatWidget()
        layout.addWidget(self.loginWidget)
        layout.addWidget(self.chatWidget)

        widget = QWidget()
        widget.setLayout(layout)
        mainWindow.setCentralWidget(widget)
