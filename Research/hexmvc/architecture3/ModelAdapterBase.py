import sys; sys.path.append("../lib")
from architecture_support import *

"""
This is the 'model' interface provided to the App, and is provided by the model
adapter (modelProxy). The methods include model manipulation and access methods,
as well as persistence methods. The Adapter has a reference to both the
underlying model and persistence object (if any).
"""

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
        raise Exception("DeleteThing not implemented in adapter");

    # Need to subclass depending on implementation
    
    def FindThing(self, id):
        raise Exception("FindThing() not implemented in this particular adapter");

    # Delegate to Persistence
    
    def LoadAll(self, filename=None):
        raise Exception("LoadAll not implemented in adapter");

    def SaveAll(self, filename=None):
        raise Exception("SaveAll not implemented in adapter");

