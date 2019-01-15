import wx

# Posted to stack overflow https://stackoverflow.com/questions/54175692/wxpython-accelerators-fire-even-when-associated-menu-item-is-disabled

help = """
If you right click on this window, a popup menu will appear with
a single menuitem which is DISABLED.

The associated accelerator key CMD S can still be triggered, however.

Is this a bug?
Shouldn't the accelerator keys NOT fire when its associated menu item
is disabled?
"""

class MyForm(wx.Frame):

    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Accelerators fire even when menu item is disabled", size=(500,500))
        panel = wx.Panel(self, wx.ID_ANY)
        wx.StaticText(panel, wx.ID_ANY, help, wx.DefaultPosition, wx.DefaultSize, 0)
        self.cb = wx.CheckBox(panel, wx.ID_ANY, u"Enable Menuitem", wx.DefaultPosition, wx.DefaultSize, 0)
        self.popupmenu = wx.Menu()

        self.item: wx.Menuself.item = self.popupmenu.Append(wx.ID_ANY, "Do Something (CMD S)")
        self.Bind(wx.EVT_MENU, self.DoSomething, self.item)
        self.Bind(wx.EVT_CHECKBOX, self.OnCbChanged)

        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('S'), self.item.GetId() )])
        self.SetAcceleratorTable(accel_tbl)

        # hmm, accelerator still fires :-(
        self.item.Enable(self.cb.IsChecked())
        # self.popupmenu.Enable(self.item.GetId(), False)
        # wx.CallAfter(self.item.Enable, False)

        # frame doesn't get event EVT_RIGHT_UP (panel does), only gets EVT_CONTEXT_MENU
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnRight)

    def OnCbChanged(self, event):
        self.item.Enable(self.cb.IsChecked())

    def OnRight(self, event):
        self.PopupMenu(self.popupmenu)

    def DoSomething(self, event):
        if not self.item.Enabled:
            print("Hack - workaround - accelerator triggers but action blocked!")
            print(f"menu item id is {self.item.GetId()} and event id is {event.GetId()}")
            return

        msg = f"Something is being triggered, menuitem enabled state is: {self.item.Enabled}"
        print(msg)
        # dlg = wx.MessageDialog(self, msg, "Message", wx.OK | wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        frame = MyForm()
        frame.Show()
        self.SetTopWindow(frame)
        return True

# Run the program
if __name__ == "__main__":
    # app = wx.App(False)
    app = MyApp()
    app.MainLoop()
