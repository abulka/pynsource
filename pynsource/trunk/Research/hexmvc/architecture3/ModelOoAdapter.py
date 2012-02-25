from ModelAdapterBase import ModelAdapterBase

class ModelOoAdapter(ModelAdapterBase):
    def __init__(self, model, persistence):
        ModelAdapterBase.__init__(self, model)
        self.persistence = persistence
        
    def DeleteThing(self, thing):
        self.model.things.remove(thing)
        self.observers.MODEL_THING_DELETED(thing)

    def LoadAll(self):
        self.model = self.persistence.LoadAll(self.model)

        self.observers.MODEL_STATUS_LOAD_OR_SAVE_ALL('Load All', True)
        self.observers.MODEL_CHANGED(self.model.things)

    def SaveAll(self):
        self.persistence.SaveAll(self.model)
        
        self.observers.MODEL_STATUS_LOAD_OR_SAVE_ALL('Save All', True)
