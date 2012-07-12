#!/usr/bin/env python

"""
PureMVC minimalist wxpython example - Converted to HexMVC

Replacing hard to follow pure mvc home-grown eventing with simple multicast
calling of methods on objects. All objects/subsystems are injected hexagonal
style, and adhere to abstract interfaces for swappability.

On The Role of App
------------------
App has job of housing the domain logic and app logic and thus the controller/commands.
App also has job of wiring the ring adapters together as it knows the relationship of them all to each other.
App sometimes mediates - calls come in and app sends them out again.
App sometimes steps out of the way, wires up the ring adapters to talk to each other.

Instantiation should be outside the app.  Theoretically inject different ring adapters into the app
and the app will still work.

"""

import wx
import abc
import sys; sys.path.append("../lib")
from architecture_support import *

# GUI

class MyForm(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent,id=3)
        self.inputFieldTxt = wx.TextCtrl(self, -1, size=(170,-1), pos=(5, 10), style=wx.TE_PROCESS_ENTER)

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent=None, id=-1, title="HexMVC Minimalist Demo",size=(200,100))
        self.myForm = MyForm(parent=self)

class WxApp(wx.App):
    appFrame = None

    def OnInit(self):
        self.appFrame = AppFrame()
        self.appFrame.Show()
        return True

# GUI Mediator

class MyFormMediator:
    def __init__(self, viewComponent):
        self.viewComponent = viewComponent
        self.viewComponent.Bind(wx.EVT_TEXT_ENTER, self.onSubmit, self.viewComponent.inputFieldTxt)
        self.observers = multicast()
        
    def DATA_CHANGED(self, mydata):
        print "handleNotification (mediator) got", mydata
        self.viewComponent.inputFieldTxt.SetValue(mydata)

    def onSubmit(self, evt):
        mydata = self.viewComponent.inputFieldTxt.GetValue()
        self.observers.DATA_SUBMITTED(mydata)

# Model

class Data:
    def __init__(self):
        self.someinfo = "Hello - hit enter"

# Model Proxy

class DataModelProxy(object):
    def __init__(self):
        self.realdata = Data()
        self.observers = multicast()

    def Boot(self):  # New - needed for HexMvc version since wiring of observers is much delayed so can't do it in init
        self.observers.DATA_CHANGED(self.data)

    @property
    def data(self):
        return self.realdata.someinfo
    @data.setter
    def data(self, value):
        print "setData (model) to", value
        self.realdata.someinfo = value
        self.observers.DATA_CHANGED(self.data)

# App

# Controller

class DataSubmittedCommand():
    def __init__(self, model, mydata):
        self.model = model
        self.mydata = mydata

    def execute(self):
        print "CMD submit execute (command)"
        self.model.data = self.mydata.upper()

class Controller():
    def __init__(self, model):
        self.model = model

    def DATA_SUBMITTED(self, mydata):
        DataSubmittedCommand(self.model, mydata).execute()

class App:
    def __init__(self, model, gui):
        self.model = model
        self.controller = Controller(model)
        self.gui = gui
        model.app = self.controller.app = gui.app = self

        # Wire observers
        gui.observers.addObserver(self.controller)
        model.observers.addObserver(gui)
    
    def Boot(self):
        self.model.Boot()
    
if __name__ == '__main__':
    # Create Gui
    wxapp = WxApp(redirect=False)
    gui = MyFormMediator(wxapp.appFrame.myForm)
    
    # Create Model
    model = DataModelProxy()
    
    # Create Core Hexagon App and inject adapters
    app = App(model, gui)
    wx.CallAfter(app.Boot)
    
    # Start Gui
    wxapp.MainLoop()
    
    print "DONE"     
   
