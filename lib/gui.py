from PyQt5 import QtWidgets


class MainApplication(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("arXiv-notifier")
        self.setGeometry(200, 200, 700, 700)
        self.setMinimumSize(500, 500)
        self.show()
