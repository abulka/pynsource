#!/usr/bin/env python

"""
PureMVC minimalist wxpython example.
PureMVC stripped out and using multicast for broadcasting.  On its way to hexmvc.
"""

import wx
import abc
from architecture_support import *


class MyForm(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=3)
        self.inputFieldTxt = wx.TextCtrl(
            self, -1, size=(170, -1), pos=(5, 10), style=wx.TE_PROCESS_ENTER
        )


class MyFormMediator:
    def __init__(self, viewComponent):
        self.viewComponent = viewComponent
        self.viewComponent.Bind(wx.EVT_TEXT_ENTER, self.onSubmit, self.viewComponent.inputFieldTxt)
        self.observers = multicast()

    # def listNotificationInterests(self):
    #    return [ AppFacade.DATA_CHANGED ]

    # def handleNotification(self, notification):
    #    if notification.getName() == AppFacade.DATA_CHANGED:
    #        print "handleNotification (mediator) got", notification.getBody()
    #        mydata = notification.getBody()
    #        self.viewComponent.inputFieldTxt.SetValue(mydata)
    def DATA_CHANGED(self, mydata):
        print("handleNotification (mediator) got", mydata)
        self.viewComponent.inputFieldTxt.SetValue(mydata)

    def onSubmit(self, evt):
        mydata = self.viewComponent.inputFieldTxt.GetValue()
        # self.sendNotification(AppFacade.DATA_SUBMITTED, mydata)
        self.observers.DATA_SUBMITTED(mydata)


class DataSubmittedCommand:
    # def execute(self, notification):
    #    print "submit execute (command)", notification.getBody()
    #    mydata = notification.getBody()
    #    self.datamodelProxy = self.facade.retrieveProxy(DataModelProxy.NAME)
    #    self.datamodelProxy.setData(mydata.upper())
    def DATA_SUBMITTED(self, mydata):
        print("submit execute (command)", mydata)
        self.datamodelProxy.setData(mydata.upper())


class DataModelProxy:
    # NAME = "DataModelProxy"

    def __init__(self):
        self.realdata = Data()
        self.observers = multicast()
        # self.sendNotification(AppFacade.DATA_CHANGED, self.realdata.data)
        # self.observers.DATA_CHANGED(self.realdata.data)  # useless since not wired up yet !@!!!!!!!!!!!

    def Boot(
        self
    ):  # New - needed for HexMvc version since wiring of observers is much delayed so can't do it in init
        self.observers.DATA_CHANGED(self.realdata.data)

    def setData(self, data):
        self.realdata.data = data
        print("setData (model) to", data)
        #        self.sendNotification(AppFacade.DATA_CHANGED, self.realdata.data)
        self.observers.DATA_CHANGED(self.realdata.data)


class Data:
    def __init__(self):
        self.data = "Hello - hit enter"


class AppFacade:
    # DATA_SUBMITTED = "DATA_SUBMITTED"
    # DATA_CHANGED = "DATA_CHANGED"

    # @staticmethod
    # def getInstance():
    #    return AppFacade()

    def initializeController(self):
        # super(AppFacade, self).registerCommand(AppFacade.DATA_SUBMITTED, DataSubmittedCommand)
        pass


class AppFrame(wx.Frame):
    # myForm = None
    # mvcfacade = None

    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title="HexMVC Minimalist Demo", size=(200, 100))
        self.myForm = MyForm(parent=self)
        mediator = MyFormMediator(self.myForm)
        # self.mvcfacade = AppFacade.getInstance()
        # self.mvcfacade.registerMediator(MyFormMediator(self.myForm))
        # self.mvcfacade.registerProxy(DataModelProxy())
        dataproxy = DataModelProxy()
        cmd = DataSubmittedCommand()
        cmd.datamodelProxy = dataproxy  # hard wire rather than a complex proxy lookup system

        mediator.observers.addObserver(cmd)
        dataproxy.observers.addObserver(mediator)
        dataproxy.Boot()


class WxApp(wx.App):
    appFrame = None

    def OnInit(self):
        self.appFrame = AppFrame()
        self.appFrame.Show()
        return True


if __name__ == "__main__":
    wxApp = WxApp(redirect=False)
    wxApp.MainLoop()
