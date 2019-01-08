# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Feb  9 2012)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

# import wx.xrc

###########################################################################
## Class MyDialogChooseFromList
###########################################################################


class MyDialogChooseFromList(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.Size(242, 303),
            style=wx.DEFAULT_DIALOG_STYLE,
        )

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticTextInstruction = wx.StaticText(
            self, wx.ID_ANY, "Choose a Sample UML diagram:", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_staticTextInstruction.Wrap(-1)
        bSizer1.Add(self.m_staticTextInstruction, 0, wx.ALL, 5)

        m_listBox1Choices = []
        self.m_listBox1 = wx.ListBox(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0
        )
        bSizer1.Add(self.m_listBox1, 1, wx.ALL | wx.EXPAND, 5)

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer1.AddButton(self.m_sdbSizer1OK)
        self.m_sdbSizer1Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer1.AddButton(self.m_sdbSizer1Cancel)
        m_sdbSizer1.Realize()

        bSizer1.Add(m_sdbSizer1, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_listBox1.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListDoubleClick)

    def __del__(self):
        pass

        # Virtual event handlers, overide them in your derived class

    def OnListDoubleClick(self, event):
        event.Skip()
