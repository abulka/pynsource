class Model:
    def __init__(self, persistence):
        self.persistence = persistence
        self.things = []
        self.Clear()

    def __str__(self):
        return str([str(t) for t in self.things])

    def __len__(self):
        return len(self.things)

    def SetApp(self, app):
        self.app = app

    def Clear(self):
        self.things = []

    def LoadAll(self):
        self.things = self.persistence.LoadAll()

    def SaveAll(self):
        self.persistence.SaveAll(self.things)

    def CreateThing(self, info):
        return Thing(info)

    def DeleteThing(self, thing):
        self.things.remove(thing)


class Thing:
    def __init__(self, info):
        self.info = info

    def __str__(self):
        return "A-" + self.info

    def AddInfo(self, msg):
        self.info += " " + msg
