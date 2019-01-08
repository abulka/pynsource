import unittest

import sys

sys.path.append("..")

from hexappmodel import App, Thing
from hexpersistence import PersistenceMock, PersistenceMock2


class HexMvcTests(unittest.TestCase):
    def setUp(self):
        class PersistenceMock3:
            def __init__(self):
                self.savedmodel = [Thing("fred"), Thing("sam")]

            def SetApp(self, app):
                self.app = app

            def SaveAll(self, model):
                self.savedmodel = model

            def LoadAll(self):
                return self.savedmodel

        class GuiMock:
            def __init__(self):
                self._trace_notifycalls = 0

            def SetApp(self, app):
                self.app = app

            def NotifyOfModelChange(self, event, thing):
                self._trace_notifycalls += 1

        class ServerMock:
            def SetApp(self, app):
                self.app = app

        self.app = App(PersistenceMock3(), ServerMock(), GuiMock())

    def tearDown(self):
        pass

    def test01(self):
        app = self.app
        app.Load()
        # print app.model
        # interrogate(app.model)

        self.assertEqual(2, len(app.model))
        self.assertEqual("A-fred", str(app.GetThing(0)))
        self.assertEqual("A-sam", str(app.GetThing(1)))

        app.AddInfoToThing(app.GetThing(0), "flinstone")
        self.assertEqual("A-fred flinstone", str(app.GetThing(0)))

    def test02(self):
        app = self.app
        self.assertEqual(0, len(app.model))

        app.New()
        self.assertEqual(0, len(app.model))

        app.CreateThing("mary")
        app.CreateThing("elizabeth")
        self.assertEqual(2, len(app.model))

        app.Save()
        app.New()
        self.assertEqual(0, len(app.model))

        app.Load()
        self.assertEqual(2, len(app.model))
        self.assertEqual("A-mary", str(app.GetThing(0)))
        self.assertEqual("A-elizabeth", str(app.GetThing(1)))

    def test_CreateDelete(self):
        app = self.app
        thing = app.CreateThing("mary")
        self.assertEqual(1, len(app.model))
        app.DeleteThing(thing)
        self.assertEqual(0, len(app.model))

        self.assertEqual(1, app.gui._trace_notifycalls)


# Utility

import types


def interrogate(item):
    """Print useful information about item."""
    if hasattr(item, "__name__"):
        print("NAME:    ", item.__name__)
    if hasattr(item, "__class__"):
        print("CLASS:   ", item.__class__.__name__)
    print("ID:      ", id(item))
    print("TYPE:    ", type(item))
    print("VALUE:   ", repr(item))
    print("CALLABLE:", end=" ")
    if callable(item):
        print("Yes")
    else:
        print("No")
    if hasattr(item, "__doc__") and getattr(item, "__doc__") != None:
        doc = getattr(item, "__doc__")
        doc = doc.strip()  # Remove leading/trailing whitespace.
        firstline = doc.split("\n")[0]
        print("DOC:     ", firstline)
