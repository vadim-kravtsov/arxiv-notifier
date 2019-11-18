from PyQt5 import QtWidgets, QtCore, QtGui
#from .librarian import LocalLibrary, Paper
import time
import pickle
import threading
import arxiv
from os import getcwd


class MainApplication(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.local_library = LocalLibrary(getcwd()+'/lib/library')
        self.initUI()
        self.init_library()
        self.periodical_query()

    def initUI(self):
        self.setWindowTitle("arXiv-notifier")
        self.setGeometry(200, 200, 1000, 600)
        self.setMinimumSize(700, 500)

        # Create containers
        self.footer = QtWidgets.QVBoxLayout()
        # self.tabs_hbox = QtWidgets.QHBoxLayout()
        # self.sort_hbox = QtWidgets.QHBoxLayout()
        # self.list_vbox = QtWidgets.QVBoxLayout()

        # Create tabs widget
        self.tabs_widget = MainTabsWidget(self.local_library)
        self.setCentralWidget(self.tabs_widget)
        self.status_bar = QtWidgets.QStatusBar()
        if self.local_library.last_update_time:
            self.status_bar.showMessage('Last update: ' + time.strftime('%H:%M  %b %d', self.local_library.last_update_time))
        self.setStatusBar(self.status_bar)
        self.show()

    def init_library(self):
        for paper in self.local_library.papers:
            self.add_paper_to_the_model(paper)

    def add_paper_to_the_model(self, paper):
        qt_title = QtGui.QStandardItem(paper.title)
        qt_author = QtGui.QStandardItem(f'{paper.authors[0]} et al.' if len(paper.authors) > 1 else paper.authors[0])
        qt_time = QtGui.QStandardItem(time.strftime('%H:%M  %b %d', paper.published))
        tabIndex = self.tabs_widget.tab_roles.index(paper.status)
        self.tabs_widget.widget(tabIndex).model().appendRow([qt_title, qt_author, qt_time])

    def periodical_query(self, periodicity=300):
        self.arxiv_query()
        self.timer = threading.Timer(periodicity, self.periodical_query)
        self.timer.start()

    def arxiv_query(self):
        results = arxiv.query('astro-ph.HE', max_results=10, sort_by='submittedDate')
        if results:
            for paper_form in results:
                new_papers = 0
                if paper_form['id'] not in self.local_library.data['ids']:
                    paper = Paper(paper_form)
                    self.local_library.add_paper(paper)
                    self.add_paper_to_the_model(paper)
                    new_papers += 1
            self.local_library.update_time(time.localtime())
            self.status_bar.showMessage('Last update: ' + time.strftime('%H:%M  %b %d', self.local_library.last_update_time))
            self.local_library.save()
            self.local_library.print()

    def closeEvent(self, event):
        event.accept()
        self.timer.cancel()


class MainTabsWidget(QtWidgets.QTabWidget):
    def __init__(self, local_library):
        super(MainTabsWidget, self).__init__()
        self.local_library = local_library
        self.installEventFilter(self)
        self.setUsesScrollButtons(False)
        self.tab_names = ['New', 'Read', 'Deleted']
        self.tab_roles = ['new', 'read', 'deleted']
        for tab_name in self.tab_names:
            self.addTab(TableView(tab_name, self), tab_name)

    def eventFilter(self, QObject, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton:
                print("Right button clicked")
        return False


class TableView(QtWidgets.QTableView):
    def __init__(self, tab_name, main_tab_widget):
        super(TableView, self).__init__()
        self.main_tab_widget = main_tab_widget
        self.setModel(QtGui.QStandardItemModel())
        self.model().insertColumns(0, 3)
        self.model().setHorizontalHeaderLabels(['Title', 'Authors', 'Published'])
        self.setSelectionMode(3)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setGridStyle(0)
        self.verticalHeader().hide()
        self.setSortingEnabled(True)
        self.setSelectionBehavior(1)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnWidth(0, 700)
        self.setColumnWidth(1, 180)
        self.name = tab_name

    def contextMenuEvent(self, event):
        if self.name == 'New':
            cmenu = QtWidgets.QMenu(self)
            cmenu.addAction("Mark as read", lambda: self.mark_as_read())
            cmenu.addAction("Delete", lambda: self.delete())
            cmenu.exec_(self.mapToGlobal(event.pos()))
        if self.name == 'Read':
            cmenu = QtWidgets.QMenu(self)
            cmenu.addAction("Mark as new", lambda: self.mark_as_new())
            cmenu.addAction("Delete", lambda: self.delete())
            cmenu.exec_(self.mapToGlobal(event.pos()))
        if self.name == 'Deleted':
            cmenu = QtWidgets.QMenu(self)
            cmenu.addAction("Mark as read", lambda: self.mark_as_read())
            cmenu.addAction("Mark as new", lambda: self.mark_as_new())
            cmenu.addAction("Delete", lambda: self.delete())
            cmenu.exec_(self.mapToGlobal(event.pos()))

    def mark_as_new(self):
        selected_rows = [x.row() for x in self.selectionModel().selectedRows()][::-1]
        for row in selected_rows:
            row = self.model().takeRow(row)
            self.main_tab_widget.local_library.find_paper_by_title(row[0].text()).change_status('new')
            self.main_tab_widget.widget(0).model().appendRow(row)
        self.clearSelection()
        self.main_tab_widget.local_library.save()

    def mark_as_read(self):
        selected_rows = [x.row() for x in self.selectionModel().selectedRows()][::-1]
        for row in selected_rows:
            row = self.model().takeRow(row)
            self.main_tab_widget.local_library.find_paper_by_title(row[0].text()).change_status('read')
            self.main_tab_widget.widget(1).model().appendRow(row)
        self.clearSelection()
        self.main_tab_widget.local_library.save()

    def delete(self):
        selected_rows = [x.row() for x in self.selectionModel().selectedRows()][::-1]
        for row in selected_rows:
            row = self.model().takeRow(row)
            self.main_tab_widget.local_library.find_paper_by_title(row[0].text()).change_status('deleted')
            self.main_tab_widget.widget(2).model().appendRow(row)
        self.clearSelection()
        self.main_tab_widget.local_library.save()


class LocalLibrary():
    def __init__(self, local_library_path):
        self.path = local_library_path
        print(self.path)
        self.load()

    def load(self):
        try:
            self.data = pickle.load(open(self.path, 'rb'))
            self.papers = self.data['papers']
            self.papers_ids = self.data['ids']
            self.last_update_time = self.data['last_update_time']
        except FileNotFoundError or EOFError:
            self.data = {'ids': [], 'papers': [], 'last_update_time': None}
            self.papers = self.data['papers']
            self.papers_ids = self.data['ids']
            self.last_update_time = self.data['last_update_time']
            self.save()
            self.load()

    def save(self):
        pickle.dump(self.data, open(self.path, 'wb'))
        # self.load()

    def add_paper(self, paper):
        self.papers_ids.append(paper.id_numb)
        self.papers.append(paper)

    def print(self):
        for paper in self.data['papers']:
            print(paper.title)

    def find_paper_by_title(self, title):
        for paper in self.papers:
            if title == paper.title:
                return paper

    def update_time(self, time):
        self.last_update_time = time


class Paper():
    def __init__(self, paper_form):
        self.abstract = paper_form['summary']
        self.authors = paper_form['authors']
        self.arxiv_url = paper_form['arxiv_url']
        self.id_numb = paper_form['id']
        self.pdf_url = paper_form['pdf_url']
        self.published = paper_form['published_parsed']
        self.title = ' '.join(paper_form['title'].splitlines())
        self.title = ' '.join(self.title.split())

        self.status = 'new'

    def change_status(self, status):
        self.status = status
