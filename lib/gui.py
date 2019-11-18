from PyQt5 import QtWidgets, QtCore, QtGui
from .librarian import LocalLibrary, Paper
import time
import threading
import arxiv


class MainApplication(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()
        self.init_library()
        self.periodical_query()


    def initUI(self):
        self.setWindowTitle("arXiv-notifier")
        self.setGeometry(200, 200, 1000, 600)
        self.setMinimumSize(700, 500)

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
            tabIndex = self.tab_names.index(tab_name)
            self.tabs_widget.addTab(QtWidgets.QTableView(), tab_name)
            self.tabs_widget.widget(tabIndex).setModel(QtGui.QStandardItemModel())
            self.tabs_widget.widget(tabIndex).setSelectionMode(3)
            self.tabs_widget.widget(tabIndex).setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.tabs_widget.widget(tabIndex).setGridStyle(0)
            self.tabs_widget.widget(tabIndex).verticalHeader().hide()
            self.tabs_widget.widget(tabIndex).setSortingEnabled(True)
            self.tabs_widget.widget(tabIndex).setSelectionBehavior(1)
            self.tabs_widget.widget(tabIndex).setFocusPolicy(QtCore.Qt.StrongFocus)
        
            #self.tabs_widget.widget(self.tab_names.index(tab_name)).model().setColumnCount(2)
            
        self.setCentralWidget(self.tabs_widget)
        self.show()

    def init_library(self):
        self.local_library = LocalLibrary()
        statusList = ['new', 'readed', 'deleted']
        self.qt_titlelist = [QtGui.QStandardItem(x.title) for x in self.local_library.papers]
        self.qt_timelist = [QtGui.QStandardItem(time.strftime('%H:%M  %b %d', x.published)) for x in self.local_library.papers]
        self.qt_authorlist = [QtGui.QStandardItem(f'{x.authors[0]} et al.' if len(x.authors) > 1
                                                  else x.authors[0]) for x in self.local_library.papers]
        tabIndex = 0
        #for paper in self.local_library.papers:
        #    tabIndex = statusList.index(paper.status)
        self.tabs_widget.widget(tabIndex).model().insertColumn(0, self.qt_titlelist)
        self.tabs_widget.widget(tabIndex).model().insertColumn(1, self.qt_authorlist)
        self.tabs_widget.widget(tabIndex).model().insertColumn(2, self.qt_timelist)
        self.tabs_widget.widget(tabIndex).model().setHorizontalHeaderLabels(['Title', 'Authors', 'Published'])
        self.tabs_widget.widget(tabIndex).setColumnWidth(0, 700)
        self.tabs_widget.widget(tabIndex).setColumnWidth(1, 180)
        #self.tabs_widget.widget(tabIndex).horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tabs_widget.widget(tabIndex).horizontalHeader().setStretchLastSection(True)
        #self.tabs_widget.widget(tabIndex).horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        #self.tabs_widget.widget(tabIndex).horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        #self.tabs_widget.widget(tabIndex).setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        #self.tabs_widget.widget(tabIndex).resizeColumnsToContents()
        #self.tabs_widget.widget(tabIndex).setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
    def periodical_query(self, periodicity=300):
        self.arxiv_query()
        self.timer = threading.Timer(periodicity, self.periodical_query)
        self.timer.start()

    def arxiv_query(self):
        resutls = arxiv.query('astro-ph.HE', max_results=10, sort_by='submittedDate')
        resutls=[]
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
