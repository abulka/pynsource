from ModelAdapterBase import ModelAdapterBase

class ModelOoAdapter(ModelAdapterBase):
    def __init__(self, model, persistence):
        ModelAdapterBase.__init__(self, model)
        self.persistence = persistence
        
    def DeleteThing(self, thing):
        self.model.things.remove(thing)
        self.observers.MODEL_THING_DELETED(thing)

    def LoadAll(self, filename=None):
        self.model = self.persistence.LoadAll(self.model, filename)

        self.observers.MODEL_STATUS_LOAD_OR_SAVE_ALL('Load All', True)
        self.observers.MODEL_CHANGED(self.model.things)

    def SaveAll(self, filename=None):
        self.persistence.SaveAll(self.model, filename)
        
        self.observers.MODEL_STATUS_LOAD_OR_SAVE_ALL('Save All', True)

    def FindThing(self, id):
        assert type(id) is int
        for thing in self.model.things:
            if thing.id == id:
                return thing
        return None
