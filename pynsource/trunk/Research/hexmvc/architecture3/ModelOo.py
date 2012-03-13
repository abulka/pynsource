# Simple (in memory) Model

class Model(object):
    def __init__(self):
        self.things = []
        self.next_id = 1

    def Clear(self):
        self.things = []
        print "simple model cleared"

    def AddThing(self, info, id=None):
        thing = Thing(info)
        thing.model = self  # backpointer
        if not id:
            id = self.next_id
            self.next_id += 1
        thing.id = id
        self.things.append(thing)
        return thing

    @property
    def size(self):
        return len(self.things)

class Thing:
    def __init__(self, info):
        self.model = None  # backpointer
        self.info = info
        self.id = None
        
    def __str__(self):
        return "Thing %d - %s" % (self.id, self.info)

    def AddInfo(self, msg):
        self.info += " " + msg
