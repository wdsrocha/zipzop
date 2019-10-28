from qtpy.QtWidgets import QApplication, QWidget
import sys
from ui_login_widget import Ui_LoginWidget


class LoginWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(LoginWidget, self).__init__(*args, **kwargs)
        self.ui = Ui_LoginWidget()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication([])

    login = LoginWidget()
    login.show()

    sys.exit(app.exec_())
