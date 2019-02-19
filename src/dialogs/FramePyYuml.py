# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Feb  9 2012)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

# import wx.xrc
from common.gui_imageviewer import ImageViewer

###########################################################################
## Class MyFrame1
###########################################################################


class MyFrame1(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="PyYuml Gui",
            pos=wx.DefaultPosition,
            size=wx.Size(500, 300),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        self.m_menubar1 = wx.MenuBar(0)
        self.m_menu1 = wx.Menu()
        self.m_menuItem5 = wx.MenuItem(
            self.m_menu1,
            wx.ID_ANY,
            "Import Python Code..." + "\t" + "CTRL+I",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu1.AppendItem(self.m_menuItem5)

        self.m_menu1.AppendSeparator()

        self.m_menuItem3 = wx.MenuItem(
            self.m_menu1, wx.ID_ANY, "Open..." + "\t" + "CTRL+O", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu1.AppendItem(self.m_menuItem3)

        self.m_menuItem4 = wx.MenuItem(
            self.m_menu1, wx.ID_ANY, "Save As..." + "\t" + "CTRL+S", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu1.AppendItem(self.m_menuItem4)

        self.m_menu1.AppendSeparator()

        self.m_menuItem6 = wx.MenuItem(
            self.m_menu1, wx.ID_ANY, "Exit", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu1.AppendItem(self.m_menuItem6)

        self.m_menubar1.Append(self.m_menu1, "File")

        self.m_menu2 = wx.Menu()
        self.m_menuItem2 = wx.MenuItem(
            self.m_menu2, wx.ID_ANY, "About...", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu2.AppendItem(self.m_menuItem2)

        self.m_menubar1.Append(self.m_menu2, "Help")

        self.SetMenuBar(self.m_menubar1)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_customControl1 = ImageViewer(self)
        bSizer1.Add(self.m_customControl1, 1, wx.ALL | wx.EXPAND, 1)

        self.SetSizer(bSizer1)
        self.Layout()
        self.m_statusBar1 = self.CreateStatusBar(1, wx.STB_SIZEGRIP, wx.ID_ANY)

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_MENU, self.OnImport, id=self.m_menuItem5.GetId())
        self.Bind(wx.EVT_MENU, self.OnOpen, id=self.m_menuItem3.GetId())
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=self.m_menuItem4.GetId())
        self.Bind(wx.EVT_MENU, self.OnExit, id=self.m_menuItem6.GetId())
        self.Bind(wx.EVT_MENU, self.OnAbout, id=self.m_menuItem2.GetId())

    def __del__(self):
        pass

        # Virtual event handlers, overide them in your derived class

    def OnImport(self, event):
        event.Skip()

    def OnOpen(self, event):
        event.Skip()

    def OnSaveAs(self, event):
        event.Skip()

    def OnExit(self, event):
        event.Skip()

    def OnAbout(self, event):
        event.Skip()
