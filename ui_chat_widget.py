from qtpy.QtWidgets import (QHBoxLayout, QLineEdit, QListView, QPushButton,
                            QSizePolicy, QSplitter, QTextBrowser, QVBoxLayout,
                            QWidget)


class Ui_ChatWidget:
    def setupUi(self, widget: QWidget):
        self.textBrowser = QTextBrowser()
        self.listView = QListView()
        self.splitter = QSplitter()
        self.splitter.addWidget(self.textBrowser)
        self.splitter.addWidget(self.listView)
        self.splitter.setCollapsible(0, 0)
        w = self.splitter.width()
        self.splitter.setSizes([.75 * w, .25 * w])

        self.lineEdit = QLineEdit()
        self.lineEdit.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.pushButton = QPushButton()
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.lineEdit)
        bottomLayout.addWidget(self.pushButton)

        layout = QVBoxLayout(widget)
        layout.addWidget(self.splitter)
        layout.addLayout(bottomLayout)
