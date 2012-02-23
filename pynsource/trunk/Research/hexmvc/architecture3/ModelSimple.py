# Simple (in memory) Model

class Model(object):
    def __init__(self):
        self.things = []

    def Clear(self):
        self.things = []
        print "simple model cleared"

    def AddThing(self, info):
        thing = Thing(info)
        thing.model = self  # backpointer
        self.things.append(thing)
        return thing

    @property
    def size(self):
        return len(self.things)

class Thing:
    def __init__(self, info):
        self.model = None  # backpointer
        self.info = info
        
    def __str__(self):
        return "Thing!-" + self.info

    def AddInfo(self, msg):
        self.info += " " + msg
