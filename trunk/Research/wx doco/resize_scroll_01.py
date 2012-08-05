import wx

class ScrollbarFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Scrollbar Example', size=(300, 200))
        self.scroll = wx.ScrolledWindow(self, -1)
        self.scroll.SetScrollbars(1, 1, 600, 400)
        self.button = wx.Button(self.scroll, -1, "Scroll Me", pos=(50, 20))
        self.Bind(wx.EVT_BUTTON,  self.OnClickTop, self.button)
        self.button2 = wx.Button(self.scroll, -1, "Scroll Back", pos=(500, 350))
        self.Bind(wx.EVT_BUTTON, self.OnClickBottom, self.button2)

        self.button = wx.Button(self.scroll, -1, "Extend scroll area1", pos=(50, 120))
        self.Bind(wx.EVT_BUTTON,  self.OnClickExtend1, self.button)
        self.button = wx.Button(self.scroll, -1, "Shrink scroll area1", pos=(150, 120))
        self.Bind(wx.EVT_BUTTON,  self.OnClickShrink1, self.button)

    def OnClickTop(self, event):
        self.scroll.Scroll(600, 400)
        
    def OnClickBottom(self, event):
        self.scroll.Scroll(1, 1)
        
    def OnClickExtend1(self, event):
        self.scroll.SetScrollbars(1, 1, 1600, 1400)

    def OnClickShrink1(self, event):
        self.scroll.SetScrollbars(1, 1, 600, 400)




app = wx.PySimpleApp()
frame = ScrollbarFrame()
frame.Show()
app.MainLoop()
