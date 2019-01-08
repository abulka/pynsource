# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Mar 22 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.aui
from fbpyn1_scintilla import PythonSTC
import wx.lib.ogl as ogl

###########################################################################
## Class FramePyIdea_gen
###########################################################################


class FramePyIdea_gen(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="PyIdea UML",
            pos=wx.DefaultPosition,
            size=wx.Size(500, 300),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow(self)

        self.m_code = PythonSTC(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.WANTS_CHARS)
        self.m_mgr.AddPane(
            self.m_code,
            wx.aui.AuiPaneInfo()
            .Name("pane_code")
            .Right()
            .Caption("Source Code")
            .MaximizeButton(False)
            .MinimizeButton(False)
            .PinButton(True)
            .Dock()
            .Resizable()
            .FloatingSize(wx.DefaultSize)
            .DockFixed(False),
        )

        self.m_menubar4 = wx.MenuBar(0)
        self.m_menu2 = wx.Menu()
        self.m_menuItem15 = wx.MenuItem(
            self.m_menu2,
            wx.ID_ANY,
            "Import Python Source..." + "\t" + "Ctrl+I",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu2.AppendItem(self.m_menuItem15)

        self.m_menu2.AppendSeparator()

        self.m_menuItem16 = wx.MenuItem(
            self.m_menu2, wx.ID_ANY, "New" + "\t" + "Ctrl+N", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu2.AppendItem(self.m_menuItem16)

        self.m_menuItem17 = wx.MenuItem(
            self.m_menu2, wx.ID_ANY, "Open..." + "\t" + "Ctrl-O", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu2.AppendItem(self.m_menuItem17)

        self.m_menuItem18 = wx.MenuItem(
            self.m_menu2, wx.ID_ANY, "Save" + "\t" + "Ctrl-S", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu2.AppendItem(self.m_menuItem18)

        self.m_menuItem21 = wx.MenuItem(
            self.m_menu2, wx.ID_ANY, "Save As...", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu2.AppendItem(self.m_menuItem21)

        self.m_menu2.AppendSeparator()

        self.m_menuItem20 = wx.MenuItem(
            self.m_menu2,
            wx.ID_ANY,
            "Print / Print Preview..." + "\t" + "Ctrl-P",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu2.AppendItem(self.m_menuItem20)

        self.m_menu2.AppendSeparator()

        self.m_menuItem19 = wx.MenuItem(
            self.m_menu2, wx.ID_ANY, "Exit" + "\t" + "Alt+F4", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu2.AppendItem(self.m_menuItem19)

        self.m_menubar4.Append(self.m_menu2, "File")

        self.m_menu6 = wx.Menu()
        self.m_menuItem26 = wx.MenuItem(
            self.m_menu6,
            wx.ID_ANY,
            "Add Class..." + "\t" + "Ctrl+Ins",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu6.AppendItem(self.m_menuItem26)

        self.m_menuItem14 = wx.MenuItem(
            self.m_menu6,
            wx.ID_ANY,
            "Delete Class" + "\t" + "Ctrl+Del",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu6.AppendItem(self.m_menuItem14)

        self.m_menu6.AppendSeparator()

        self.m_menuItem29 = wx.MenuItem(
            self.m_menu6,
            wx.ID_ANY,
            "Class Properties..." + "\t" + "Ctrl+T",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu6.AppendItem(self.m_menuItem29)

        self.m_menuItem28 = wx.MenuItem(
            self.m_menu6,
            wx.ID_ANY,
            "Class Source Code..." + "\t" + "Ctrl+E",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu6.AppendItem(self.m_menuItem28)

        self.m_menubar4.Append(self.m_menu6, "Edit")

        self.m_menu7 = wx.Menu()
        self.m_menuItem81 = wx.MenuItem(
            self.m_menu7, wx.ID_ANY, "Layout" + "\t" + "Ctrl+L", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu7.AppendItem(self.m_menuItem81)

        self.m_menuItem35 = wx.MenuItem(
            self.m_menu7, wx.ID_ANY, "Layout Optimal (slower)", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu7.AppendItem(self.m_menuItem35)

        self.m_menu7.AppendSeparator()

        self.m_menuItem31 = wx.MenuItem(
            self.m_menu7,
            wx.ID_ANY,
            "Decrease Node Spread" + "\t" + "Ctrl+1",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu7.AppendItem(self.m_menuItem31)

        self.m_menuItem30 = wx.MenuItem(
            self.m_menu7,
            wx.ID_ANY,
            "Increase Node Spread" + "\t" + "Ctrl+2",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu7.AppendItem(self.m_menuItem30)

        self.m_menu7.AppendSeparator()

        self.m_menuItem24 = wx.MenuItem(
            self.m_menu7, wx.ID_ANY, "UML", wx.EmptyString, wx.ITEM_CHECK
        )
        self.m_menu7.AppendItem(self.m_menuItem24)
        self.m_menuItem24.Enable(False)
        self.m_menuItem24.Check(True)

        self.m_menuItem22 = wx.MenuItem(
            self.m_menu7, wx.ID_ANY, "Ascii Art Uml", wx.EmptyString, wx.ITEM_CHECK
        )
        self.m_menu7.AppendItem(self.m_menuItem22)

        self.m_menuItem23 = wx.MenuItem(
            self.m_menu7, wx.ID_ANY, "yUml", wx.EmptyString, wx.ITEM_CHECK
        )
        self.m_menu7.AppendItem(self.m_menuItem23)

        self.m_menu7.AppendSeparator()

        self.m_menuItem7 = wx.MenuItem(
            self.m_menu7,
            wx.ID_ANY,
            "Redraw Screen" + "\t" + "Ctrl+R",
            wx.EmptyString,
            wx.ITEM_NORMAL,
        )
        self.m_menu7.AppendItem(self.m_menuItem7)

        self.m_menubar4.Append(self.m_menu7, "View")

        self.m_menu8 = wx.Menu()
        self.m_menuItem9 = wx.MenuItem(
            self.m_menu8, wx.ID_ANY, "Help..." + "\t" + "F1", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu8.AppendItem(self.m_menuItem9)

        self.m_menuItem11 = wx.MenuItem(
            self.m_menu8, wx.ID_ANY, "Visit PyNSource Website...", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu8.AppendItem(self.m_menuItem11)

        self.m_menu8.AppendSeparator()

        self.m_menuItem12 = wx.MenuItem(
            self.m_menu8, wx.ID_ANY, "Check for Updates...", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu8.AppendItem(self.m_menuItem12)

        self.m_menuItem13 = wx.MenuItem(
            self.m_menu8, wx.ID_ANY, "About...", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu8.AppendItem(self.m_menuItem13)

        self.m_menubar4.Append(self.m_menu8, "Help")

        self.m_menu5 = wx.Menu()
        self.m_menuItem8 = wx.MenuItem(
            self.m_menu5, wx.ID_ANY, "Show Pane", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu5.AppendItem(self.m_menuItem8)

        self.m_menuItem2 = wx.MenuItem(
            self.m_menu5, wx.ID_ANY, "Add Pane", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu5.AppendItem(self.m_menuItem2)

        self.m_menuItem6 = wx.MenuItem(
            self.m_menu5, wx.ID_ANY, "Add Pane (float)", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu5.AppendItem(self.m_menuItem6)

        self.m_menuItem3 = wx.MenuItem(
            self.m_menu5, wx.ID_ANY, "Fold1", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu5.AppendItem(self.m_menuItem3)

        self.m_menuItem4 = wx.MenuItem(
            self.m_menu5, wx.ID_ANY, "Fold All", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu5.AppendItem(self.m_menuItem4)

        self.m_menuItem5 = wx.MenuItem(
            self.m_menu5, wx.ID_ANY, "Hier", wx.EmptyString, wx.ITEM_NORMAL
        )
        self.m_menu5.AppendItem(self.m_menuItem5)

        self.m_menubar4.Append(self.m_menu5, "Debug")

        self.SetMenuBar(self.m_menubar4)

        self.m_statusBar1 = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)
        self.canvas = ogl.ShapeCanvas(self)
        diagram = ogl.Diagram()
        self.canvas.SetDiagram(diagram)
        diagram.SetCanvas(self.canvas)
        self.m_mgr.AddPane(
            self.canvas,
            wx.aui.AuiPaneInfo()
            .Left()
            .Caption("UML")
            .MaximizeButton(False)
            .MinimizeButton(False)
            .PinButton(True)
            .Dock()
            .Resizable()
            .FloatingSize(wx.DefaultSize)
            .DockFixed(False)
            .CentrePane(),
        )

        self.m_auiToolBar2 = wx.aui.AuiToolBar(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT
        )
        self.m_auiToolBar2.AddTool(
            wx.ID_ANY,
            "sssddddd",
            wx.Bitmap("icons22/kcmscsi.png", wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            "ssss",
            wx.EmptyString,
            None,
        )
        self.m_auiToolBar2.AddTool(
            wx.ID_ANY,
            "tool",
            wx.Bitmap("icons22/kmoon.png", wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            wx.EmptyString,
            wx.EmptyString,
            None,
        )
        self.m_auiToolBar2.AddTool(
            wx.ID_ANY,
            "tool",
            wx.Bitmap("icons22/kalzium.png", wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            wx.EmptyString,
            wx.EmptyString,
            None,
        )
        self.m_auiToolBar2.AddSeparator()
        self.m_auiToolBar2.AddTool(
            wx.ID_ANY,
            "tool",
            wx.Bitmap("icons22/kedit.png", wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            wx.EmptyString,
            wx.EmptyString,
            None,
        )
        self.m_auiToolBar2.AddTool(
            wx.ID_ANY,
            "tool",
            wx.Bitmap("icons22/kcmprocessor.png", wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            wx.EmptyString,
            wx.EmptyString,
            None,
        )
        self.m_auiToolBar2.AddTool(
            wx.ID_ANY,
            "tool",
            wx.Bitmap("icons22/kcmmidi.png", wx.BITMAP_TYPE_ANY),
            wx.NullBitmap,
            wx.ITEM_NORMAL,
            wx.EmptyString,
            wx.EmptyString,
            None,
        )
        self.m_auiToolBar2.Realize()
        self.m_mgr.AddPane(
            self.m_auiToolBar2,
            wx.aui.AuiPaneInfo()
            .Top()
            .CaptionVisible(False)
            .CloseButton(False)
            .MaximizeButton(False)
            .MinimizeButton(False)
            .PinButton(False)
            .PaneBorder(False)
            .Movable(False)
            .Dock()
            .Fixed()
            .DockFixed(False)
            .Floatable(False)
            .Layer(1),
        )

        self.m_mgr.Update()
        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_MENU, self.OnShowPane, id=self.m_menuItem8.GetId())
        self.Bind(wx.EVT_MENU, self.OnAddPane, id=self.m_menuItem2.GetId())
        self.Bind(wx.EVT_MENU, self.OnAddPaneFloat, id=self.m_menuItem6.GetId())
        self.Bind(wx.EVT_MENU, self.OnFold1, id=self.m_menuItem3.GetId())
        self.Bind(wx.EVT_MENU, self.OnFoldAll, id=self.m_menuItem4.GetId())
        self.Bind(wx.EVT_MENU, self.OnHier, id=self.m_menuItem5.GetId())

    def __del__(self):
        self.m_mgr.UnInit()

        # Virtual event handlers, overide them in your derived class

    def OnShowPane(self, event):
        event.Skip()

    def OnAddPane(self, event):
        event.Skip()

    def OnAddPaneFloat(self, event):
        event.Skip()

    def OnFold1(self, event):
        event.Skip()

    def OnFoldAll(self, event):
        event.Skip()

    def OnHier(self, event):
        event.Skip()
