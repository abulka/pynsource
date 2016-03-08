import wx
import wx.aui

class MyFrame(wx.Frame):

    def __init__(self, parent, id=-1, title='wx.aui Test',
                 pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = wx.aui.AuiManager(self)

        # create several text controls
        text1 = wx.TextCtrl(self, -1, 'Pane 1 - sample text',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)

        text2 = wx.TextCtrl(self, -1, 'Pane 2 - sample text',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)

        text3 = wx.TextCtrl(self, -1, 'Main content window',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)

        # add the panes to the manager
        self._mgr.AddPane(text1, wx.LEFT, 'Pane Number One')
        self._mgr.AddPane(text2, wx.BOTTOM, 'Pane Number Two')
        self._mgr.AddPane(text3, wx.CENTER)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def OnClose(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()
        # delete the frame
        self.Destroy()


app = wx.App()
frame = MyFrame(None)
frame.Show()
app.MainLoop()