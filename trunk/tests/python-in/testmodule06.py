import utilcc
from observer import Observable
from event import eventfactory
from editorweather import WeatherEditor
from editorflags import FlagEditor
from editorturns import TurnEditor
import copy
import pprint, undo

class ParseMeTest(undo.UndoItem):
    def __init__(self, scenario):
        self.scenario = scenario
        self.flagsdict = None
        self.pointsdict = None
        self.weatherdict = None

        # Perhaps these should be in oobeditor? or perhaps weathereditor should be in resolverweather.
        self.flageditor = FlagEditor(gamestatusstate=self)
        self.weathereditor = WeatherEditor(gamestatusstate=self)
        self.turnseditor = TurnEditor(gamestatusstate=self)

        self.SetFlagsFromMemento(self.scenario.flagsinfochunk)

    def SetFlagsFromMemento(self, memento):
        if memento:
            self.flagsdict = eval(memento)
        else:
            self.flagsdict = {}
