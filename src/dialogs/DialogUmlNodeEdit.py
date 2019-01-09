# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Mar 22 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class DialogUmlNodeEdit
###########################################################################


class DialogUmlNodeEdit(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="Uml Node Properties",
            pos=wx.DefaultPosition,
            size=wx.Size(264, 286),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer9 = wx.BoxSizer(wx.VERTICAL)

        self.m_panel2 = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        bSizer11 = wx.BoxSizer(wx.VERTICAL)

        bSizer12 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText1 = wx.StaticText(
            self.m_panel2, wx.ID_ANY, "Class Name", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_staticText1.Wrap(-1)
        self.m_staticText1.SetMinSize(wx.Size(55, -1))

        bSizer12.Add(self.m_staticText1, 0, wx.ALL, 5)

        self.txtClassName = wx.TextCtrl(
            self.m_panel2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_PROCESS_ENTER,
        )
        bSizer12.Add(self.txtClassName, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        bSizer11.Add(bSizer12, 0, wx.EXPAND, 5)

        bSizer14 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText2 = wx.StaticText(
            self.m_panel2, wx.ID_ANY, "Attributes", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_staticText2.Wrap(-1)
        self.m_staticText2.SetMinSize(wx.Size(55, -1))

        bSizer14.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.txtAttrs = wx.TextCtrl(
            self.m_panel2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_MULTILINE,
        )
        bSizer14.Add(self.txtAttrs, 1, wx.ALL | wx.EXPAND, 5)

        bSizer11.Add(bSizer14, 1, wx.EXPAND, 5)

        bSizer13 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText3 = wx.StaticText(
            self.m_panel2, wx.ID_ANY, "Methods", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_staticText3.Wrap(-1)
        self.m_staticText3.SetMinSize(wx.Size(55, -1))

        bSizer13.Add(self.m_staticText3, 0, wx.ALL, 5)

        self.txtMethods = wx.TextCtrl(
            self.m_panel2,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_MULTILINE,
        )
        bSizer13.Add(self.txtMethods, 1, wx.ALL | wx.EXPAND, 5)

        bSizer11.Add(bSizer13, 1, wx.EXPAND, 5)

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button(self.m_panel2, wx.ID_OK)
        m_sdbSizer1.AddButton(self.m_sdbSizer1OK)
        self.m_sdbSizer1Cancel = wx.Button(self.m_panel2, wx.ID_CANCEL)
        m_sdbSizer1.AddButton(self.m_sdbSizer1Cancel)
        m_sdbSizer1.Realize()
        bSizer11.Add(m_sdbSizer1, 1, wx.EXPAND, 5)

        self.m_panel2.SetSizer(bSizer11)
        self.m_panel2.Layout()
        bSizer11.Fit(self.m_panel2)
        bSizer9.Add(self.m_panel2, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer9)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.txtClassName.Bind(wx.EVT_TEXT_ENTER, self.OnClassNameEnter)

    def __del__(self):
        pass

        # Virtual event handlers, overide them in your derived class

    def OnClassNameEnter(self, event):
        event.Skip()
