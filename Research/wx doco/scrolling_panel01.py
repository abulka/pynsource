"""
http://stackoverflow.com/questions/5912761/wxpython-scrolled-panel-not-updating-scroll-bars

Anyway it appears that you missed the following things that are mandatory to
make scrolled panel works:

Scrolled panel must have a sizer. This could be done via
self.test_panel.SetSizer(self.a_sizer) method. All other controls inside the
panel must be attached to this sizer.

You must call SetupScrolling() method on your panel, e.g.
self.test_panel.SetupScrolling()

You must enable auto layout for the panel, e.g. self.test_panel.SetAutoLayout(1)

P.S. Have you ever seen an examples of the wxPython code? I'm asking since
almost all of them have wonderful method like __do_layout or something like
that. This approach will help to make your code much more readable.

EDIT:

You need to add self.test_panel.FitInside() to TextChange method in order to
force the panel to recalculate sizes of child controls and update its own
virtual size.

Here is complete solution:

"""

import wx
from wx.lib.scrolledpanel import ScrolledPanel


class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title, wx.DefaultPosition, wx.Size(600, 400))
        # Controls
        self.tin = wx.TextCtrl(self, size=wx.Size(600, 400), style=wx.TE_MULTILINE)
        self.test_panel = ScrolledPanel(self, size=wx.Size(600, 400))
        self.test_panel.SetupScrolling()
        self.tin2 = wx.StaticText(self.test_panel)

        # Layout
        # -- Scrolled Window
        self.panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel_sizer.Add(self.tin2, 0, wx.EXPAND)
        self.test_panel.SetSizer(self.panel_sizer)
        self.panel_sizer.Fit(self.test_panel)
        # -- Main Frame
        self.inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.inner_sizer.Add(self.tin, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 50)
        self.inner_sizer.Add(self.test_panel, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 50)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.inner_sizer, 1, wx.ALL | wx.EXPAND, 20)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.sizer.Layout()

        self.test_panel.SetAutoLayout(1)

        # Bind Events
        self.tin.Bind(wx.EVT_TEXT, self.TextChange)

    def TextChange(self, event):
        self.tin2.SetLabel(self.tin.GetValue())
        self.test_panel.FitInside()


class MyApp(wx.App):
    def OnInit(self):
        self.fr = MyFrame(None, -1, "TitleX")
        self.fr.Show(True)
        self.SetTopWindow(self.fr)
        return True


app = MyApp(0)
app.MainLoop()


def main():

    win = 1


if __name__ == "__main__":
    main()
