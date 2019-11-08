from qtpy.QtWidgets import (QHBoxLayout, QLineEdit, QListWidget, QPushButton,
                            QSizePolicy, QSplitter, QStyle, QTextBrowser,
                            QVBoxLayout, QWidget)


class Ui_ChatWidget:
    def setupUi(self, widget: QWidget):
        self.textBrowser = QTextBrowser()
        self.listWidget = QListWidget()
        self.splitter = QSplitter()
        self.splitter.addWidget(self.textBrowser)
        self.splitter.addWidget(self.listWidget)
        self.splitter.setCollapsible(0, 0)
        w = self.splitter.width()
        self.splitter.setSizes([.75 * w, .25 * w])

        self.lineEdit = QLineEdit()
        self.lineEdit.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.pushButton = QPushButton()
        self.pushButton.setIcon(
            widget.style().standardIcon(QStyle.SP_ArrowRight))

        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.lineEdit)
        bottomLayout.addWidget(self.pushButton)

        layout = QVBoxLayout(widget)
        layout.addWidget(self.splitter)
        layout.addLayout(bottomLayout)
