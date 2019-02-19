import wx
import random
from .DialogChooseFromList import MyDialogChooseFromList

test_data = ["test a", "test aa", "test aab", "test ab", "test abc", "test abcc", "test abcd"]


class MyDialog(MyDialogChooseFromList):
    def SetMyData(self, data):
        self.data = data
        self.m_listBox1.InsertItems(data, 0)

    def OnListDoubleClick(self, event):
        print(self.GetChosenItem())
        # self.Destroy()
        self.Close()

    def GetChosenItem(self):
        index = self.m_listBox1.GetSelection()
        return self.data[index]


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
        dialog = MyDialog(None)
        dialog.m_staticTextInstruction.Value = "Please Choose:"
        dialog.SetMyData(test_data)

        if dialog.ShowModal() == wx.ID_OK:
            print(dialog.GetChosenItem())
            # wx.MessageBox("Got the following\n%s\n%s\n%s" % (id, attrs, methods))

        dialog.Destroy()


def main():
    ex = wx.App()
    TestApp(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
