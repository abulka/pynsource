#!/usr/bin/python

# myscrolledwindow.py

import wx


class MyScrolledWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500, 400))

        sw = wx.ScrolledWindow(self)
        bmp = wx.Image("moo.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        wx.StaticBitmap(sw, -1, bmp)
        sw.SetScrollbars(20, 20, 55, 40)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyScrolledWindow(None, -1, "Aliens")
        frame.Show(True)
        frame.Centre()
        return True


app = MyApp(0)
app.MainLoop()
