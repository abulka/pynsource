import sys; sys.path.append("../lib")
from architecture_support import *

class ModelAdapterBase(object):
    def __init__(self, model):
        self.app = None
        self.model = model
        self.observers = multicast()

    def Boot(self):
        self.observers.MODEL_CHANGED(self.things)

    def __str__(self):
        return str([str(t) for t in self.model.things])

    @property
    def size(self):
        return self.model.size

    @property
    def things(self):
        return self.model.things

    # Things you can do to the Model
    
    def Clear(self):
        self.model.Clear()
        self.observers.MODEL_CLEARED()

    def AddThing(self, info):
        thing = self.model.AddThing(info)
        self.observers.MODEL_THING_ADDED(thing, self.size)
        return thing

    def AddInfoToThing(self, thing, moreinfo):
        thing.AddInfo(moreinfo)
        self.observers.MODEL_THING_UPDATE(thing)

    def DeleteThing(self, thing):
        raise Exception("DeleteThing not implemented in proxy");

    def LoadAll(self, thing):
        raise Exception("LoadAll not implemented in proxy");

    def SaveAll(self, thing):
        raise Exception("SaveAll not implemented in proxy");

