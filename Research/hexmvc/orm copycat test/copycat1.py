import datetime

class WikiPage():
        def __init__(self, id, content):
            self.id = id
            self.content = content
            self.history = []
            self.last_modify = datetime.datetime.now()

class Wiki():
        def __init__(self):
            self.pages = {}
        def create_page(self, page_id, content):
            page = None
            if page_id in self.pages:
                page = self.pages[page_id]
            if not page:
                page = WikiPage(page_id, content)
                self.pages[page_id] = page
            return page
            
from copycat import init_system
wiki = init_system(Wiki(), "./files")
#wiki.create_page('My First Page', 'My First Page Content')
page = wiki.pages['My First Page']
print page
