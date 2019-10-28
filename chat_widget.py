import sys

from qtpy.QtWidgets import QApplication, QWidget

from ui_chat_widget import Ui_ChatWidget


class ChatWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(ChatWidget, self).__init__(*args, **kwargs)
        self.ui = Ui_ChatWidget()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication([])

    chat = ChatWidget()
    chat.show()

    sys.exit(app.exec_())
