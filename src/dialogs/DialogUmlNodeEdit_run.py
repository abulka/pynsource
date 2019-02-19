import wx
import random
from .DialogUmlNodeEdit import DialogUmlNodeEdit


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
        id = "D" + str(random.randint(1, 99))
        dialog = DialogUmlNodeEdit(None)
        dialog.txtClassName.Value = id
        dialog.txtAttrs.Value = "aa\nbb\nccc"

        if dialog.ShowModal() == wx.ID_OK:
            id = dialog.txtClassName.Value
            attrs = dialog.txtAttrs.Value.split("\n")
            methods = dialog.txtMethods.Value.split("\n")

            wx.MessageBox("Got the following\n%s\n%s\n%s" % (id, attrs, methods))
        dialog.Destroy()


def main():
    ex = wx.App()
    TestApp(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
