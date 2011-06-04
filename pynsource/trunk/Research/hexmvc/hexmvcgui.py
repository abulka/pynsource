#!/usr/bin/env python

import wx
from hexmvcgui_gen import HexMvcGuiFrame1

# BOOT WIRING

from hexappmodel import App, Thing
from hexpersistence import PersistenceMock, PersistenceMock2

class MyFrame(HexMvcGuiFrame1):
    def __init__( self, parent ):
        HexMvcGuiFrame1.__init__( self, parent )
        self.app = App(PersistenceMock2())
        
    def DumpModel( self, event ):
        self._DumpModel()

    def DumpClear( self, event ):
        self.m_textCtrl1.Clear()

    def Misc1( self, event ):
        self.m_textCtrl1.AppendText("asdasdasd ")
        
    def MiscMessageBox( self, event ):
        wx.MessageBox("hi there")

    def FileLoad( self, event ):        
        self.app.Load()
        self._DumpModel()

    def FileNew( self, event ):        
        self.app.New()
        self._DumpModel()
        
    def _DumpModel(self):
        self.m_textCtrl1.AppendText(str(self.app.model))
        for thing in self.app.model.things:
            self.m_listBox1.Append(str(thing), thing)
        
wxapp = wx.App()
frame = MyFrame(None)
frame.Show()
#frame.SetSize((400,400))
wxapp.MainLoop()
