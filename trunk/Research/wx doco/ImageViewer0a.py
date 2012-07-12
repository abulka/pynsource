#!/usr/bin/env python

import wx, os

class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):

        wx.Frame.__init__(self, *args, **kwargs)
        
        sw = wx.ScrolledWindow(self)
        
        bmp = wx.Image('moo.jpg',wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        wx.StaticBitmap(sw, -1, bmp)
        sw.SetScrollbars(20,20,55,40)
       
class App(wx.App):
    def OnInit(self):
        frame = TestFrame(None, title="Andy wxBitmap Test")
        frame.Show(True)
        frame.Centre()
        return True

if __name__ == "__main__":
    app = App(0)
    app.MainLoop()
    
"""
You'll be better off not using a wx.StaticBitmap for this.  (After all 
static means unchanging.)  Instead catch the EVT_PAINT event and draw 
the bitmap yourself.  Then you can do things like stretching it to fit 
the window, or whatever you want.  Just convert it to a wx.Image, 
manipulate it, convert to a wx.Bitmap and draw it.
"""
