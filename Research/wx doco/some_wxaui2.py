import wx
import wx.aui

########################################################################
class TabPanel(wx.Panel):
    """
    This will be the first notebook tab
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
        txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txtOne, 0, wx.ALL, 5)
        sizer.Add(txtTwo, 0, wx.ALL, 5)

        self.SetSizer(sizer)


class DemoPanel(wx.Panel):
    """
    This will be the first notebook tab
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # create the AuiNotebook instance
        nb = wx.aui.AuiNotebook(self)

        # add some pages to the notebook
        pages = [(TabPanel(nb), "Tab 1"), (TabPanel(nb), "Tab 2"), (TabPanel(nb), "Tab 3")]
        for page, label in pages:
            nb.AddPage(page, label)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 1, wx.EXPAND)
        self.SetSizer(sizer)


########################################################################
class DemoFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, "AUI-Notebook Tutorial", size=(600, 400))
        panel = DemoPanel(self)
        self.Show()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = DemoFrame()
    app.MainLoop()
