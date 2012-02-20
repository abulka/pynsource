#!/usr/bin/env python

"""
PureMVC minimalist wxpython example - Converted to HexMVC

Replacing hard to follow pure mvc home-grown eventing with simple multicast
calling of methods on objects. All objects/subsystems are injected hexagonal
style, and adhere to abstract interfaces for swappability.
"""

import wx
import abc
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
        self.data = "Hello - hit enter"

# Model Proxy

class DataModelProxy():
    #NAME = "DataModelProxy"
    
    def __init__(self):
        self.realdata = Data()
        self.observers = multicast()

    def Boot(self):  # New - needed for HexMvc version since wiring of observers is much delayed so can't do it in init
        self.observers.DATA_CHANGED(self.realdata.data)

    def setData(self, data):
        self.realdata.data = data
        print "setData (model) to", data
        self.observers.DATA_CHANGED(self.realdata.data)

# App

# Controller

class DataSubmittedCommand():
    #def execute(self, notification):
    #    print "submit execute (command)", notification.getBody()
    #    mydata = notification.getBody()
    #    self.datamodelProxy = self.facade.retrieveProxy(DataModelProxy.NAME)
    #    self.datamodelProxy.setData(mydata.upper())
    def DATA_SUBMITTED(self, mydata):
        print "submit execute (command)", mydata
        self.datamodelProxy.setData(mydata.upper())

class App:
    def __init__(self, model, controller, gui):
        self.model = model
        self.controller = controller
        self.gui = gui
        model.app = controller.app = gui.app = self

        # WHATS THE POINT OF THE ABOVE IF NOTHING IS BEING ROUTED THROUGH APP
        # IF RING ADAPTERS ARE TALKING TO EACH OTHER VIA NOTIFICATIONS
        # AND WE ARE BYPASSING APP - HMMMMMM
        
        """
        Need to give the app the job of housing the logic and thus the commands.
        App also has job of wiring the ring adapters together as it knows the relationship of them all to each other.
        App sometimes mediates - calls come in and app sends them out again.
        App sometimes steps out of the way, wires up the ring adapters to talk to each other.
        
        Instantiation should be outside the app.  Theoretically inject different ring adapters into the app
        and the app will still work.
        """

        # Wire controller to point to model, hard wire rather than a complex proxy lookup system
        controller.datamodelProxy = model
        
        # Wire observers
        gui.observers.addObserver(controller)
        model.observers.addObserver(gui)
    
    def Boot(self):
        self.model.Boot()

    
if __name__ == '__main__':
    # Create Gui
    wxapp = WxApp(redirect=False)
    gui = MyFormMediator(wxapp.appFrame.myForm)
    
    # Create Model
    model = DataModelProxy()
    
    # Create Controller
    cmd = DataSubmittedCommand()
    
    # Create Core Hexagon App and inject adapters
    app = App(model, cmd, gui)
    wx.CallAfter(app.Boot)
    
    # Start Gui
    wxapp.MainLoop()
    
    print "DONE"     
    
