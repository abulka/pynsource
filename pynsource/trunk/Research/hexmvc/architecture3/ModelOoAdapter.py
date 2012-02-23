from ModelAdapterBase import ModelAdapterBase

class ModelOoAdapter(ModelAdapterBase):
    def DeleteThing(self, thing):
        self.model.things.remove(thing)
        self.observers.MODEL_THING_DELETED(thing)
