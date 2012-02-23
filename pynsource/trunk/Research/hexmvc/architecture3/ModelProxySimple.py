from ModelProxyBase import ModelProxyBase

class ModelProxySimple(ModelProxyBase):
    def DeleteThing(self, thing):
        self.model.things.remove(thing)
        self.observers.MODEL_THING_DELETED(thing)
