import wx
import random
from .FrameDeepLayout import FrameDeepLayout


class FrameDeepLayout2(FrameDeepLayout):
    def OnCancelClick(self, event):
        print("got cancel")
        self.Destroy()


class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TestFrame, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        self.SetSize((300, 200))
        self.SetTitle("Andy's Custom dialog tester")
        self.Centre()

        self.m_button1 = wx.Button(self, wx.ID_ANY, "Launch", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button1.Bind(wx.EVT_BUTTON, self.OnCancelClick)

        self.Show(True)
        self.MAIN()

    def OnCancelClick(self, event):
        self.MAIN()

    def MAIN(self):
        f = FrameDeepLayout2(parent=self)
        f.Show(True)


def main2():
    class MainApp(wx.App):
        def OnInit(self):
            """Init Main App."""
            self.frame = TestFrame(None)
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            return True

    app = MainApp(0)
    app.MainLoop()


def main():
    class MainApp(wx.App):
        def OnInit(self):
            """Init Main App."""
            self.frame = FrameDeepLayout(None)
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            return True

    app = MainApp(0)
    app.MainLoop()


if __name__ == "__main__":
    main2()
