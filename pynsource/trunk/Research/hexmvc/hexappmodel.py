#!/usr/bin/env python

class App:
    def __init__(self, persistence):
        self.model = Model(self, persistence)
        
    def New(self):
        self.model.Clear()

    def Load(self):
        cmd = CmdLoadModel(self)
        cmd.Execute()

    def Save(self):
        cmd = CmdSaveModel(self)
        cmd.Execute()

    def CreateThing(self, info):
        cmd = CmdCreateThing(self)
        cmd.info = info
        cmd.Execute()
        return cmd.result

    def AddInfoToThing(self, a, info):
        cmd = CmdAddInfoToThing(self)
        cmd.a = a
        cmd.info = info
        cmd.Execute()

    def GetThing(self, n):
        return self.model.things[n]




class Cmd:
    def __init__(self, app):
        self.app = app

class CmdLoadModel(Cmd):
    def Execute(self):
        self.app.model.LoadAll()

class CmdSaveModel(Cmd):
    def Execute(self):
        self.app.model.SaveAll()

class CmdCreateThing(Cmd):
    def Execute(self):
        self.result = Thing(self.info)
        self.app.model.things.append(self.result)

class CmdAddInfoToThing(Cmd):
    def Execute(self):
        self.a.Do(self.info)




class Model:        
    def __init__(self, app, persistence):
        self.app = app
        self.persistence = persistence
        self.things = []
        self.Clear()

    def __str__(self):
        return str([str(t) for t in self.things])

    def __len__(self):
        return len(self.things)
        
    def Clear(self):
        self.things = []
        
    def LoadAll(self):
        self.things = self.persistence.LoadAll()

    def SaveAll(self):
        self.persistence.SaveAll(self.things)

class Thing:
    def __init__(self, info):
        self.info = info
        
    def __str__(self):
        return "A-" + self.info

    def Do(self, msg):
        self.info += " " + msg
