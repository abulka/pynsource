import wx
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(350, 300))

        splitter = wx.SplitterWindow(self, -1)
        panel1 = wx.Panel(splitter, -1)
        wx.StaticText(panel1, -1,
                    "Whether you think that you can, or that you can't, you are usually right."
                    "\n\n Henry Ford",
            (100,100), style=wx.ALIGN_CENTRE)
        panel1.SetBackgroundColour(wx.LIGHT_GREY)
        panel2 = wx.Panel(splitter, -1)
        panel2.SetBackgroundColour(wx.WHITE)
        splitter.SplitVertically(panel1, panel2)
        self.Centre()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'splitterwindow.py')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()
