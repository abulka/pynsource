import wx

class MainApp(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, -1, "test",)
        self.frame.CreateStatusBar()
        self.frame.Show(True)
        return True

def main():
    application = MainApp(0)
    application.MainLoop()

if __name__ == "__main__":
    main()
