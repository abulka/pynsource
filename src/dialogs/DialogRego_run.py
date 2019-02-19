import wx
from DialogRego import RegoDialog


class TestApp(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TestApp, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        self.SetSize((300, 200))
        self.SetTitle("Andy's Custom dialog tester")
        self.Centre()
        self.Show(True)
        self.MAIN()

    def MAIN(self):
        dialog = RegoDialog(None)
        dialog.m_textCtrl_name.Value = ""
        dialog.m_textCtrl_serial.Value = ""

        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.m_textCtrl_name.Value
            serial = dialog.m_textCtrl_serial.Value

            wx.MessageBox(f"Got the following\n{name}\n{serial}")
        dialog.Destroy()


def main():
    ex = wx.App()
    TestApp(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
