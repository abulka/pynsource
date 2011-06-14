#!/usr/bin/env python

class App:
    def __init__(self, persistence, server, gui):
        self.model = Model(self, persistence)
        self.server = server
        self.gui = gui
        
        server.SetApp(self)
        persistence.SetApp(self)
        gui.SetApp(self)
        
    def Boot(self):
        self.server.StartServer()
        
    def GetUrlOrigin(self):
        return self.server.GetUrlOrigin()
        
    def GetModelSize(self):
        return len(self.model)
        
    def New(self):
        cmd = CmdNew(self)
        cmd.Execute()

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

    def DeleteThing(self, thing):
        cmd = CmdDeleteThing(self)
        cmd.thing = thing
        cmd.Execute()

    def AddInfoToThing(self, a, info):
        cmd = CmdAddInfoToThing(self)
        cmd.a = a
        cmd.info = info
        cmd.Execute()

    def GetThing(self, n):
        return self.model.things[n]

    def StartServer(self):
        cmd = CmdStartServer(self)
        cmd.server = self.server
        cmd.Execute()



class Cmd:
    def __init__(self, app):
        self.app = app

class CmdNew(Cmd):
    def Execute(self):
        self.app.model.Clear()
        self.app.gui.NotifyOfModelChange("clear", None)

class CmdLoadModel(Cmd):
    def Execute(self):
        self.app.model.LoadAll()
        self.app.gui.NotifyOfModelChange("loadall", None)

class CmdSaveModel(Cmd):
    def Execute(self):
        self.app.model.SaveAll()

class CmdCreateThing(Cmd):
    def Execute(self):
        self.result = Thing(self.info)
        self.app.model.things.append(self.result)

class CmdDeleteThing(Cmd):
    def Execute(self):
        self.app.gui.NotifyOfModelChange("delete", self.thing)
        self.app.model.things.remove(self.thing)

class CmdAddInfoToThing(Cmd):
    def Execute(self):
        self.a.Do(self.info)

class CmdStartServer(Cmd):
    def Execute(self):
        self.server.StartServer()



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
