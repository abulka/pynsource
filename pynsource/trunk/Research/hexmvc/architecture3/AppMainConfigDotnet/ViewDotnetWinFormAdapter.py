﻿from architecture_support import *

import System.Diagnostics.Process
import random

# GUI Form is auto generated by SharpDevelop
from ViewDotnetWinForm import MainForm

# GUI Mediator inherits rather than wraps the viewComponent, in this case, due
# to the way wxBuilder sends us events - expecting us to override handlers

class WinFormAdapter(MainForm):
    def __init__(self):
        MainForm.__init__(self)
        self.app = None
        self.observers = multicast()
        self.callAfter = None

    def onLoad(self, sender, e):
        # Call whatever method has been wired (by the master app) into self.callAfter so that 
        # we know the form is all set up and ready for app to start.  Its typically the app.Boot method.
        if self.callAfter:
            self.callAfter()

    def Boot(self):
        print "BOOT"
        self._InitHyperlinks()

    # Util

    def _InitHyperlinks(self):
        def seturl(obj):
            #obj.SetURL(self.app.url_server + obj.Text)
            self._toolTip1.SetToolTip(obj, obj.Text)
        seturl(self._linkLabel1)
        seturl(self._linkLabel2)
        seturl(self._linkLabel3)

    # Gui Generated Events, override the handler here
        
    def BtnDebug1Click(self, sender, e):
        print "got debug event"
        from System.Collections import ArrayList
        self.array = ArrayList()
        for i in xrange(10):
          self.array.Add(i)
        self._listBox1.DataSource = self.array
        self.array.Add(100)
        self.array.Add(200)
        self.array.Add(300)

    
    def OnLinkClicked(self, sender, e):
        print "link clicked", sender.Text
        System.Diagnostics.Process.Start(self.app.url_server + sender.Text)
    
    def OnAddThing(self, sender, e):
        info = str(random.randint(0,99999)) + " " + self._inputFieldTxt.Text
        self.observers.CMD_ADD_THING(info)
        print info

    # Non Gui Incoming Events

    def MODEL_THING_ADDED(self, thing, modelsize):
        #self.self._listBox1.Add(str(thing), thing)
        self._listBox1.Items.Add(str(thing))

"""

    # Util

    def _FindClientData(self, control, clientData):
        # Listboxes etc. don't support finding via clientData so I wrote this.
        for i in range(0, self.m_listBox1.GetCount()):
            if self.m_listBox1.GetClientData(i) == clientData:
                return i
        return wx.NOT_FOUND

    def _RepairSelection(self, index):
        if self.m_listBox1.IsEmpty():
            return
        index = max(0, index-1)
        self.m_listBox1.SetSelection(index)
        
    # Gui Generated Events, override the handler here
    
    def OnFileNew(self, event):
        self.observers.CMD_FILE_NEW()

    def OnLoadAll(self, event):
        self.observers.CMD_FILE_LOAD_ALL()

    def OnSaveAll(self, event):
        self.observers.CMD_FILE_SAVE_ALL()

    def OnAddInfoToThing(self, event):
        if self.m_listBox1.IsEmpty():
            return
        index = self.m_listBox1.GetSelection()
        if index == wx.NOT_FOUND:
            return
        thing = self.m_listBox1.GetClientData(index) # see ItemContainer methods http://www.wxpython.org/docs/api/wx.ItemContainer-class.html
        self.observers.CMD_ADD_INFO_TO_THING(thing, "Z")

    def OnDeleteThing(self, event):
        if self.m_listBox1.IsEmpty():
            return
        index = self.m_listBox1.GetSelection()
        thing = self.m_listBox1.GetClientData(index) # see ItemContainer methods http://www.wxpython.org/docs/api/wx.ItemContainer-class.html
        self.observers.CMD_DELETE_THING(thing)

    def OnDumpModel(self, event):
        #self.m_textCtrlDump.Clear()
        self.m_textCtrlDump.AppendText(str(self.app.model) + "\n")

    # Non Gui Incoming Events
    
    def MODEL_CLEARED(self):
        self.m_listBox1.Clear()
        
    def MODEL_CHANGED(self, things):
        self.m_listBox1.Clear()
        for thing in things:
            self.m_listBox1.Append(str(thing), thing)

    def MODEL_THING_UPDATE(self, thing):
        index = self._FindClientData(self.m_listBox1, thing)
        if index != wx.NOT_FOUND:
            self.m_listBox1.SetString(index, str(thing))  # Maybe .Set() does both at the same time?
            self.m_listBox1.SetClientData(index, thing)

    def MODEL_THING_DELETED(self, thing):
        index = self._FindClientData(self.m_listBox1, thing)
        if index != wx.NOT_FOUND:
            self.m_listBox1.Delete(index)
            self._RepairSelection(index)        

    def MODEL_STATUS_LOAD_OR_SAVE_ALL(self, msg, success):
        self.m_statusBar1.SetStatusText("%(msg)s result: %(success)s" % vars())

class MyWxApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        frame = MyFormMediator(parent=None)
        frame.Show()
        self.myframe = frame
        return True

"""
