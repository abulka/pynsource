#!/usr/bin/env python


class App:
    def __init__(self, model, server, gui):
        self.model = model
        self.server = server
        self.gui = gui

        model.SetApp(self)
        server.SetApp(self)
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

    def AddInfoToThing(self, thing, info):
        cmd = CmdAddInfoToThing(self)
        cmd.thing = thing
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
        self.result = self.app.model.CreateThing(self.info)
        self.app.model.things.append(self.result)


class CmdDeleteThing(Cmd):
    def Execute(self):
        self.app.gui.NotifyOfModelChange("delete", self.thing)
        self.app.model.DeleteThing(self.thing)


class CmdAddInfoToThing(Cmd):
    def Execute(self):
        self.thing.AddInfo(self.info)
        self.app.gui.NotifyOfModelChange("update", self.thing)


class CmdStartServer(Cmd):
    def Execute(self):
        self.server.StartServer()
