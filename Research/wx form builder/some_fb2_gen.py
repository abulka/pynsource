# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Mar 22 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.aui
from someStyledTextCtrl2 import PythonSTC

###########################################################################
## Class MyFrame1
###########################################################################


class MyFrame1(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.Size(557, 361),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_auiToolBar1 = wx.aui.AuiToolBar(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT
        )
        self.m_button1 = wx.Button(
            self.m_auiToolBar1, wx.ID_ANY, "MyButton", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_auiToolBar1.AddControl(self.m_button1)
        self.m_bpButton1 = wx.BitmapButton(
            self.m_auiToolBar1,
            wx.ID_ANY,
            wx.NullBitmap,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BU_AUTODRAW,
        )
        self.m_auiToolBar1.AddControl(self.m_bpButton1)
        self.m_staticText1 = wx.StaticText(
            self.m_auiToolBar1, wx.ID_ANY, "MyLabel", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_staticText1.Wrap(-1)
        self.m_auiToolBar1.AddControl(self.m_staticText1)
        self.m_slider1 = wx.Slider(
            self.m_auiToolBar1,
            wx.ID_ANY,
            50,
            0,
            100,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SL_HORIZONTAL,
        )
        self.m_auiToolBar1.AddControl(self.m_slider1)
        self.m_button2 = wx.Button(
            self.m_auiToolBar1, wx.ID_ANY, "MyButton", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_auiToolBar1.AddControl(self.m_button2)
        self.m_auiToolBar1.Realize()

        bSizer1.Add(self.m_auiToolBar1, 0, wx.ALL, 5)

        self.m_auinotebook1 = wx.aui.AuiNotebook(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE
        )
        self.m_panel4 = wx.Panel(
            self.m_auinotebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        self.m_auinotebook1.AddPage(self.m_panel4, "a page", True, wx.NullBitmap)
        self.m_panel5 = wx.Panel(
            self.m_auinotebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        self.m_auinotebook1.AddPage(self.m_panel5, "a page", False, wx.NullBitmap)

        bSizer1.Add(self.m_auinotebook1, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.m_statusBar1 = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)
        self.m_menubar1 = wx.MenuBar(0)
        self.m_menu1 = wx.Menu()
        self.m_menuItem1 = wx.MenuItem(
            self.m_menu1, wx.ID_ANY, "MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu1.AppendItem(self.m_menuItem1)

        self.m_menuItem2 = wx.MenuItem(
            self.m_menu1, wx.ID_ANY, "MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu1.AppendItem(self.m_menuItem2)

        self.m_menuItem3 = wx.MenuItem(
            self.m_menu1, wx.ID_ANY, "MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu1.AppendItem(self.m_menuItem3)

        self.m_menubar1.Append(self.m_menu1, "MyMenu")

        self.m_menu3 = wx.Menu()
        self.m_menu11 = wx.Menu()
        self.m_menuItem4 = wx.MenuItem(
            self.m_menu11, wx.ID_ANY, "MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu11.AppendItem(self.m_menuItem4)

        self.m_menuItem5 = wx.MenuItem(
            self.m_menu11, wx.ID_ANY, "MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu11.AppendItem(self.m_menuItem5)

        self.m_menu3.AppendSubMenu(self.m_menu11, "MyMenu")

        self.m_menubar1.Append(self.m_menu3, "MyMenu")

        self.SetMenuBar(self.m_menubar1)

        self.Centre(wx.BOTH)

    def __del__(self):
        pass


###########################################################################
## Class MyFrame2
###########################################################################


class MyFrame2(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.Size(500, 300),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.m_notebook1 = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_panel1 = wx.Panel(
            self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        # WARNING: wxPython code generation isn't supported for this widget yet.
        self.m_scintilla1 = wx.Window(self.m_panel1)
        bSizer4.Add(self.m_scintilla1, 1, wx.EXPAND | wx.ALL, 5)

        self.m_panel1.SetSizer(bSizer4)
        self.m_panel1.Layout()
        bSizer4.Fit(self.m_panel1)
        self.m_notebook1.AddPage(self.m_panel1, "Ed", False)
        self.m_panel2 = wx.Panel(
            self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        self.m_customControl1 = PythonSTC(
            self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        # settings from andy
        bSizer5.Add(self.m_customControl1, 1, wx.ALL | wx.EXPAND, 5)

        self.m_panel2.SetSizer(bSizer5)
        self.m_panel2.Layout()
        bSizer5.Fit(self.m_panel2)
        self.m_notebook1.AddPage(self.m_panel2, "andycustom", True)
        self.m_panel3 = wx.Panel(
            self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        self.m_notebook1.AddPage(self.m_panel3, "a page", False)

        bSizer2.Add(self.m_notebook1, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer2)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass


###########################################################################
## Class MyFrame3
###########################################################################


class MyFrame3(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="AUI Andy Demo",
            pos=wx.DefaultPosition,
            size=wx.Size(535, 348),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow(self)

        self.m_panel6 = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        self.m_mgr.AddPane(
            self.m_panel6,
            wx.aui.AuiPaneInfo()
            .Left()
            .Caption("Tools")
            .MaximizeButton(False)
            .MinimizeButton(False)
            .PinButton(True)
            .Dock()
            .Resizable()
            .FloatingSize(wx.Size(116, 154))
            .DockFixed(False)
            .Row(1)
            .BestSize(wx.Size(100, -1)),
        )

        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        self.m_button3 = wx.Button(
            self.m_panel6, wx.ID_ANY, "Import", wx.DefaultPosition, wx.DefaultSize, 0
        )
        bSizer3.Add(self.m_button3, 0, wx.ALL | wx.EXPAND, 5)

        self.m_button4 = wx.Button(
            self.m_panel6, wx.ID_ANY, "Say", wx.DefaultPosition, wx.DefaultSize, 0
        )
        bSizer3.Add(self.m_button4, 0, wx.ALL | wx.EXPAND, 5)

        self.m_panel6.SetSizer(bSizer3)
        self.m_panel6.Layout()
        bSizer3.Fit(self.m_panel6)
        self.m_textCtrl1 = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE
        )
        self.m_mgr.AddPane(
            self.m_textCtrl1,
            wx.aui.AuiPaneInfo()
            .Left()
            .CaptionVisible(False)
            .MaximizeButton(False)
            .MinimizeButton(False)
            .PinButton(True)
            .Dock()
            .Resizable()
            .FloatingSize(wx.DefaultSize)
            .DockFixed(False)
            .CentrePane(),
        )

        self.m_menubar2 = wx.MenuBar(0)
        self.m_menu4 = wx.Menu()
        self.m_menuItem6 = wx.MenuItem(
            self.m_menu4, wx.ID_ANY, "Hi", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu4.AppendItem(self.m_menuItem6)

        self.m_menubar2.Append(self.m_menu4, "MyMenu")

        self.SetMenuBar(self.m_menubar2)

        self.m_mgr.Update()
        self.Centre(wx.BOTH)

        # Connect Events
        self.m_button3.Bind(wx.EVT_BUTTON, self.OnButton1)
        self.m_button4.Bind(wx.EVT_BUTTON, self.OnSay)
        self.Bind(wx.EVT_MENU, self.OnHi, id=self.m_menuItem6.GetId())

    def __del__(self):
        self.m_mgr.UnInit()

        # Virtual event handlers, overide them in your derived class

    def OnButton1(self, event):
        event.Skip()

    def OnSay(self, event):
        event.Skip()

    def OnHi(self, event):
        event.Skip()
