# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx

# import wx.xrc

###########################################################################
## Class DialogComment
###########################################################################


class DialogComment(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="Comment",
            pos=wx.DefaultPosition,
            size=wx.Size(372, 286),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer9 = wx.BoxSizer(wx.VERTICAL)

        self.m_panel2 = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        bSizer11 = wx.BoxSizer(wx.VERTICAL)

        bSizer13 = wx.BoxSizer(wx.HORIZONTAL)

        self.txt_comment = wx.TextCtrl(
            self.m_panel2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_MULTILINE,
        )
        self.txt_comment.SetMaxLength(0)
        bSizer13.Add(self.txt_comment, 1, wx.ALL | wx.EXPAND, 5)

        bSizer11.Add(bSizer13, 5, wx.EXPAND, 5)

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button(self.m_panel2, wx.ID_OK)
        m_sdbSizer1.AddButton(self.m_sdbSizer1OK)
        self.m_sdbSizer1Cancel = wx.Button(self.m_panel2, wx.ID_CANCEL)
        m_sdbSizer1.AddButton(self.m_sdbSizer1Cancel)
        m_sdbSizer1.Realize()

        bSizer11.Add(m_sdbSizer1, 1, wx.ALIGN_CENTER, 5)

        self.m_panel2.SetSizer(bSizer11)
        self.m_panel2.Layout()
        bSizer11.Fit(self.m_panel2)
        bSizer9.Add(self.m_panel2, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer9)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
