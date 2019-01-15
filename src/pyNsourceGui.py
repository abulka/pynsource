"""
PyNSource GUI
-------------

(c) Andy Bulka
www.andypatterns.com

LICENSE: GPL 3

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx
import wx.lib.ogl as ogl

import os, stat
from common.messages import *

APP_VERSION = 1.70
WINDOW_SIZE = (1024, 768)
MULTI_TAB_GUI = True
USE_SIZER = False
ALLOW_INSERT_IMAGE_AND_COMMENT_COMMANDS = True

# if 'wxMac' in wx.PlatformInfo:
#     MULTI_TAB_GUI = False

from gui.coord_utils import setpos, getpos
from gui.uml_canvas import UmlCanvas
from gui.wx_log import Log
from ascii_uml.layout_ascii import model_to_ascii_builder

from common.architecture_support import *
from app.app import App
import wx.lib.mixins.inspection  # Ctrl-Alt-I
import wx.html as html


class MainApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        self.log = Log()
        self.working = False
        wx.InitAllImageHandlers()
        self.andyapptitle = "PyNsource GUI - Python Code into UML"

        self.frame = wx.Frame(
            None,
            -1,
            self.andyapptitle,
            pos=(50, 50),
            size=(0, 0),
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.DEFAULT_FRAME_STYLE,
        )
        self.frame.CreateStatusBar()

        # ANDY HACK SECTION - STOP BUILDING THE REST OF THE UI AND SHOW THE FRAME NOW!
        # self.frame.SetPosition((40, 40))
        # self.frame.SetSize((400, 400))
        # self.frame.Show()
        # self.OnHelp(None)  # attempt to trigger help window instantly - works!  And mouse scrolling works.
        # return True
        # END HACK SECTION

        if MULTI_TAB_GUI:

            # self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
            sizer = wx.BoxSizer(wx.VERTICAL)
            self.notebook = wx.Notebook(
                self.frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0
            )

            # Page 0
            self.umlcanvas = UmlCanvas(self.notebook, Log(), self.frame)
            self.umlcanvas.SetScrollRate(5, 5)
            self.notebook.AddPage(self.umlcanvas, "UML", True)

            # Page 1
            self.asciiart = wx.ScrolledWindow(
                self.notebook,
                wx.ID_ANY,
                wx.DefaultPosition,
                wx.DefaultSize,
                wx.HSCROLL | wx.VSCROLL,
            )
            self.asciiart.SetScrollRate(5, 5)
            asciiart_sizer = wx.BoxSizer(wx.VERTICAL)

            # txt = u"Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, \n" * 10
            # self.multiText = wx.StaticText(self.asciiart, wx.ID_ANY, txt, wx.DefaultPosition, wx.DefaultSize, 0)
            # self.multiText.Wrap(600)
            # asciiart_sizer.Add(self.multiText, 1, wx.ALL, 0)

            self.multiText = wx.TextCtrl(
                self.asciiart, wx.ID_ANY, ASCII_UML_HELP_MSG, style=wx.TE_MULTILINE | wx.HSCROLL
            )
            self.multiText.SetFont(
                wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
            )  # see http://www.wxpython.org/docs/api/wx.Font-class.html for more fonts
            asciiart_sizer.Add(self.multiText, 1, wx.EXPAND | wx.ALL, 0)
            self.asciiart.SetSizer(asciiart_sizer)
            self.asciiart.Layout()
            asciiart_sizer.Fit(self.asciiart)
            self.notebook.AddPage(self.asciiart, "Ascii Art", True)

            sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 0)
            self.frame.SetSizer(sizer)
            self.frame.Layout()
            self.frame.Centre(wx.BOTH)
            # self.frame.Show()
            self.notebook.ChangeSelection(0)

            # TODO - investgate re-enabling some of these?
            # self.multiText.Bind( wx.EVT_CHAR, self.onKeyChar_Ascii_Text_window)
            # self.multiText.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom_ascii)
            # self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabPageChanged)

        else:
            self.notebook = None

            self.panel_one = wx.Panel(self.frame, -1)
            self.umlcanvas = UmlCanvas(self.panel_one, Log(), self.frame)
            #
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.umlcanvas, 1, wx.EXPAND)
            self.panel_one.SetSizer(sizer)

            self.panel_two = self.asciiart = wx.Panel(self.frame, -1)
            self.multiText = wx.TextCtrl(
                self.panel_two, -1, ASCII_UML_HELP_MSG, style=wx.TE_MULTILINE | wx.HSCROLL
            )
            self.multiText.SetFont(
                wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
            )  # see http://www.wxpython.org/docs/api/wx.Font-class.html for more fonts
            self.multiText.Bind(wx.EVT_CHAR, self.onKeyChar_Ascii_Text_window)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.multiText, 1, wx.EXPAND)
            self.panel_two.SetSizer(sizer)

            self.panel_two.Hide()

            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(self.panel_one, 1, wx.EXPAND)
            self.sizer.Add(self.panel_two, 1, wx.EXPAND)
            self.frame.SetSizer(self.sizer)

        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.

        # Set the frame to a good size for showing stuff
        self.frame.SetSize(WINDOW_SIZE)
        self.umlcanvas.SetFocus()
        self.SetTopWindow(self.frame)

        self.frame.Show(
            True
        )  # in wxpython2.8 this causes umlcanvas to grow too, but not in wxpython3 - till much later
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        self.popupmenu = None
        self.umlcanvas.Bind(
            wx.EVT_RIGHT_DOWN, self.OnRightButtonMenu
        )  # WARNING: takes over all righclick events - need to event.skip() to let through things to UmlShapeHandler
        self.Bind(wx.EVT_SIZE, self.OnResizeFrame)

        self.umlcanvas.InitSizeAndObjs()  # Now that frame is visible and calculated, there should be sensible world coords to use

        self.InitConfig()

        class Context(object):
            """ Everything everybody needs to know """

            pass

        context = Context()
        # init the context
        context.wxapp = self
        context.config = self.config
        context.umlcanvas = self.umlcanvas
        context.displaymodel = self.umlcanvas.displaymodel
        context.snapshot_mgr = self.umlcanvas.snapshot_mgr
        context.coordmapper = self.umlcanvas.coordmapper
        context.layouter = self.umlcanvas.layouter
        context.overlap_remover = self.umlcanvas.overlap_remover
        context.frame = self.frame
        if MULTI_TAB_GUI:
            context.multiText = self.multiText
            context.asciiart = self.asciiart
        else:
            context.multiText = None
            context.asciiart = None

        # App knows about everyone.
        # Everyone (ring classes) should be an adapter
        # but not strictly necessary unless you want an extra level
        # of indirection and separation or don't want to constantly
        # edit the ring classes to match what the app (and other ring
        # objects) expect - edit an adapter instead.
        self.app = App(context)
        self.app.Boot()

        self.InitMenus()
        self.PostOglViewSwitch()  # ensure key bindings kick in under linux

        self.frame.CenterOnScreen()

        # self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)  # start up non-minimised when packaged - doesn't work
        # self.frame.Iconize(False) # start up non-minimised when packaged
        # if self.frame.IsIconized():
        #     wx.MessageBox("iconized?")
        # wx.CallAfter(self.minimized_on_mac_problem)

        wx.CallAfter(
            self.app.run.CmdBootStrap
        )  # doesn't make a difference calling this via CallAfter

        # wx.lib.inspection.InspectionTool().Show()

        return True

    # def minimized_on_mac_problem(self):
    #     self.frame.Iconize(False) # start up non-minimised when packaged
    #     if self.frame.IsIconized():
    #         wx.MessageBox("iconized?")
    #     self.frame.Show()
    #
    # def OnActivate(self, event):
    #     print "OnActivate"
    #     if event.GetActive():
    #         self.frame.Raise()
    #     event.Skip()

    def InitConfig(self):
        config_dir = os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), PYNSOURCE_CONFIG_DIR)
        try:
            os.makedirs(config_dir)
        except OSError:
            pass
        self.user_config_file = os.path.join(config_dir, PYNSOURCE_CONFIG_FILE)
        # print "Pynsource config file", self.user_config_file

        from configobj import ConfigObj  # easy_install configobj

        self.config = ConfigObj(
            self.user_config_file
        )  # doco at http://www.voidspace.org.uk/python/configobj.html
        # print self.config
        self.config["keyword1"] = 100
        self.config["keyword2"] = "hi there"
        self.config.write()

    def OnResizeFrame(self, event):  # ANDY  interesting - GetVirtualSize grows when resize frame
        if event.EventObject == self.umlcanvas:

            # Proportionally constrained resize.  Nice trick from http://stackoverflow.com/questions/6005960/resizing-a-wxpython-window
            # hsize = event.GetSize()[0] * 0.75
            # self.frame.SetSizeHints(minW=-1, minH=hsize, maxH=hsize)
            # self.frame.SetTitle(str(event.GetSize()))

            self.umlcanvas.canvas_resizer.frame_calibration()

        event.Skip()

    def OnWheelZoom_ascii(self, event):
        # Since our binding of wx.EVT_MOUSEWHEEL to here takes over all wheel events
        # we have to manually do the normal test scrolling.  This event can't propogate via event.skip()
        #
        # The native widgets handle the low level
        # events (or not) their own way and wx makes no guarantees about behaviors
        # when intercepting them yourself.
        # --
        # Robin Dunn

        # print "MOUSEWHEEEL self.working=", self.working
        if self.working:
            return
        self.working = True

        # print event.ShouldPropagate(), dir(event)

        controlDown = event.CmdDown()
        if controlDown:
            font = self.multiText.GetFont()

            if event.GetWheelRotation() < 0:
                newfontsize = font.GetPointSize() - 1
            else:
                newfontsize = font.GetPointSize() + 1

            if newfontsize > 0 and newfontsize < 100:
                self.multiText.SetFont(wx.Font(newfontsize, wx.MODERN, wx.NORMAL, wx.NORMAL, False))
        else:
            if event.GetWheelRotation() < 0:
                self.multiText.ScrollLines(4)
            else:
                self.multiText.ScrollLines(-4)

        self.working = False

        # self.frame.GetEventHandler().ProcessEvent(event)
        # wx.PostEvent(self.frame, event)

    def onKeyChar_Ascii_Text_window(self, event):
        # See good tutorial http://www.blog.pythonlibrary.org/2009/08/29/wxpython-catching-key-and-char-events/
        keycode = event.GetKeyCode()
        controlDown = event.CmdDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        # print keycode

        if controlDown and keycode == 1:  # CTRL-A
            self.multiText.SelectAll()

        event.Skip()

    def OnDumpUmlWorkspace(self, event):
        self.app.run.CmdDumpUmlWorkspace()

    def OnSaveGraphToConsole(self, event):
        self.app.run.CmdFileSaveWorkspaceToConsole()

    def OnSaveGraph(self, event):
        self.app.run.CmdFileSaveWorkspace()

    def OnLoadGraphFromText(self, event):
        self.app.run.CmdFileLoadWorkspaceFromQuickPrompt()

    def OnLoadGraph(self, event):
        self.app.run.CmdFileLoadWorkspaceViaDialog()

    def OnLoadGraphSample(self, event):
        self.app.run.CmdFileLoadWorkspaceSampleViaPickList()  # CmdFileLoadWorkspaceSampleViaDialog()

        # phoenix hack to get things to appear
        # self.app.run.CmdRefreshUmlWindow()
        # self.umlcanvas.mega_refresh()

    def set_app_title(self, title):
        self.frame.SetTitle(self.andyapptitle + " - " + title)

    def OnTabPageChanged(self, event):
        if event.GetSelection() == 0:  # ogl
            self.PostOglViewSwitch()
        elif event.GetSelection() == 1:  # ascii art
            self.RefreshAsciiUmlTab()
            self.PostAsciiViewSwitch()
        event.Skip()

    def RefreshAsciiUmlTab(self):
        self.model_to_ascii()

    def PostAsciiViewSwitch(self):
        self.menuBar.EnableTop(2, False)  # disable layout menu
        wx.CallAfter(self.multiText.SetFocus)
        wx.CallAfter(self.multiText.SetInsertionPoint, 0)

    def PostOglViewSwitch(self):
        wx.CallAfter(self.umlcanvas.SetFocus)
        self.menuBar.EnableTop(2, True)  # enable layout menu

    def InitMenus(self):
        menuBar = wx.MenuBar()
        self.menuBar = menuBar
        menu1 = wx.Menu()
        menu2 = wx.Menu()
        menu3 = wx.Menu()
        menu3sub = wx.Menu()
        menu4 = wx.Menu()
        menu5 = wx.Menu()
        menu5sub = wx.Menu()

        self.next_menu_id = wx.NewIdRef()  # was wx.NewId()

        def Add(menu, name, shortcut=None, func=None, func_update=None):
            name_ori = name
            if shortcut:
                name = "%s\t%s" % (name, shortcut)
            id = self.next_menu_id

            # Mac tweak, see http://wiki.wxpython.org/Optimizing%20for%20Mac%20OS%20X
            if "wxMac" in wx.PlatformInfo and name == "&About...":
                id = wx.ID_ABOUT

            menu_item = menu.Append(id, name, name_ori)
            self.Bind(wx.EVT_MENU, func, id=id)
            if func_update:
                self.Bind(wx.EVT_UPDATE_UI, func_update, id=id)

            self.next_menu_id = wx.NewIdRef()  # was wx.NewId()
            return menu_item

        def AddSubMenu(menu, submenu, s):
            menu.AppendSubMenu(submenu, s)

        Add(menu1, "&New", "Ctrl-N", self.FileNew)
        Add(menu1, "&Open...", "Ctrl-O", self.OnLoadGraph)
        Add(menu1, "Open Sample &Uml...", "Ctrl-U", self.OnLoadGraphSample)
        Add(menu1, "&Save As...", "Ctrl-S", self.OnSaveGraph)
        menu1.AppendSeparator()
        Add(menu1, "&Import Python Code...", "Ctrl-I", self.OnFileImport)

        # New way of wiring things up - see https://wxpython.org/blog/avoiding-window-ids/index.html
        self.item_python3_mode = menu1.AppendCheckItem(
            wx.ID_ANY, "Python 3 mode", help="Assume Python syntax 2/3"
        )
        self.Bind(wx.EVT_MENU, self.OnPythonMode, self.item_python3_mode)
        self.item_python3_mode.Check()

        menu1.AppendSeparator()
        Add(menu1, "&Print / Preview...", "Ctrl-P", self.FilePrint)
        menu1.AppendSeparator()
        Add(menu1, "E&xit", "Alt-X", self.OnButton)

        Add(menu2, "&Add Class...", "Ctrl-A", self.OnInsertClass)
        if ALLOW_INSERT_IMAGE_AND_COMMENT_COMMANDS:
            Add(menu2, "&Insert Image...", "Ctrl-M", self.OnInsertImage)
            Add(menu2, "&Insert Comment...", "Shift-I", self.OnInsertComment)
        menu_item_delete_class = Add(
            menu2, "&Delete", "Del", self.OnDeleteNode, self.OnDeleteNode_update
        )
        menu_item_delete_class.Enable(
            True
        )  # demo one way to enable/disable.  But better to do via _update function
        Add(
            menu2,
            "&Edit Class Properties...",
            "F2",
            self.OnEditProperties,
            self.OnEditProperties_update,
        )
        menu2.AppendSeparator()
        Add(menu2, "&Redraw Screen", "Ctrl-R", self.OnRefreshUmlWindow)

        Add(menu5, "&Toggle Ascii UML", "Ctrl-J", self.OnViewToggleAscii)
        menu5.AppendSeparator()
        Add(menu5, "Colour &Sibling Subclasses", "Ctrl-F", self.OnColourSiblings)
        Add(menu5, "&Default Colours", "Ctrl-D", self.OnCycleColoursDefault)
        menu5.AppendSeparator()

        Add(menu5sub, "&Change Node Colour", "Ctrl-G", self.OnCycleColours)
        Add(
            menu5sub,
            "Change &Sibling Subclass Colour Scheme",
            "Ctrl-F",
            self.OnColourSiblingsRandom,
        )
        AddSubMenu(menu5, menu5sub, "Advanced")

        Add(menu3, "&Layout UML", "Ctrl-L", self.OnLayout)
        Add(menu3, "&Layout UML Optimally (slower)", "Ctrl-B", self.OnDeepLayout)
        menu3.AppendSeparator()
        Add(menu3, "&Expand Layout", "Ctrl-.", self.app.run.CmdLayoutExpand)
        Add(menu3, "&Contract Layout", "Ctrl-,", self.app.run.CmdLayoutContract)
        menu3.AppendSeparator()
        Add(menu3, "&Remember Layout", "Ctrl-1", self.OnRememberLayout2)
        Add(menu3, "&Restore Layout", "Ctrl-2", self.OnRestoreLayout2)

        Add(menu4, "&Help...", "F1", self.OnHelp)
        Add(menu4, "&Visit PyNSource Website...", "", self.OnVisitWebsite)
        Add(menu4, "&Check for Updates...", "", self.OnCheckForUpdates)
        Add(menu4, "&Report Bug...", "", self.OnReportBug)
        if not "wxMac" in wx.PlatformInfo:
            menu4.AppendSeparator()
        helpID = Add(menu4, "&About...", "", self.OnAbout).GetId()

        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Edit")
        menuBar.Append(menu3, "&Layout")

        # Super Stoopid Hack (TM) is to just name the menu "View " instead of "View"
        # https://github.com/itsayellow/marcam/issues/52
        # https://github.com/wxWidgets/Phoenix/issues/347
        menuBar.Append(menu5, "&View ")  # the name "View" causes weird mac dock auto items

        menuBar.Append(menu4, "&Help")
        self.frame.SetMenuBar(menuBar)

    def OnPythonMode(self, event):
        print("python 3 syntax mode state now:", self.item_python3_mode.IsChecked())

    def OnRightButtonMenu(self, event):  # Menu
        x, y = event.GetPosition()

        # Since our binding of wx.EVT_RIGHT_DOWN to here takes over all right click events
        # we have to manually figure out if we have clicked on shape
        # then allow natural shape node menu to kick in via UmlShapeHandler (defined above)
        hit_which_shapes = [
            s for s in self.umlcanvas.GetDiagram().GetShapeList() if s.HitTest(x, y)
        ]
        if hit_which_shapes:
            event.Skip()
            return

        self.umlcanvas.focus_canvas()  # bit of accelerator fun, though below menu is not accel.

        if self.popupmenu:
            self.popupmenu.Destroy()  # wx.Menu objects need to be explicitly destroyed (e.g. menu.Destroy()) in this situation. Otherwise, they will rack up the USER Objects count on Windows; eventually crashing a program when USER Objects is maxed out. -- U. Artie Eoff  http://wiki.wxpython.org/index.cgi/PopupMenuOnRightClick
        self.popupmenu = wx.Menu()  # Create a menu

        item = self.popupmenu.Append(wx.ID_ANY, "Add Class...")
        self.frame.Bind(wx.EVT_MENU, self.OnInsertClass, item)
        if ALLOW_INSERT_IMAGE_AND_COMMENT_COMMANDS:
            item = self.popupmenu.Append(wx.ID_ANY, "Add Image...")
            self.frame.Bind(wx.EVT_MENU, self.OnInsertImage, item)
            item = self.popupmenu.Append(wx.ID_ANY, "Add Comment...")
            self.frame.Bind(wx.EVT_MENU, self.OnInsertComment, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "Load Graph from text...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoadGraphFromText, item)

        item = self.popupmenu.Append(wx.ID_ANY, "Dump Graph to console")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraphToConsole, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "Load Graph...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoadGraph, item)

        item = self.popupmenu.Append(wx.ID_ANY, "Save Graph...")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraph, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "DumpUmlWorkspace")
        self.frame.Bind(wx.EVT_MENU, self.OnDumpUmlWorkspace, item)

        self.frame.PopupMenu(self.popupmenu, wx.Point(x, y))

    def OnReportBug(self, event):
        import webbrowser

        # webbrowser.open("http://code.google.com/p/pynsource/issues/list")
        webbrowser.open("https://github.com/abulka/pynsource/issues")

    def OnRememberLayout1(self, event):
        self.umlcanvas.CmdRememberLayout1()

    def OnRememberLayout2(self, event):
        self.umlcanvas.CmdRememberLayout2()

    def OnRestoreLayout1(self, event):
        self.umlcanvas.CmdRestoreLayout1()
        self.frame.Layout()  # needed when running phoenix

    def OnRestoreLayout2(self, event):
        self.umlcanvas.CmdRestoreLayout2()
        self.frame.Layout()  # needed when running phoenix

    def OnCycleColours(self, event):
        self.app.run.CmdCycleColours()

    def OnCycleColoursDefault(self, event):
        self.app.run.CmdCycleColours(colour=wx.Brush("WHEAT", wx.SOLID))

    def OnColourSiblings(self, event):
        self.app.run.CmdColourSiblings()

    def OnColourSiblingsRandom(self, event):
        self.app.run.CmdColourSiblings(color_range_offset=True)

    def OnFileImport(self, event):
        mode = 3 if self.item_python3_mode.IsChecked() else 2
        self.app.run.CmdFileImportViaDialog(mode=mode)

    def OnViewToggleAscii(self, event):
        if MULTI_TAB_GUI:
            if self.viewing_uml_tab:
                self.notebook.SetSelection(1)
                self.model_to_ascii()
                self.PostAsciiViewSwitch()
            else:
                self.switch_to_ogl_uml_view()
        else:
            if self.panel_one.IsShown():
                self.panel_one.Hide()
                self.panel_two.Show()
                self.model_to_ascii()
                self.PostAsciiViewSwitch()
                self.frame.Layout()
            else:
                self.switch_to_ogl_uml_view()

    def switch_to_ogl_uml_view(self):
        if MULTI_TAB_GUI:
            self.notebook.SetSelection(0)
            self.PostOglViewSwitch()
        else:
            self.panel_one.Show()
            self.panel_two.Hide()
            self.PostOglViewSwitch()
            self.frame.Layout()

    def model_to_ascii(self):
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        m = model_to_ascii_builder()
        try:
            wx.SafeYield()
            s = m.main(self.umlcanvas.displaymodel.graph)
            self.multiText.SetValue(str(s))
            if str(s).strip() == "":
                self.multiText.SetValue(ASCII_UML_HELP_MSG)
            self.multiText.ShowPosition(0)
        finally:
            wx.EndBusyCursor()

    def FileNew(self, event):
        self.app.run.CmdFileNew()

    def FilePrint(self, event):

        from common.printframework import MyPrintout

        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_LETTER)

        self.box = wx.BoxSizer(wx.VERTICAL)
        # self.log.WriteText("OnPrintPreview\n")
        printout = MyPrintout(self.umlcanvas, self.log)
        printout2 = MyPrintout(self.umlcanvas, self.log)
        self.preview = wx.PrintPreview(printout, printout2, self.printData)
        if not self.preview.IsOk():
            self.log.WriteText("Houston, we have a problem...\n")
            return

        frame = wx.PreviewFrame(self.preview, self.frame, "This is a print preview")

        frame.Initialize()
        frame.SetPosition(self.frame.GetPosition())
        frame.SetSize(self.frame.GetSize())
        frame.Show(True)

    def OnAbout(self, event):
        # self.MessageBox(ABOUT_MSG.strip() %  APP_VERSION)

        from wx.lib.wordwrap import wordwrap
        from wx.adv import AboutDialogInfo, AboutBox

        info = AboutDialogInfo()
        # info.SetIcon(wx.Icon('Images\\img_uml01.png', wx.BITMAP_TYPE_PNG))
        info.SetName(ABOUT_APPNAME)
        info.SetVersion(str(APP_VERSION))
        info.SetDescription(ABOUT_MSG)
        # info.Description = wordwrap(ABOUT_MSG, 350, wx.ClientDC(self.frame))
        info.SetCopyright(ABOUT_AUTHOR)
        # info.SetWebSite(WEB_PYNSOURCE_HOME_URL)
        info.WebSite = (WEB_PYNSOURCE_HOME_URL, "Home Page")
        info.SetLicence(ABOUT_LICENSE)
        # info.AddDeveloper(ABOUT_AUTHOR)
        # info.AddDocWriter(ABOUT_FEATURES)
        # info.AddArtist('Blah')
        # info.AddTranslator('Blah')

        AboutBox(info)

    def OnVisitWebsite(self, event):
        import webbrowser

        webbrowser.open(WEB_PYNSOURCE_HOME_URL)

    def OnCheckForUpdates(self, event):
        import urllib.request, urllib.error, urllib.parse

        s = urllib.request.urlopen(WEB_VERSION_CHECK_URL).read().decode("utf-8")
        s = s.replace("\r", "")
        info = eval(s)
        ver = info["latest_version"]

        if ver > APP_VERSION:
            msg = WEB_UPDATE_MSG % (ver, info["latest_announcement"].strip())
            retCode = wx.MessageBox(
                msg.strip(), "Update Check", wx.YES_NO | wx.ICON_QUESTION
            )  # MessageBox simpler than MessageDialog
            if retCode == wx.YES:
                import webbrowser

                webbrowser.open(info["download_url"])
        elif ver < APP_VERSION:
            self.MessageBox(
                f"You seem to have a pre-release version {APP_VERSION} - congratulations!  Stable version is {ver}"
            )
        else:
            self.MessageBox("You already have the latest version:  %s" % APP_VERSION)

    # def OnHelpAlt(self, event):  # not used
    #     """manually build a frame with inner html window, no sizer involved"""
    #     class MyHtmlFrame(wx.Frame):
    #         def __init__(self, parent, title):
    #             super(MyHtmlFrame, self).__init__(parent, title=title)
    #             html = wx.html.HtmlWindow(parent=self)
    #             if "gtk2" in wx.PlatformInfo:
    #                 html.SetStandardFonts()
    #             wx.CallAfter(html.LoadPage, os.path.join("dialogs/HelpWindow.html"))
    #     frm = MyHtmlFrame(parent=self.frame, title="Simple HTML Browser")
    #     frm.Show()

    def OnHelp(self, event):
        """Uses a wxformbuilder frame with inner html window"""
        from dialogs.HelpWindow import HelpWindow

        class Help(HelpWindow):
            def __init__(self, parent):
                HelpWindow.__init__(self, parent)

                # CMD-W to close Frame by attaching the key bind event to accellerator table
                randomId = wx.NewIdRef()  # was wx.NewId()
                self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=randomId)
                accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("W"), randomId)])
                self.SetAcceleratorTable(accel_tbl)

                self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)  # Close on ESC

            def OnKeyUP(self, event):  # Close on ESC
                keyCode = event.GetKeyCode()
                if keyCode == wx.WXK_ESCAPE:
                    self.Close()
                event.Skip()

            def OnCancelClick(self, event):
                self.Close()

            def OnCloseMe(self, event):
                self.Close(True)

            def OnCloseWindow(self, event):
                self.Destroy()

        f = Help(parent=self.frame)

        if os.path.exists("../Resources"):
            dir = "../Resources"
        else:
            dir = "dialogs/"
        f.m_htmlWin1.LoadPage(os.path.join(dir, "HelpWindow.html"))
        f.Show(True)

    def Enable_if_node_selected(self, event):
        selected = [s for s in self.umlcanvas.GetDiagram().GetShapeList() if s.Selected()]
        event.Enable(len(selected) > 0 and self.viewing_uml_tab)

    @property
    def viewing_uml_tab(self):
        if MULTI_TAB_GUI:
            if self.notebook:
                return self.notebook.GetSelection() == 0
            else:
                return False
        else:
            return self.panel_one.IsShown()

    def OnDeleteNode(self, event):
        self.app.run.CmdNodeDeleteSelected()

    def OnDeleteNode_update(self, event):
        self.Enable_if_node_selected(event)

    def OnInsertComment(self, event):
        self.app.run.CmdInsertComment()

    def OnInsertImage(self, event):
        self.app.run.CmdInsertImage()

    def OnInsertClass(self, event):
        self.app.run.CmdInsertUmlClass()

    def OnEditProperties(self, event):
        from gui.node_edit_multi_purpose import node_edit_multi_purpose

        # not sure why we are looping cos currently cannot select more than one shape
        for shape in self.umlcanvas.GetDiagram().GetShapeList():
            if shape.Selected():
                node_edit_multi_purpose(shape, self.app)
                break

    def OnEditProperties_update(self, event):
        self.Enable_if_node_selected(event)

    def OnLayout(self, event):
        self.app.run.CmdLayout()

    def OnDeepLayout(self, event):
        self.app.run.CmdDeepLayout()

    def OnRefreshUmlWindow(self, event):
        self.app.run.CmdRefreshUmlWindow()

    def MessageBox(self, msg):
        dlg = wx.MessageDialog(self.frame, msg, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnButton(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.umlcanvas.ShutdownDemo()
        evt.Skip()


def main():
    application = MainApp(0)
    # application = MainApp(redirect=True, filename='/tmp/pynsource.log')  # to view what's going on

    application.MainLoop()


if __name__ == "__main__":

    # Sanity check for paths, ensure there is not any .. and other relative crud in
    # our path.  You only need that stuff when running a module as a standalone.
    # in which case prefix such appends with if __name__ == '__main__':
    # Otherwise everything should be assumed to run from trunk/src/ as the root
    #
    # import sys, pprint
    # pprint.pprint(sys.path)

    main()
