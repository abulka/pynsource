#!/usr/bin/env python

import wx
from hexmvcgui_gen import HexMvcGuiFrame1
import thread, time

# BOOT WIRING

from hexappmodel import App, Thing
from hexpersistence import PersistenceMock, PersistenceMock2
from hexserver import Server1

class MyFrame(HexMvcGuiFrame1):
    def __init__( self, parent ):
        HexMvcGuiFrame1.__init__( self, parent )
        self.need_abort = False
        wx.CallAfter(self.Andy, "hi")
        
    def Andy(self, msg):
        print msg + " Andy"
        #self.app.server.StartServer()
        
    def SetApp(self, app):
        self.app = app
        print "app has been set"

    def DumpModel( self, event ):
        self._DumpModel()

    def DumpClear( self, event ):
        self.m_textCtrl1.Clear()

    def AddJunkText( self, event ):
        self._AddJunkText()
        
    def MiscMessageBox( self, event ):
        wx.MessageBox("hi there")

    def FileLoad( self, event ):        
        self.app.Load()
        self._DumpModel()

    def FileNew( self, event ):        
        self.app.New()
        self._DumpModel()
        
    def _AddJunkText(self):
        self.m_textCtrl1.AppendText("asdasdasd ")

    def _IncrGuage(self):
        self.m_gauge1.Value += 1

    def _DumpModel(self):
        self.m_textCtrl1.AppendText(str(self.app.model))
        for thing in self.app.model.things:
            self.m_listBox1.Append(str(thing), thing)

    def BackgroundTask1( self, event ):
        self.need_abort = False
        self.m_gauge1.Range = 5
        self.m_gauge1.Value = 0
        thread.start_new_thread(self._DoSomeLongTask, ())

    def StopBackgroundTask1( self, event ):
        self.need_abort = True

    def _DoSomeLongTask(self):
        print "Background Task started"
        for i in range(0,5):
            if self.need_abort:
                print "aborted."
                return
            wx.CallAfter(self._AddJunkText)
            wx.CallAfter(self._IncrGuage)
            print '*',
            time.sleep(1)   # lets events through to the main wx thread and paints/messages get through ok
        print "Done Background Task."
        self.m_gauge1.Value = 0

        self._DoSomeLongTask2()

    def StartServer( self, event ):
        self.app.StartServer()

#wxapp = wx.App(redirect=False)
#frame = MyFrame(None)
#
#app = App(persistence=PersistenceMock2(), server=Server1(), gui=frame)
#
#frame.Show()
##frame.SetSize((400,400))
#wxapp.MainLoop()
#print "DONE - AFTER THE WX MAIN LOOP"


class MyApp(wx.App):
    def OnInit(self):
        print "OnInit"
        frame = MyFrame(parent=None)
        frame.Show()
        self.myframe = frame
        return True  # Return a success flag

#myapp = MyApp(redirect=False)
#print "myapp created"
#app = App(persistence=PersistenceMock2(), server=Server1(), gui=myapp.myframe)
#myapp.MainLoop()
#print "DONE - AFTER THE WX MAIN LOOP"
