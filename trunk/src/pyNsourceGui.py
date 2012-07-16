"""
PyNSource GUI
-------------

Andy Bulka
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
from messages import *

APP_VERSION = 1.6
WINDOW_SIZE = (1024,768)
MULTI_TAB_GUI = True
USE_SIZER = False

from gui.coord_utils import setpos, getpos
from gui.uml_canvas import UmlCanvas
from gui.wx_log import Log
from gui_imageviewer import ImageViewer

from architecture_support import *
from app.app import App

class MainApp(wx.App):
    def OnInit(self):
        self.log = Log()
        self.working = False
        wx.InitAllImageHandlers()
        self.andyapptitle = 'PyNsource GUI - Python Code into UML'

        self.frame = wx.Frame(None, -1, self.andyapptitle, pos=(50,50), size=(0,0),
                        style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.DEFAULT_FRAME_STYLE)
        self.frame.CreateStatusBar()
        self.InitMenus()

        if MULTI_TAB_GUI:
            self.notebook = wx.Notebook(self.frame, -1)
         
            if USE_SIZER:
                # create the chain of real objects
                panel = wx.Panel(self.notebook, -1)
                self.umlwin = UmlCanvas(panel, Log(), self.frame)
                # add children to sizers and set the sizer to the parent
                sizer = wx.BoxSizer( wx.VERTICAL )
                sizer.Add(self.umlwin, 1, wx.GROW)
                panel.SetSizer(sizer)
            else:
                self.umlwin = UmlCanvas(self.notebook, Log(), self.frame)

            #self.yuml = ImageViewer(self.notebook) # wx.Panel(self.notebook, -1)
            
            self.asciiart = wx.Panel(self.notebook, -1)
    
            if USE_SIZER:
                self.notebook.AddPage(panel, "UML")
            else:
                self.notebook.AddPage(self.umlwin, "UML")
            #self.notebook.AddPage(self.yuml, "yUml")
            self.notebook.AddPage(self.asciiart, "Ascii Art")
    
            # Modify my own page http://www.andypatterns.com/index.php/products/pynsource/asciiart/
            # Some other ideas here http://c2.com/cgi/wiki?UmlAsciiArt 
            self.multiText = wx.TextCtrl(self.asciiart, -1, ASCII_UML_HELP_MSG, style=wx.TE_MULTILINE|wx.HSCROLL)
            bsizer = wx.BoxSizer()
            bsizer.Add(self.multiText, 1, wx.EXPAND)
            self.asciiart.SetSizerAndFit(bsizer)
            self.multiText.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False))   # see http://www.wxpython.org/docs/api/wx.Font-class.html for more fonts
            self.multiText.Bind( wx.EVT_CHAR, self.onKeyChar_Ascii_Text_window)
            self.multiText.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom_ascii)

            self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabPageChanged)
            
        else:
            self.umlwin = UmlCanvas(self.frame, Log(), self.frame)
            
        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.
        
        # Set the frame to a good size for showing stuff
        self.frame.SetSize(WINDOW_SIZE)
        self.umlwin.SetFocus()
        self.SetTopWindow(self.frame)

        self.frame.Show(True)
        wx.EVT_CLOSE(self.frame, self.OnCloseFrame)
        
        self.popupmenu = None
        self.umlwin.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonMenu)  # WARNING: takes over all righclick events - need to event.skip() to let through things to UmlShapeHandler 
        self.Bind(wx.EVT_SIZE, self.OnResizeFrame)

        #self.umlwin.Bind(wx.EVT_SET_FOCUS, self.onFocus)  # attempt at making mousewheel auto scroll the workspace
        #self.frame.Bind(wx.EVT_SET_FOCUS, self.onFocus)   # attempt at making mousewheel auto scroll the workspace
        
        self.InitConfig()

        self.observers = multicast()

        class Context(object):
            """ Everything everybody needs to know """
            pass
        context = Context()
        # init the context
        context.wxapp = self
        context.config = self.config
        context.umlwin = self.umlwin
        context.model = self.umlwin.umlworkspace
        context.snapshot_mgr = self.umlwin.snapshot_mgr
        context.coordmapper = self.umlwin.coordmapper
        context.layouter = self.umlwin.layouter
        context.overlap_remover = self.umlwin.overlap_remover
        context.frame = self.frame
        context.multiText = self.multiText
        context.asciiart = self.asciiart
        
        # App knows about everyone.
        # Everyone (ring classes) should be an adapter
        # but not strictly necessary unless you want an extra level
        # of indirection and separation or don't want to constantly
        # edit the ring classes to match what the app (and other ring
        # objects) expect - edit an adapter instead.
        self.app = App(context)
        #app.Boot()
        
        
        
        wx.CallAfter(self.BootStrap)    # doesn't make a difference calling this via CallAfter
        
        return True
    
    def BootStrap(self):

        def bootstrap01():
            self.frame.SetSize((1024,768))
            self.umlwin.Go(files=[os.path.abspath( __file__ )])
        def bootstrap02():
            self.umlwin.Go(files=[os.path.abspath( "../Research/state chart editor/Editor.py" )])
            self.umlwin.RedrawEverything()
            #self.umlwin.umlworkspace.Dump()
        def bootstrap03():
            self.umlwin.RedrawEverything()  # Allow main frame to resize and thus allow world coords to calibrate before we generate layout coords for loaded graph
            filename = os.path.abspath( "saved uml workspaces/uml05.txt" )
            fp = open(filename, "r")
            s = fp.read()
            fp.close()
            self.LoadGraph(s)
        def bootstrap04():
            self.umlwin.Go(files=[os.path.abspath( "pyNsourceGui.py" )])
            self.umlwin.RedrawEverything()
        def bootstrap05():
            self.umlwin.Go(files=[os.path.abspath("printframework.py"), os.path.abspath("png.py")])
            self.umlwin.RedrawEverything()
        def bootstrap06():
            self.umlwin.Go(files=[os.path.abspath("gui_umlshapes.py")])
            self.umlwin.RedrawEverything()
            
        #print "BootStrap"
        bootstrap03()
        
    #def onFocus(self, event):   # attempt at making mousewheel auto scroll the workspace
    #    self.umlwin.SetFocus()  # attempt at making mousewheel auto scroll the workspace
        
    def InitConfig(self):
        config_dir = os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), PYNSOURCE_CONFIG_DIR)
        try:
            os.makedirs(config_dir)
        except OSError:
            pass        
        self.user_config_file = os.path.join(config_dir, PYNSOURCE_CONFIG_FILE)
        #print "Pynsource config file", self.user_config_file
        
        from configobj import ConfigObj # easy_install configobj
        self.config = ConfigObj(self.user_config_file) # doco at http://www.voidspace.org.uk/python/configobj.html
        #print self.config
        self.config['keyword1'] = 100
        self.config['keyword2'] = "hi there"
        self.config.write()

    def OnResizeFrame (self, event):   # ANDY  interesting - GetVirtualSize grows when resize frame
        if event.EventObject == self.umlwin:
            #print "OnResizeFrame"
            self.umlwin.coordmapper.Recalibrate(self.frame.GetClientSize()) # may need to call self.GetVirtualSize() if scrolled window
            #self.umlwin.coordmapper.Recalibrate(self.umlwin.GetVirtualSize())
        event.Skip()
        
    def OnRightButtonMenu(self, event):   # Menu
        x, y = event.GetPosition()

        # Since our binding of wx.EVT_RIGHT_DOWN to here takes over all right click events
        # we have to manually figure out if we have clicked on shape 
        # then allow natural shape node menu to kick in via UmlShapeHandler (defined above)
        hit_which_shapes = [s for s in self.umlwin.GetDiagram().GetShapeList() if s.HitTest(x,y)]
        if hit_which_shapes:
            event.Skip()
            return
        
        if self.popupmenu:
            self.popupmenu.Destroy()    # wx.Menu objects need to be explicitly destroyed (e.g. menu.Destroy()) in this situation. Otherwise, they will rack up the USER Objects count on Windows; eventually crashing a program when USER Objects is maxed out. -- U. Artie Eoff  http://wiki.wxpython.org/index.cgi/PopupMenuOnRightClick
        self.popupmenu = wx.Menu()     # Create a menu
        
        item = self.popupmenu.Append(wx.NewId(), "Insert Class...")
        self.frame.Bind(wx.EVT_MENU, self.OnInsertClass, item)
        item = self.popupmenu.Append(wx.NewId(), "Insert Image...")
        self.frame.Bind(wx.EVT_MENU, self.OnInsertImage, item)
        item = self.popupmenu.Append(wx.NewId(), "Insert Comment...")
        self.frame.Bind(wx.EVT_MENU, self.OnInsertComment, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.NewId(), "Load Graph from text...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoadGraphFromText, item)
        
        item = self.popupmenu.Append(wx.NewId(), "Dump Graph to console")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraphToConsole, item)
        
        self.popupmenu.AppendSeparator()
        
        item = self.popupmenu.Append(wx.NewId(), "Load Graph...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoadGraph, item)
        
        item = self.popupmenu.Append(wx.NewId(), "Save Graph...")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraph, item)
        
        self.popupmenu.AppendSeparator()
        
        item = self.popupmenu.Append(wx.NewId(), "DumpUmlWorkspace")
        self.frame.Bind(wx.EVT_MENU, self.OnDumpUmlWorkspace, item)
        
        self.frame.PopupMenu(self.popupmenu, wx.Point(x,y))
        
    def OnWheelZoom_ascii(self, event):
        # Since our binding of wx.EVT_MOUSEWHEEL to here takes over all wheel events
        # we have to manually do the normal test scrolling.  This event can't propogate via event.skip()
        #
        #The native widgets handle the low level 
        #events (or not) their own way and wx makes no guarantees about behaviors 
        #when intercepting them yourself. 
        #-- 
        #Robin Dunn 

        if self.working: return
        self.working = True
        
        #print event.ShouldPropagate(), dir(event)
        
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

        #self.frame.GetEventHandler().ProcessEvent(event)
        #wx.PostEvent(self.frame, event)
        
    def onKeyChar_Ascii_Text_window(self, event):
        # See good tutorial http://www.blog.pythonlibrary.org/2009/08/29/wxpython-catching-key-and-char-events/
        keycode = event.GetKeyCode()
        controlDown = event.CmdDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        #print keycode
        
        if controlDown and keycode == 1:    # CTRL-A
            self.multiText.SelectAll()

        event.Skip()

    def OnDumpUmlWorkspace(self, event):
        self.umlwin.DumpStatus()

    def OnSaveGraphToConsole(self, event):
        print self.umlwin.umlworkspace.graph.GraphToString()

    def OnSaveGraph(self, event):
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.\\saved uml workspaces',
            defaultFile="", wildcard="*.txt", style=wx.FD_SAVE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            
            fp = open(filename, "w")
            fp.write(self.umlwin.umlworkspace.graph.GraphToString())
            fp.close()
        dlg.Destroy()
        
    def OnLoadGraphFromText(self, event):
        eg = "{'type':'node', 'id':'A', 'x':142, 'y':129, 'width':250, 'height':250}"
        dialog = wx.TextEntryDialog (parent=self.frame, message='Enter node/edge persistence strings:', caption='Load Graph From Text', defaultValue=eg, style=wx.OK|wx.CANCEL|wx.TE_MULTILINE )
        if dialog.ShowModal() == wx.ID_OK:
            txt = dialog.GetValue()
            print txt
            self.LoadGraph(txt)
        dialog.Destroy()
            
    def OnLoadGraph(self, event):
        thisdir = self.config.get('LastDirFileOpen', '.\\saved uml workspaces') # remember dir path
        
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.txt", style=wx.OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            self.config['LastDirFileOpen'] = dlg.GetDirectory()  # remember dir path
            self.config.write()

            fp = open(filename, "r")
            s = fp.read()
            fp.close()

            self.LoadGraph(s)
        dlg.Destroy()

    def LoadGraph(self, filedata=""):
        self.umlwin.Clear()
        
        self.umlwin.umlworkspace.graph.LoadGraphFromStrings(filedata)
                
        # build view from model
        self.umlwin.stage1(translatecoords=False)

        # set layout coords to be in sync with world, so that if expand scale things will work
        self.umlwin.coordmapper.Recalibrate()
        self.umlwin.AllToLayoutCoords()
        
        # refresh view
        self.umlwin.GetDiagram().ShowAll(1) # need this, yes
        self.umlwin.stateofthenation()
        
        self.RefreshAsciiUmlTab()

        
    def OnTabPageChanged(self, event):
        if event.GetSelection() == 0:  # ogl
            self.Bind(wx.EVT_MOUSEWHEEL, self.umlwin.OnWheelZoom)  # rebind as it seems to get unbound when switch to ascii tab
            wx.CallAfter(self.umlwin.SetFocus)
            self.menuBar.EnableTop(2, True)  # enable layout menu

        #elif event.GetSelection() == 1:  # yuml
        #    #self.yuml.ViewImage(thefile='../outyuml.png')
        #    pass

        elif event.GetSelection() == 1:  # ascii art
            self.RefreshAsciiUmlTab()
            self.menuBar.EnableTop(2, False)  # disable layout menu
            wx.CallAfter(self.multiText.SetFocus)
            wx.CallAfter(self.multiText.SetInsertionPoint, 0) 
         
        event.Skip()
        
    def RefreshAsciiUmlTab(self):
        self.model_to_ascii()
        
    def InitMenus(self):
        menuBar = wx.MenuBar(); self.menuBar = menuBar
        menu1 = wx.Menu()
        menu2 = wx.Menu()
        menu3 = wx.Menu()
        menu3sub = wx.Menu()
        menu4 = wx.Menu()

        self.next_menu_id = wx.NewId()
        def Add(menu, s1, s2, func, func_update=None):
            menu_item = menu.Append(self.next_menu_id, s1, s2)
            wx.EVT_MENU(self, self.next_menu_id, func)
            if func_update:
                wx.EVT_UPDATE_UI(self, self.next_menu_id, func_update)
            self.next_menu_id = wx.NewId()
            return menu_item

        def AddSubMenu(menu, submenu, s):
            menu.AppendMenu(self.next_menu_id, s, submenu)
            self.next_menu_id = wx.NewId()

        Add(menu1, "&New\tCtrl-N", "New Diagram", self.FileNew)
        Add(menu1, "&Open...\tCtrl-O", "Load UML Diagram...", self.OnLoadGraph)
        Add(menu1, "&Save As...\tCtrl-S", "Save UML Diagram...", self.OnSaveGraph)
        menu1.AppendSeparator()
        Add(menu1, "&Import Python Code...\tCtrl-I", "Import Python Source Files", self.FileImport)
        #Add(menu1, "File &Import yUml...\tCtrl-Y", "Import Python Source Files", self.FileImport2)
        #Add(menu1, "&Import Ascii Art...\tCtrl-J", "Import Python Source Files", self.FileImport3)
        menu1.AppendSeparator()
        Add(menu1, "&Print / Preview...\tCtrl-P", "Print", self.FilePrint)
        menu1.AppendSeparator()
        Add(menu1, "E&xit\tAlt-X", "Exit demo", self.OnButton)
        
        Add(menu2, "&Insert Class...\tIns", "Insert Class...", self.OnInsertClass)
        Add(menu2, "&Insert Image...\tCtrl-Ins", "Insert Image...", self.OnInsertImage)
        Add(menu2, "&Insert Comment...\tShift-Ins", "Insert Comment...", self.OnInsertComment)
        menu_item_delete_class = Add(menu2, "&Delete\tDel", "Delete", self.OnDeleteNode, self.OnDeleteNode_update)
        menu_item_delete_class.Enable(True)  # demo one way to enable/disable.  But better to do via _update function
        Add(menu2, "&Edit Class Properties...\tF2", "Edit Class Properties", self.OnEditProperties, self.OnEditProperties_update)
        menu2.AppendSeparator()
        Add(menu2, "&Refresh", "Refresh", self.OnRefreshUmlWindow)
        
        Add(menu3, "&Layout UML\tL", "Layout UML", self.OnLayout)
        Add(menu3, "&Layout UML Optimally (slower)\tB", "Deep Layout UML (slow)", self.OnDeepLayout)
        menu3.AppendSeparator()
        Add(menu3sub, "&Remember Layout into memory slot 1\tShift-9", "Remember Layout 1", self.OnRememberLayout1)
        Add(menu3sub, "&Restore Layout 1\t9", "Restore Layout 1", self.OnRestoreLayout1)
        menu3sub.AppendSeparator()
        Add(menu3sub, "&Remember Layout into memory slot 2\tShift-0", "Remember Layout 2", self.OnRememberLayout2)
        Add(menu3sub, "&Restore Layout 2\t0", "Restore Layout 2", self.OnRestoreLayout2)
        AddSubMenu(menu3, menu3sub, "Snapshots")
        #menu3.AppendSeparator()
        #Add(menu3, "&Expand Layout\t->", "Expand Layout", self.OnExpandLayout)
        menu3.AppendSeparator()
        
        
        Add(menu4, "&Help...\tF1", "Help", self.OnHelp)
        Add(menu4, "&Visit PyNSource Website...", "PyNSource Website", self.OnVisitWebsite)
        Add(menu4, "&Check for Updates...", "Check for Updates", self.OnCheckForUpdates)
        menu4.AppendSeparator()
        Add(menu4, "&About...", "About...", self.OnAbout)

        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Edit")
        menuBar.Append(menu3, "&Layout")
        menuBar.Append(menu4, "&Help")
        self.frame.SetMenuBar(menuBar)
        
    def OnRememberLayout1(self, event):
        self.umlwin.CmdRememberLayout1()
    def OnRememberLayout2(self, event):
        self.umlwin.CmdRememberLayout2()
    def OnRestoreLayout1(self, event):
        self.umlwin.CmdRestoreLayout1()
    def OnRestoreLayout2(self, event):
        self.umlwin.CmdRestoreLayout2()
        
    def FileImport(self, event):
        self.notebook.SetSelection(0)
        
        thisdir = self.config.get('LastDirFileImport', os.getcwd()) # remember dir path
        
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            
            self.config['LastDirFileImport'] = dlg.GetDirectory()  # remember dir path
            self.config.write()
            
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            self.umlwin.Go(files=filenames)
            self.umlwin.RedrawEverything()
            wx.EndBusyCursor()
            print 'Import - Done.'


    def model_to_ascii(self):
        from layout.layout_ascii import model_to_ascii_builder
        import time
        
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        m = model_to_ascii_builder()
        try:
            wx.SafeYield()
            #time.sleep(0.2)
            s = m.main(self.umlwin.umlworkspace.graph)
            #self.notebook.SetSelection(2)            
            self.multiText.SetValue(str(s))
            if str(s).strip() == "":
                self.multiText.SetValue(ASCII_UML_HELP_MSG)
            self.multiText.ShowPosition(0)
        finally:
            wx.EndBusyCursor()
            
    def FileNew(self, event):
        self.umlwin.Clear()
        self.RefreshAsciiUmlTab()
        
    def FilePrint(self, event):

        from printframework import MyPrintout

        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_LETTER)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.canvas = self.umlwin.GetDiagram().GetCanvas()

        #self.log.WriteText("OnPrintPreview\n")
        printout = MyPrintout(self.canvas, self.log)
        printout2 = MyPrintout(self.canvas, self.log)
        self.preview = wx.PrintPreview(printout, printout2, self.printData)
        if not self.preview.Ok():
            self.log.WriteText("Houston, we have a problem...\n")
            return

        frame = wx.PreviewFrame(self.preview, self.frame, "This is a print preview")

        frame.Initialize()
        frame.SetPosition(self.frame.GetPosition())
        frame.SetSize(self.frame.GetSize())
        frame.Show(True)

    def OnAbout(self, event):
        #self.MessageBox(ABOUT_MSG.strip() %  APP_VERSION)
        
        from wx.lib.wordwrap import wordwrap
        info = wx.AboutDialogInfo()
        #info.SetIcon(wx.Icon('Images\\img_uml01.png', wx.BITMAP_TYPE_PNG))
        info.SetName(ABOUT_APPNAME)
        info.SetVersion(str(APP_VERSION))
        info.SetDescription(ABOUT_MSG)
        #info.Description = wordwrap(ABOUT_MSG, 350, wx.ClientDC(self.frame))
        info.SetCopyright(ABOUT_AUTHOR)
        #info.SetWebSite(WEB_PYNSOURCE_HOME_URL)
        info.WebSite = (WEB_PYNSOURCE_HOME_URL, "Home Page")
        info.SetLicence(ABOUT_LICENSE)
        #info.AddDeveloper(ABOUT_AUTHOR)
        #info.AddDocWriter(ABOUT_FEATURES)
        #info.AddArtist('Blah')
        #info.AddTranslator('Blah')

        wx.AboutBox(info)

    def OnVisitWebsite(self, event):
        import webbrowser
        webbrowser.open(WEB_PYNSOURCE_HOME_URL)

    def OnCheckForUpdates(self, event):
        import urllib2
        s = urllib2.urlopen(WEB_VERSION_CHECK_URL).read()
        s = s.replace("\r", "")
        info = eval(s)
        ver = info["latest_version"]
        
        if ver > APP_VERSION:
            msg = WEB_UPDATE_MSG % (ver, info["latest_announcement"].strip())
            retCode = wx.MessageBox(msg.strip(), "Update Check", wx.YES_NO | wx.ICON_QUESTION)  # MessageBox simpler than MessageDialog
            if (retCode == wx.YES):
                import webbrowser
                webbrowser.open(info["download_url"])
        else:
            self.MessageBox("You already have the latest version:  %s" % APP_VERSION)
    
    def OnHelp(self, event):
        self.MessageBox(HELP_MSG.strip())

    def Enable_if_node_selected(self, event):
        selected = [s for s in self.umlwin.GetDiagram().GetShapeList() if s.Selected()]
        viewing_uml_tab = self.notebook.GetSelection() == 0
        event.Enable(len(selected) > 0 and viewing_uml_tab)

    def OnDeleteNode(self, event):
        self.observers.CMD_NODE_DELETE_SELECTED()
                
    def OnDeleteNode_update(self, event):
        self.Enable_if_node_selected(event)

    def OnInsertComment(self, event):
        self.observers.CMD_INSERT_COMMENT()

    def OnInsertImage(self, event):
        self.observers.CMD_INSERT_IMAGE()
                
    def OnInsertClass(self, event):
        self.observers.CMD_INSERT_CLASS()
        
    def OnEditProperties(self, event):
        for shape in self.umlwin.GetDiagram().GetShapeList():
            if shape.Selected():
                self.observers.CMD_EDIT_CLASS(shape)
                break
            
    def OnEditProperties_update(self, event):
        self.Enable_if_node_selected(event)

    def OnLayout(self, event):
        self.umlwin.CmdLayout()

    def OnDeepLayout(self, event):
        self.umlwin.CmdDeepLayout()


    def OnRefreshUmlWindow(self, event):
        self.umlwin.RedrawEverything()
        self.RefreshAsciiUmlTab()

    def MessageBox(self, msg):
        dlg = wx.MessageDialog(self.frame, msg, 'Message', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnButton(self, evt):
        self.frame.Close(True)


    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.umlwin.ShutdownDemo()
        evt.Skip()

def main():
    application = MainApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()


