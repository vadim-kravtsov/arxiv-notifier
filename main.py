import sys
from PyQt5.QtWidgets import QApplication
from lib.gui import MainApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainApplication()
    sys.exit(app.exec_())
