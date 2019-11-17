import pickle
import threading
import arxiv


class LocalLibrary():
    def __init__(self, local_library_path='library'):
        self.path = local_library_path
        self.load()

    def load(self):
        try:
            self.data = pickle.load(open(self.path, 'rb'))
            self.papers = self.data['papers']
            self.papers_ids = self.data['ids']
        except FileNotFoundError or EOFError:
            self.data = {'ids': [], 'papers': []}
            self.papers = self.data['papers']
            self.papers_ids = self.data['ids']
            self.save()

    def save(self):
        pickle.dump(self.data, open(self.path, 'wb'))
        self.load()

    def add_paper(self, paper):
        self.papers_ids.append(paper.id_numb)
        self.papers.append(paper)

    def print(self):
        for paper in self.data['papers']:
            print(paper.title)


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


def periodical_query(local_library, periodicity=3):
    arxiv_query(local_library)
    threading.Timer(periodicity, periodical_query).start()


def arxiv_query(local_library):
    resutls = arxiv.query('astro-ph.HE', max_results=10, sort_by='submittedDate')
    for paper_form in resutls:
        new_papers = 0
        if paper_form['id'] not in local_library.data['ids']:
            local_library.add_paper(Paper(paper_form))
            new_papers += 1
    local_library.save()
    local_library.print()
    return resutls
