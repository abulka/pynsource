#!/usr/bin/env python

from hexappmodel import Thing

class PersistenceMock:
    def Save(self, model):
        pass
    
    def Load(self):
        pass
      
class PersistenceMock2:
    def __init__(self):
        self.savedmodel = [Thing("100"), Thing("101")]
        
    def SaveAll(self, model):
        self.savedmodel = model
    
    def LoadAll(self):
        return self.savedmodel
      
