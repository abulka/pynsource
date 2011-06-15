from sqlobject import *
from sqlobject.sqlite import builder; SQLiteConnection = builder()
conn = SQLiteConnection('hexpersist_sqlobject.db', debug=False)

class Model(SQLObject):        
    _connection = conn
    occupant = ForeignKey('Thing', default=None)
    
    def __init__(self, persistence):
        self.persistence = persistence
        self.things = []
        self.Clear()

    def __str__(self):
        return str([str(t) for t in self.things])

    def __len__(self):
        return len(self.things)
        
    def Clear(self):
        self.things = []
        
    def LoadAll(self):
        self.things = self.persistence.LoadAll()

    def SaveAll(self):
        self.persistence.SaveAll(self.things)

class Thing(SQLObject):
    _connection = conn
    info = StringCol(length=20)
    model = ForeignKey('Model', default=None)

    def __init__(self, info):
        self.info = info
        
    def __str__(self):
        return "A-" + self.info

    def AddInfo(self, msg):
        self.info += " " + msg
        