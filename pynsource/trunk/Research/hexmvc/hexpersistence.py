#!/usr/bin/env python

from hexappmodel import ModelA

class PersistenceMock:
    def Save(self, model):
        pass
    
    def Load(self):
        model = ModelA(self)
        model.info = "mock info"
        return model
      

class PersistenceMock2:
    def __init__(self):
        self.savedmodel = [ModelA("100"), ModelA("101")]
        
    def SaveAll(self, model):
        self.savedmodel = model
    
    def LoadAll(self):
        return self.savedmodel
      
