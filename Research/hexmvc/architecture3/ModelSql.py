# SqlObject Model

from sqlobject import *

class Model(SQLObject):
    things = MultipleJoin('Thing')

    @property
    def size(self):
        return len(self.things)
        
    def Clear(self):
        for thing in self.things:
            Thing.delete(thing.id)

    def AddThing(self, info):
        thing = Thing(info=info, model=self)
        return thing

class Thing(SQLObject):
    info = StringCol(length=50)
    model = ForeignKey('Model', default=None)

    def __str__(self):
        return "Thing %d - %s" % (self.id, self.info)

    def to_dict(self):
        return {"id":self.id, "info":self.info}
        
    def AddInfo(self, msg):
        self.info += " " + msg
