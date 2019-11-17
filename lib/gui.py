from PyQt5 import QtWidgets, QtCore, QtGui
from .librarian import LocalLibrary, Paper
import threading
import arxiv


class MainApplication(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.local_library = LocalLibrary()
        self.periodical_query()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("arXiv-notifier")
        self.setGeometry(200, 200, 700, 700)
        self.setMinimumSize(500, 500)

        # Create containers
        self.main_vbox = QtWidgets.QVBoxLayout()
        self.tabs_hbox = QtWidgets.QHBoxLayout()
        self.sort_hbox = QtWidgets.QHBoxLayout()
        self.list_vbox = QtWidgets.QVBoxLayout()

        # Create tabs widget
        self.tabs_widget = QtWidgets.QTabWidget()
        self.tabs_widget.setUsesScrollButtons(False)
        self.tab_names = ['New', 'Readed', 'Deleted']

        for tab_name in self.tab_names:
            self.tabs_widget.addTab(QtWidgets.QListView(), tab_name)
            self.tabs_widget.widget(self.tab_names.index(tab_name)).setModel(QtGui.QStandardItemModel())
            self.tabs_widget.widget(self.tab_names.index(tab_name)).setSelectionMode(3)
            self.tabs_widget.widget(self.tab_names.index(tab_name)).setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setCentralWidget(self.tabs_widget)
        self.show()

    def periodical_query(self, periodicity=3):
        self.arxiv_query()
        self.timer = threading.Timer(periodicity, self.periodical_query)
        self.timer.start()

    def arxiv_query(self):
        resutls = arxiv.query('astro-ph.HE', max_results=10, sort_by='submittedDate')
        for paper_form in resutls:
            new_papers = 0
            if paper_form['id'] not in self.local_library.data['ids']:
                self.local_library.add_paper(Paper(paper_form))
                new_papers += 1
        self.local_library.save()
        self.local_library.print()

    def closeEvent(self, event):
        event.accept()
        self.timer.cancel()
