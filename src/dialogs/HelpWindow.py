# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx

# import wx.xrc
import wx.html

###########################################################################
## Class HelpWindow
###########################################################################


class HelpWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="Pynsource Quick Help",
            pos=wx.DefaultPosition,
            size=wx.Size(637, 679),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_htmlWin1 = wx.html.HtmlWindow(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO
        )
        bSizer1.Add(self.m_htmlWin1, 25, wx.ALL | wx.EXPAND, 5)

        bSizer1.Add((0, 0), 1, wx.EXPAND, 5)

        self.btnCancelClose = wx.Button(
            self, wx.ID_ANY, "Close", wx.DefaultPosition, wx.DefaultSize, 0
        )
        bSizer1.Add(self.btnCancelClose, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.btnCancelClose.Bind(wx.EVT_BUTTON, self.OnCancelClick)

    def __del__(self):
        pass

        # Virtual event handlers, overide them in your derived class

    def OnCancelClick(self, event):
        event.Skip()


###########################################################################
## Class MyPanel1
###########################################################################


class MyPanel1(wx.Panel):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.Size(500, 300),
        style=wx.TAB_TRAVERSAL,
        name=wx.EmptyString,
    ):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

    def __del__(self):
        pass
