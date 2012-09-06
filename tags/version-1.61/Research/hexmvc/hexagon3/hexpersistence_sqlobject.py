from sqlobject import *

class Model(SQLObject):        
    things = MultipleJoin('Thing')

    #def __init__(self, persistence):
    #    #self.persistence = persistence
    #    #self.things = []
    #    self.Clear()

    def __str__(self):
        return str([str(t) for t in self.things])

    def __len__(self):
        return len(self.things)
        
    def Clear(self):
        for thing in self.things:
            Thing.delete(thing.id)
        
    def LoadAll(self):
        #self.things = self.persistence.LoadAll()
        pass

    def SaveAll(self):
        #self.persistence.SaveAll(self.things)
        pass

class Thing(SQLObject):
    info = StringCol(length=50)
    model = ForeignKey('Model', default=None)

    #def __init__(self, info):
    #    self.info = info
        
    def __str__(self):
        return "Thing: " + self.info

    def AddInfo(self, msg):
        self.info += " " + msg
        
if __name__ == "__main__":
    from sqlobject.sqlite import builder; SQLiteConnection = builder()
    conn = SQLiteConnection('hexpersistence_sqlobject.db', debug=False)
    sqlhub.processConnection = conn

    init = raw_input("Create from scratch? (y/n) ")
    if init == 'y':
        print "Recreating database..."
    
        Model.dropTable(True)
        Model.createTable()
        Thing.dropTable(True)
        Thing.createTable()
        
        model = Model()    
        thing1 = Thing(info="mary", model=model)
        thing2 = Thing(info="fred", model=model)
    else:
        model = Model.get(1)
        thing1 = Thing.get(1); print thing1
        thing2 = Thing.get(2); print thing2

    assert len(model.things) == 2
    assert thing1 in model.things
    assert thing2 in model.things

    # test deletion    
    thing3 = Thing(info="tmp", model=model); print thing3
    assert len(model.things) == 3
    Thing.delete(thing3.id)
    assert len(model.things) == 2

    print "done"
    