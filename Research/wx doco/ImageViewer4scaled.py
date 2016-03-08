#!/usr/bin/python

import wx

class TestApp(wx.App):
    def OnInit(self):
        self.MainFrame = wx.Frame(None, -1, "Test Frame")
        self.MainFrame.SetBackgroundColour(wx.WHITE)
        
        self.sw = wx.ScrolledWindow(self.MainFrame)
        self.sw.SetScrollbars(20,20,55,40)

        self.BMP = wx.Bitmap("../../outyuml.png", wx.BITMAP_TYPE_PNG)
        
        self.sw.Bind(wx.EVT_PAINT, self.OnPaint)
        
        #self.MainFrame.Bind(wx.EVT_PAINT, self.OnPaint)
        self.MainFrame.Show()
        return True
    
    def OnPaint(self, Event):
        DC = wx.PaintDC(self.sw, self.BMP, wx.BUFFER_VIRTUAL_AREA) 
        #DC = wx.PaintDC(self.sw)
        DC.SetUserScale(2,2) # ANDY
        DC.DrawBitmap(self.BMP, 0, 0)
        Event.Skip()

App = TestApp(1)
App.MainLoop()
