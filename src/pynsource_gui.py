"""
Pynsource GUI
-------------

(c) Andy Bulka
www.andypatterns.com

Community Edition
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

Pro Edition
LICENCE: Commercial

The pro edition of Pynsource requires a valid paid license.  Please
support further development of this project by purchasing a license
http://pynsource.atug.com/buy
"""

import os
import sys
# from pydbg import dbg
from common.messages import *
import wx
from gui.settings import PRO_EDITION, ASYNC_BACKGROUND_REFRESH, LOCAL_OGL
from common.printframework import MyPrintout
from media import images
from gui.settings import APP_VERSION, APP_VERSION_FULL, APP_ICON_PATH
from gui.settings_wx import DEFAULT_ASCII_UML_FONT_SIZE
from generate_code.gen_plantuml import displaymodel_to_plantuml
from generate_code.gen_plantuml import plant_uml_create_png_and_return_image_url_async
from common.dialog_dir_path import dialog_path_pyinstaller_push, dialog_path_pyinstaller_pop, set_original_working_dir
from configobj import ConfigObj  # pip install configobj
from appdirs import AppDirs  # pip install appdirs
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
import asyncio
import aiohttp
from asyncio.events import get_event_loop
from app.settings import RefreshPlantUmlEvent, EVT_REFRESH_PLANTUML_EVENT
from app.settings import CancelRefreshPlantUmlEvent, EVT_CANCEL_REFRESH_PLANTUML_EVENT
from app.settings import ASYNC
import datetime
from contextlib import suppress
import urllib.request, urllib.parse
from common.url_to_data import url_to_data
import json
from typing import List, Set, Dict, Tuple, Optional
import webbrowser


if PRO_EDITION:
    import ogl2 as ogl
    from pro.gui_imageviewer2 import ImageViewer2 as ImageViewer
else:
    if LOCAL_OGL:
        import ogl
    else:
        import wx.lib.ogl as ogl
    from common.gui_imageviewer import ImageViewer

WINDOW_SIZE = (1024, 768)
GUI_LAYOUT = "MULTI_TAB_GUI"  # "MULTI_TAB_GUI" or "SPLIT_GUI" or None
USE_SIZER = False
ALLOW_INSERT_IMAGE_AND_COMMENT_COMMANDS = True

# if 'wxMac' in wx.PlatformInfo:
#     GUI_LAYOUT = None

from gui.uml_canvas import UmlCanvas
from gui.wx_log import Log
from ascii_uml.layout_ascii import model_to_ascii_builder
import logging
from common.logger import config_log
from app.app import App
import wx.lib.mixins.inspection  # Ctrl-Alt-I

unregistered = not PRO_EDITION

log = logging.getLogger(__name__)
config_log(log)


class MainApp(WxAsyncApp):  #, wx.lib.mixins.inspection.InspectionMixin):
# class MainApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)  # needed for window 10
        # self.Init()  # initialize the inspection tool
        self.log = Log()
        self.working = False
        self.printData = None
        wx.InitAllImageHandlers()
        self.andyapptitle = "Pynsource"

        self.args = sys.argv[1:]

        self.frame = wx.Frame(
            None,
            -1,
            self.andyapptitle,
            pos=(50, 50),
            size=(0, 0),
            style=wx.DEFAULT_FRAME_STYLE,
            # style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.DEFAULT_FRAME_STYLE,
            # style=wx.DEFAULT_FRAME_STYLE & ~ (wx.MAXIMIZE_BOX),
            # style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION | wx.CLIP_CHILDREN | wx.CLOSE_BOX
        )
        self.frame.CreateStatusBar()

        """
        Setting double buffered True solves blurring of shapes as you drag them under wx.ogl and solves the constant
        flickering of the display in ogl2 mode due to the constant Refresh() thus paints happening.
        Its supposed to be true by default, however it is actually false by default on windows!.  Cannot turn off on Mac.
        """
        self.frame.SetDoubleBuffered(True)
        # print(self.frame.IsDoubleBuffered())

        # ANDY HACK SECTION - STOP BUILDING THE REST OF THE UI AND SHOW THE FRAME NOW!
        # self.frame.SetPosition((40, 40))
        # self.frame.SetSize((400, 400))
        # self.frame.Show()
        # self.OnHelp(None)  # attempt to trigger help window instantly - works!  And mouse scrolling works.
        # return True
        # END HACK SECTION

        if GUI_LAYOUT == "MULTI_TAB_GUI":

            # self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
            sizer = wx.BoxSizer(wx.VERTICAL)
            self.notebook = wx.Notebook(
                self.frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0, # 0 or wx.NB_RIGHT
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

            if 'wxMac' in wx.PlatformInfo:
                # Prevent '-' being turned into special dash which causes ascii lines to look wrong
                self.multiText.OSXEnableAutomaticDashSubstitution(False)

            self.multiText.SetFont(
                wx.Font(DEFAULT_ASCII_UML_FONT_SIZE, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
            )  # see http://www.wxpython.org/docs/api/wx.Font-class.html for more fonts
            
            asciiart_sizer.Add(self.multiText, 1, wx.EXPAND | wx.ALL, 0)
            self.asciiart.SetSizer(asciiart_sizer)
            self.asciiart.Layout()
            asciiart_sizer.Fit(self.asciiart)
            self.notebook.AddPage(self.asciiart, "Ascii Art", True)

            # Page 2
            self.plantuml = ImageViewer(self.notebook)
            self.notebook.AddPage(self.plantuml, "PlantUML", True)

            sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 0)
            self.frame.SetSizer(sizer)
            self.frame.Layout()
            self.frame.Centre(wx.BOTH)
            # self.frame.Show()
            self.notebook.ChangeSelection(0)

            self.multiText.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom_ascii)
            self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabPageChanged)  # builds ascii

        elif GUI_LAYOUT == "SPLIT_GUI":

            # Ascii UML text control above the canvas - good for testing canvas coord resiliency

            bSizer1 = wx.BoxSizer(wx.VERTICAL)

            self.notebook = wx.Notebook(self.frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                        0)
            self.m_panel1 = wx.Panel(self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                     wx.TAB_TRAVERSAL)
            bSizer3 = wx.BoxSizer(wx.VERTICAL)

            self.m_scrolledWindow4 = wx.ScrolledWindow(self.m_panel1, wx.ID_ANY, wx.DefaultPosition,
                                                       wx.DefaultSize, wx.HSCROLL | wx.VSCROLL)
            self.m_scrolledWindow4.SetScrollRate(5, 5)
            bSizer5 = wx.BoxSizer(wx.VERTICAL)

            self.m_textCtrl2 = wx.TextCtrl(self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString,
                                           wx.DefaultPosition, wx.DefaultSize, style=wx.TE_MULTILINE | wx.HSCROLL)
            self.m_textCtrl2.SetFont(wx.Font(DEFAULT_ASCII_UML_FONT_SIZE, wx.MODERN, wx.NORMAL, wx.NORMAL, False))
            bSizer5.Add(self.m_textCtrl2, 1, wx.ALL | wx.EXPAND, 5)

            self.m_scrolledWindow4.SetSizer(bSizer5)
            self.m_scrolledWindow4.Layout()
            bSizer5.Fit(self.m_scrolledWindow4)
            bSizer3.Add(self.m_scrolledWindow4, 1, wx.EXPAND | wx.ALL, 5)

            self.umlcanvas = UmlCanvas(self.m_panel1, Log(), self.frame)
            self.umlcanvas.SetScrollRate(5, 5)
            # self.m_scrolledWindow3 = wx.ScrolledWindow(self.m_panel1, wx.ID_ANY, wx.DefaultPosition,
            #                                            wx.DefaultSize, wx.HSCROLL | wx.VSCROLL)
            # self.m_scrolledWindow3.SetScrollRate(5, 5)
            # bSizer3.Add(self.m_scrolledWindow3, 3, wx.EXPAND | wx.ALL, 5)
            UML_CANVAS_PROPORTION = 2  # set to 3 to make ascii window smaller and uml canvas bigger
            bSizer3.Add(self.umlcanvas, UML_CANVAS_PROPORTION, wx.EXPAND | wx.ALL, 5)

            self.m_panel1.SetSizer(bSizer3)
            self.m_panel1.Layout()
            bSizer3.Fit(self.m_panel1)
            self.notebook.AddPage(self.m_panel1, u"a page", False)

            bSizer1.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

            self.frame.SetSizer(bSizer1)
            self.frame.Layout()

            self.frame.Centre(wx.BOTH)
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
                wx.Font(DEFAULT_ASCII_UML_FONT_SIZE, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
            )  # see http://www.wxpython.org/docs/api/wx.Font-class.html for more fonts

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
        if GUI_LAYOUT == "MULTI_TAB_GUI":
            context.multiText = self.multiText
            context.asciiart = self.asciiart
            self.plantuml.context = context  # actually only need to pass config
        elif GUI_LAYOUT == "SPLIT_GUI":
            self.multiText = self.m_textCtrl2
            self.asciiart = self.m_scrolledWindow4
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

        if ASYNC:
            # Custom event bindings
            # don't specify id, and use self.frame not self
            AsyncBind(EVT_REFRESH_PLANTUML_EVENT, self.refresh_plantuml_view, self.frame)
            AsyncBind(EVT_CANCEL_REFRESH_PLANTUML_EVENT,
                      self.cancel_refresh_plantuml_view,
                      self.frame)
        else:
            # bind custom event to synchronous handler - works OK
            self.Bind(EVT_REFRESH_PLANTUML_EVENT, self.refresh_plantuml_view)

        self.determine_cwd()
        self.set_custom_window_position()

        """
        Only run bootstrap command at startup to load a sample file - only in dev mode 
        """
        if getattr(sys, 'frozen', False):
            # running in a bundle
            pass
            # doesn't make a difference calling this via CallAfter ?
            # though when deployed, need a delay
            # wx.CallAfter(self.app.run.CmdBootStrap)
            # fix refresh issue on macbook air when deployed
            # wx.CallLater(100, self.app.run.CmdRefreshUmlWindow)  # risky - may clash with wx.SafeYield()
        else:
            # running live in development mode
            # Load an initial diagram, for fun
            if "wxGTK" not in wx.PlatformInfo:
                wx.CallAfter(self.app.run.CmdBootStrap)  # causes safe yield warnings on linux?
            # wx.CallLater(2000, self.app.run.CmdBootStrap)

            wx.CallAfter(self.PostOglViewSwitch)  # ensure status bar message appears after loading

        try:
            if ASYNC:
                StartCoroutine(self.check_for_updates, self.frame)
        except Exception as e:
            print(e)
            print("Error checking for latest version during startup? Exception bypassed.")
            # raise e

        if ASYNC and ASYNC_BACKGROUND_REFRESH:
            StartCoroutine(self.mega_refresh_check, self.frame)

        self._set_app_icon()

        log.info(f"Pynsource version {APP_VERSION_FULL} running, ASYNC={ASYNC}, PRO={PRO_EDITION}")
        log.info(f'wxPython version {wx.version()}')  # wx.VersionInfo().GetVersionString() doesn't work

        if self.args:
            wx.CallAfter(self.app.run.CmdFileImportViaArgs, self.args, 3)  # default to Python 3 reverse engineering

        # wx.lib.inspection.InspectionTool().Show()

        return True

    def _set_app_icon(self):
        """
        Set app icon, though for Mac you need to set up a .plist pointing to a .icns file when
        bundling using pyinstaller
        Though... somehow the official wxdemo seems to change mac icon running in devel mode?
        """
        try:
            wd = sys._MEIPASS
        except AttributeError:
            wd = os.path.dirname(os.path.realpath(__file__))  # "."
        path = os.path.join(wd, APP_ICON_PATH)
        self.frame.SetIcon(wx.Icon(path))

    def determine_cwd(self):
        """
        Determine the place where Pynsource is running from, so can access media and html
        """
        cwd_info = {}

        cwd_info['getcwd'] = os.getcwd()

        cwd_info['__file__'] = os.path.dirname(os.path.realpath(__file__))

        if "SNAP" in os.environ:
            cwd_info['SNAP'] = os.environ["SNAP"]

        print("cwd_info", cwd_info)
        set_original_working_dir(cwd_info['__file__'])  # more accurate
        self.cwd_info = cwd_info

    def set_custom_window_position(self):
        """
        Fix for people who have small or unusual displays

        Edit your pynsource.ini file to add one or both entries:

            WindowSize = 200, 400
            WindowPosition = 210, 240

        You can comment out those lines with # e.g.

            #WindowSize = 200, 400
            #WindowPosition = 210, 240

        Returns: -
        """

        window_size = self.config.get("WindowSize", None)
        window_pos = self.config.get("WindowPosition", None)

        # def convert_to_tuple(ls: List[str, str]) -> Tuple[int, int]:
        def convert_to_tuple(ls: List[str]) -> Tuple[int, int]:
            pos = [int(i) for i in ls]
            pos = tuple(pos)
            return pos

        if type(window_size) == list:
            self.frame.SetSize(convert_to_tuple(window_size))

        if type(window_pos) == list:
            self.frame.SetPosition(convert_to_tuple(window_pos))


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
        """Config file.  I have two, the main original one, and a second one that uses wx config."""

        """
        Main config file pynsource.ini
        
        Mac:
            ~/Library/Preferences/Pynsource/pynsource.ini
            e.g.
            /Users/YOURNAME/Library/Preferences/Pynsource/pynsource.ini
            
        Windows:
            C:\\Users\\YOURNAME\\AppData\\Roaming\\Pynsource\\pynsource.ini
            
        Linux:
            ~/.Pynsource/pynsource.ini
        """
        global PYNSOURCE_CONFIG_DIR
        if "wxGTK" in wx.PlatformInfo:
            PYNSOURCE_CONFIG_DIR = "." + PYNSOURCE_CONFIG_DIR

        config_dir = os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), PYNSOURCE_CONFIG_DIR)
        try:
            os.makedirs(config_dir)
        except OSError:
            pass
        self.user_config_file = os.path.join(config_dir, PYNSOURCE_CONFIG_FILE)
        log.info("Pynsource (configobj) config location %s" % self.user_config_file)

        self.config = ConfigObj(self.user_config_file)
        self.config["keyword1"] = 100
        self.config["keyword2"] = "hi there"
        # self.config["LastFilesOpened"] = ["blah", "blah2", "blah3"]

        # Set some sensible defaults
        for key in ["LastDirFileOpen", "LastDirFileImport", "LastDirInsertImage"]:
            if not self.config.get(key, None):
                self.config[key] = os.path.expanduser("~/")

        self.config.write()


        """
        Second config file based on wx API's - needed cos File History API requres it for persistence
        on Mac its stored in "~/Library/Preferences/Pynsource Preferences" if you specify it this way:
            self.configwx = wx.FileConfig(appName=ABOUT_APPNAME, vendorName=VENDOR_NAME)
        but I want the preferences to be in a subdir, together with my other preferences file, so
        by specifying localFilename the preference config file is now
            ~/Library/Preferences/Pynsource/pynsource_wx.ini
        living nicely with the other config file, in the directory
            ~/Library/Preferences/Pynsource/
        """
        self.user_configwx_file = os.path.join(config_dir, PYNSOURCE_CONFIGWX_FILE)
        self.configwx = wx.FileConfig(localFilename=self.user_configwx_file)

        keyword3 = self.configwx.Read("keyword3")  # just testing
        log.info("Pynsource (wx.FileConfig) config location %s" % self.user_configwx_file)
        # print(keyword3)

        """Experiments with using wx.StandardPaths"""
        # std = wx.StandardPaths.Get()
        #
        # print("GetConfigDir is", std.GetConfigDir())
        # print("GetUserDataDir is", std.GetUserDataDir())
        # print("GetUserConfigDir is", std.GetUserConfigDir())
        #
        # results:
        #
        # # GetConfigDir is /Library/Preferences
        # # GetUserDataDir is ~/Library/Application Support/pynsource-gui
        # # GetUserConfigDir is ~/Library/Preferences

        log.info("Main config contents: %s" % self.config)

    def OnResizeFrame(self, event):  # ANDY  interesting - GetVirtualSize grows when resize frame
        # print("OnResizeFrame event.EventObject", event.EventObject.__class__, event.EventObject == self.umlcanvas, isinstance(event.EventObject, wx.ScrolledWindow))

        # if event.EventObject == self.umlcanvas:  # only works in ogl2 mode
        if isinstance(event.EventObject, wx.ScrolledWindow):

            # Proportionally constrained resize.  Nice trick from http://stackoverflow.com/questions/6005960/resizing-a-wxpython-window
            # hsize = event.GetSize()[0] * 0.75
            # self.frame.SetSizeHints(minW=-1, minH=hsize, maxH=hsize)
            # self.frame.SetTitle(str(event.GetSize()))

            # print("GetClientSize()", self.umlcanvas.GetClientSize(), wx.ClientDisplayRect(), wx.DisplaySize())

            # self.umlcanvas.canvas_resizer.frame_calibration()  # do I really need this anymore?

            self.umlcanvas.fix_scrollbars()

            if 'wxMac' in wx.PlatformInfo and not PRO_EDITION:
                # Protect against resizing to pure fullscreen, to avoid weird performance degredation
                # Luckily the Messagebox kills the resize frame attempt!
                # print(f"wx.DisplaySize()={wx.DisplaySize()}")
                alarm = self.frame.GetScreenRect()[2] >= wx.DisplaySize()[0] and \
                        self.frame.GetScreenRect()[3] >= wx.DisplaySize()[1]
                # print(self.frame.GetClientSize(), self.frame.GetScreenRect(), alarm)
                if alarm:
                    # print("\n",whoscalling2())
                    wx.CallAfter(self.mac_fullscreen_warning)

        event.Skip()

    def mac_fullscreen_warning(self):
        if 'wxMac' in wx.PlatformInfo:
            self.MessageBox(PURE_MAC_FULLSCREEN_WARNING)

    def OnWheelZoom_ascii(self, event):
        # Since our binding of wx.EVT_MOUSEWHEEL to here takes over all wheel events
        # we have to manually do the normal test scrolling.  This event can't propogate via event.skip()
        #
        # The native widgets handle the low level
        # events (or not) their own way and wx makes no guarantees about behaviors
        # when intercepting them yourself.
        # --
        # Robin Dunn
        #
        # Update - this doesn't seem true anymore, since my adding event.Skip() at the end
        # of this routine allow regular mouse wheel scrolling to continue to work.

        # print "MOUSEWHEEEL self.working=", self.working
        if self.working:
            return
        self.working = True

        # print event.ShouldPropagate(), dir(event)

        controlDown = event.CmdDown()
        if controlDown:
            direction = event.GetWheelRotation()
            self.ascii_art_zoom(direction)
            self.multiText.ShowPosition(0)

        # don't need this explicit scroll code - it happens naturally
        # else:
        #     if event.GetWheelRotation() < 0:
        #         self.multiText.ScrollLines(4)
        #     else:
        #         self.multiText.ScrollLines(-4)

        self.working = False

        # self.frame.GetEventHandler().ProcessEvent(event)
        # wx.PostEvent(self.frame, event)

        if not controlDown:
            event.Skip()  # Need this or regular mouse wheel scrolling breaks

    def ascii_art_zoom(self, direction=1, amount=1, reset=False):
        if unregistered:
            return

        font = self.multiText.GetFont()
        # dbg(font.GetPointSize())
        # dbg(direction)
        MIN_FONT_SIZE = 4
        MAX_FONT_SIZE = 65

        if reset:
            self.multiText.SetFont(wx.Font(DEFAULT_ASCII_UML_FONT_SIZE, wx.MODERN, wx.NORMAL, wx.NORMAL, False))
            return

        if direction < 0:
            newfontsize = font.GetPointSize() - amount
        else:
            newfontsize = font.GetPointSize() + amount

        if newfontsize > MIN_FONT_SIZE and newfontsize < MAX_FONT_SIZE:
            self.multiText.SetFont(wx.Font(newfontsize, wx.MODERN, wx.NORMAL, wx.NORMAL, False))

    def OnDumpDisplayModel(self, event):
        self.app.run.CmdDumpDisplayModel()

    def OnSaveGraphToConsole(self, event):
        self.app.run.CmdFileSaveWorkspaceToConsole()

    def OnSaveGraphToXML(self, event):
        self.app.run.CmdFileSaveWorkspaceToXML()

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
        if event.GetSelection() == 0:  # canvas diagram
            self.PostOglViewSwitch()
        elif event.GetSelection() == 1:  # ascii art
            self.RefreshAsciiUmlTab()
            self.PostAsciiViewSwitch()
        elif event.GetSelection() == 2:  # plantuml
            # force cos tab hasn't changed yet

            wx.CallAfter(self.plantuml.SetFocus)  # otherwise focus remains on tab itself
            wx.PostEvent(self.frame, RefreshPlantUmlEvent(force=True))

        event.Skip()  # allow the tab change to occur, though seems to happen even if omitted

    async def refresh_plantuml_view(self, event):
        force = getattr(event, "force", False)

        if self.plantuml.working_fetching:
            return

        # await self._refresh_plantuml_view(force)  # original technique doesn't give us task id

        if sys.version_info[1] == 6:  # create_task not available in Python 3.6
            loop = asyncio.get_event_loop()
            self.plantuml_refresh_task = loop.create_task(self._refresh_plantuml_view(force))
        else:
            self.plantuml_refresh_task = asyncio.create_task(self._refresh_plantuml_view(force))

        await self.plantuml_refresh_task

    async def _refresh_plantuml_view(self, force=False):
        """Build plantuml view from display model, which involves converting to PlantUML text and
        sending to PlantUML server to render.

        There are actually two steps.
            1. plant_uml_create_png_and_return_image_url(plant_uml_txt) - contacts plantuml
               server and gets back a html page with the url of the resulting image inside
            2. self.plantuml.ViewImage(url=image_url) - contacts the plantuml server to get image

        'force' means do it regardless of what tab is visible

        If there is an entry in

            ~/Library/Preferences/Pynsource/pynsource.ini

        and it contains

            PlantUmlServerUrl = http://localhost:8080/plantuml/uml

        then that will be used as the Plantuml server url, otherwise the url defaults to
        "http://www.plantuml.com/plantuml/uml"

        For instructions on installing PlantUML server see http://plantuml.com/server or
        otherwise google for advice.

        """
        if force or self.viewing_plantuml_tab:
            if len(self.umlcanvas.displaymodel.graph.nodeSet) == 0:
                self.plantuml.clear()
            else:
                # Generate plantuml from displaymodel graph
                try:
                    plant_uml_txt = displaymodel_to_plantuml(self.umlcanvas.displaymodel)

                    self.plantuml.render_in_progress(True, self.frame)
                    StartCoroutine(self.update_refresh_plantuml_view_clock, self.frame)

                    # internet connection errors getting initial plantuml html are
                    # handled internally to this function
                    plantuml_server_local_url = self.config.get("PlantUmlServerUrl", None)
                    image_url = await plant_uml_create_png_and_return_image_url_async(
                        plant_uml_txt,
                        plantuml_server_local_url=plantuml_server_local_url
                    )

                    # Simulate failures
                    # import random
                    # if random.randint(1,2) == 1:
                    #     image_url = None

                    log.info("image_url of UML %s" % image_url)

                    if image_url:
                        await self.plantuml.ViewImage(url=image_url)
                        self.plantuml.plantuml_text = plant_uml_txt
                        self.frame.SetStatusText(STATUS_TEXT_UML_VIEW)
                    else:
                        self.frame.SetStatusText(STATUS_TEXT_UML_VIEW_NO_PLANTUML_RESPONSE)
                        self.plantuml.clear_cos_connection_error(msg=f"(no image_url from plantuml at {plantuml_server_local_url})") # this is what I was just getting
                        self.plantuml.plantuml_text = plant_uml_txt  # fixed - ensure plantuml_text always available
                finally:
                    self.plantuml.render_in_progress(False, self.frame)

    async def cancel_refresh_plantuml_view(self, event):
        self.plantuml_refresh_task.cancel()
        self.plantuml.render_in_progress(False, self.frame)

    async def update_refresh_plantuml_view_clock(self):
        while self.plantuml.working_fetching:
            if self.viewing_plantuml_tab:
                self._update_clock()
                self.frame.Refresh()  # just in case big on screen message changes
            await asyncio.sleep(0.5)

    def _update_clock(self):
        time_taken: float = self.plantuml.time_taken_fetching
        self.frame.SetStatusText(f"{PLANTUML_VIEW_FETCHING_MSG}  (time taken: {int(time_taken)} seconds)")

    async def async_callback(self, event):
        print("development mode", self._running_andy_development_mode())
        self.frame.SetStatusText("Menu clicked")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Working")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Completed")
        await asyncio.sleep(1)
        self.frame.SetStatusText("")

    def RefreshAsciiUmlTab(self):
        self.model_to_ascii()

    def PostAsciiViewSwitch(self):
        self.menuBar.EnableTop(2, False)  # disable layout menu
        wx.CallAfter(self.multiText.SetFocus)
        wx.CallAfter(self.multiText.SetInsertionPoint, 0)
        self.frame.SetStatusText("Hold ALT whilst dragging to block select.  CMD/Ctrl + Mousewheel to zoom (Pro).")

    def PostOglViewSwitch(self):
        wx.CallAfter(self.umlcanvas.SetFocus)
        self.menuBar.EnableTop(2, True)  # enable layout menu
        self.frame.SetStatusText("Click to select.  Drag to move.  Right click on shapes, lines and workspace.  CMD/Ctrl + Mousewheel to zoom (Pro).")

    def InitMenus(self):
        menuBar = wx.MenuBar()
        self.menuBar = menuBar
        menu1 = self.menu1 = wx.Menu()
        menu2 = wx.Menu()
        menu3 = wx.Menu()
        menu3sub = wx.Menu()
        menu4 = wx.Menu()
        menu5 = wx.Menu()
        menu5sub = wx.Menu()

        # and a file history
        self.filehistory = wx.FileHistory()
        self.filehistory.UseMenu(self.menu1)

        self.next_menu_id = wx.NewIdRef()  # was wx.NewId()

        if getattr(sys, 'frozen', False):
            pro_image = images.pro.GetBitmap() if unregistered else None
        else:
            # set this to images.pro.GetBitmap() if want to see Pro menu images even if registered
            pro_image = images.pro.GetBitmap() if unregistered else None

        def Add(menu, name, shortcut=None, func=None, func_update=None, image=None):

            if "wxGTK" in wx.PlatformInfo:  # ubuntu gtk menus have images disallowed, so add text
                if image:
                    name = f"{name:<30} (Pro)"

            help_string = name
            if shortcut:
                name = "%s\t%s" % (name, shortcut)
            id = self.next_menu_id

            # Mac tweak, see http://wiki.wxpython.org/Optimizing%20for%20Mac%20OS%20X
            if "wxMac" in wx.PlatformInfo and name == "&About...":
                id = wx.ID_ABOUT

            if "wxMSW" in wx.PlatformInfo:
                # Alternate technique for creating menuitem with image, that works under windows.
                # Also works on Mac but not Linux because GTK disables images in menu items.
                # The idea is to create the menuitem first, set the image and THEN add the menu item to the menu.
                menu_item = wx.MenuItem(menu, id, name, help_string)
                if image:
                    menu_item.SetBitmap(image)
                menu_item = menu.Append(menu_item)
            else:
                # Original technique, menu images work ok on mac, but not windows or linux
                menu_item = menu.Append(id, name, help_string)
                if image:
                    menu_item.SetBitmap(image)

            self.Bind(wx.EVT_MENU, func, id=id)
            if func_update:
                self.Bind(wx.EVT_UPDATE_UI, func_update, id=id)

            self.next_menu_id = wx.NewIdRef()  # was wx.NewId()
            return menu_item

        def AddSubMenu(menu, submenu, s):
            menu.AppendSubMenu(submenu, s)

        Add(menu1, "&New", "Ctrl-N", self.FileNew)
        Add(menu1, "&Open...", "Ctrl-O", self.OnLoadGraph)
        Add(menu1, "Open Sample &Diagram...", "Ctrl-U", self.OnLoadGraphSample)
        Add(menu1, "&Save As...", "Ctrl-S", self.OnSaveGraph, self.uml_only_view_update)
        Add(menu1, "&Export Diagram to XML...", "", self.OnSaveGraphToXML, self.uml_only_view_update)
        menu1.AppendSeparator()
        Add(menu1, "&Save PlantUML Image...", "", self.OnSavePlantUml, self.save_plantuml_update, image=pro_image)
        menu1.AppendSeparator()
        Add(menu1, "&Import Python Code...", "Ctrl-I", self.OnFileImport)

        # New way of wiring things up - see https://wxpython.org/blog/avoiding-window-ids/index.html
        self.item_python3_mode = menu1.AppendCheckItem(
            wx.ID_ANY, "Python 3 mode", help="Assume Python syntax 2/3"
        )
        self.Bind(wx.EVT_MENU, self.OnPythonMode, self.item_python3_mode)
        self.item_python3_mode.Check()

        # Visualise Python Modules Checked Menu Item
        name = "Visualise Python Modules"
        if pro_image and ("wxGTK" in wx.PlatformInfo or "wxMSW" in wx.PlatformInfo):
            # ubuntu and windows checkbox menus images disallowed, so use text instead
            name = f"{name:<30} (Pro)"        
        id = wx.NewIdRef()
        self.item_visualise_modules = menu1.AppendCheckItem(
            id, 
            name, 
            help="Visualise Python Modules themselves as UML Boxes with module level vars and defs"
        )
        if pro_image and "wxMac" in wx.PlatformInfo:
            self.item_visualise_modules.SetBitmap(pro_image)
        self.Bind(wx.EVT_MENU, self.OnVisualiseModules, self.item_visualise_modules)
        def visualise_modules_update(event):
            event.Enable(PRO_EDITION)        
        self.Bind(wx.EVT_UPDATE_UI, visualise_modules_update, id=id)
        self.item_visualise_modules.Check()

        menu1.AppendSeparator()
        Add(menu1, "&Print / Preview...", "Ctrl-P", self.FilePrint)
        Add(menu1, "&Page Setup...", "", self.OnPageSetup)
        menu1.AppendSeparator()
        Add(menu1, "E&xit", "Alt-X", self.OnButton)

        K_ADD_CLASS = "F3" if "wxGTK" in wx.PlatformInfo else "Ctrl-1"
        K_ADD_COMMENT = "F4" if "wxGTK" in wx.PlatformInfo else "Ctrl-2"
        K_ADD_IMAGE = "F5" if "wxGTK" in wx.PlatformInfo else "Ctrl-3"

        Add(menu2, "&Add Class...", K_ADD_CLASS, self.OnInsertClass, self.uml_only_view_update)
        if ALLOW_INSERT_IMAGE_AND_COMMENT_COMMANDS:
            Add(menu2, "&Insert Comment...", K_ADD_COMMENT, self.OnInsertComment, self.uml_only_view_update)  # was Shift-I
            Add(menu2, "&Insert Image...", K_ADD_IMAGE, self.OnInsertImage, self.uml_only_view_update)
        menu2.AppendSeparator()
        Add(menu2, "&Duplicate", "Ctrl-D", self.OnDuplicate, self.OnDuplicateNode_update)
        menu2.AppendSeparator()
        menu_item_delete_class = Add(
            menu2, "&Delete", "Del", self.OnDeleteNode, self.OnDeleteNode_update
        )
        menu2.AppendSeparator()
        menu_item_delete_class.Enable(
            True
        )  # demo one way to enable/disable.  But better to do via _update function
        Add(
            menu2,
            "Prop&erties...",
            "F2",
            self.OnEditProperties,
            self.OnEditProperties_update,
        )

        Add(menu5, "Zoom In", "Ctrl-+", self.OnZoomIn, self.OnPro_update, image=pro_image)
        Add(menu5, "Zoom Out", "Ctrl--", self.OnZoomOut, self.OnPro_update, image=pro_image)
        Add(menu5, "Zoom To Fit", "Ctrl-9", self.OnZoomToFit, self.OnPro_update, image=pro_image)
        Add(menu5, "Reset Zoom", "Ctrl-0", self.OnZoomReset, self.OnPro_update, image=pro_image)

        # Add(menu5, "test - add new code block", "Ctrl-7", self.OnNewCodeBlock)
        # Add(menu5, "test - add new DividedShape", "Ctrl-6", self.OnNewDividedShape)
        # menu5.AppendSeparator()

        # if ASYNC:
        #     id = wx.NewIdRef()
        #     menu_item = menu5.Append(id, "test - async call\tCtrl-6")
        #     AsyncBind(wx.EVT_MENU, self.async_callback, menu5, id=id)

        menu5.AppendSeparator()

        Add(menu5, "&Toggle Ascii Art UML", "Ctrl-J", self.OnViewToggleAscii)
        Add(menu5, "&Toggle PlantUML", "Ctrl-K", self.OnViewTogglePlantUml)
        menu5.AppendSeparator()
        Add(menu5, "Colour &Sibling Classes", "Ctrl-F", self.OnColourSiblings, self.uml_only_view_update)

        Add(
            menu5sub,
            "Change &Sibling Class Colour Scheme",
            "Ctrl-T",
            self.OnColourSiblingsRandom, self.uml_only_view_update,
        )
        Add(menu5sub, "&Randomise Class Colour", "Ctrl-G", self.OnCycleColours, self.uml_only_view_update)
        menu5sub.AppendSeparator()
        Add(menu5sub, "Reset to &Default Class Colours", "", self.OnCycleColoursDefault, self.uml_only_view_update)
        AddSubMenu(menu5, menu5sub, "Advanced")
        menu5.AppendSeparator()
        Add(menu5, "&Redraw Screen", "Ctrl-R", self.OnRefreshUmlWindow)

        Add(menu3, "&Layout UML", "Ctrl-L", self.OnLayout, self.uml_only_view_update)
        Add(menu3, "&Layout UML Optimally", "Ctrl-B", self.OnDeepLayout, self.OnPro_and_uml_view_only_update, image=pro_image)
        menu3.AppendSeparator()
        Add(menu3, "&Expand Layout", "Ctrl-.", self.app.run.CmdLayoutExpand, self.uml_only_view_update)
        Add(menu3, "&Contract Layout", "Ctrl-,", self.app.run.CmdLayoutContract, self.uml_only_view_update)
        menu3.AppendSeparator()
        Add(menu3, "&Remember Layout", "Ctrl-6", self.OnRememberLayout2, self.uml_only_view_update)
        Add(menu3, "&Restore Layout", "Ctrl-7", self.OnRestoreLayout2, self.uml_only_view_update)

        Add(menu4, "&Help...", "F1", self.OnHelp)
        Add(menu4, "&Visit Pynsource Website...", "", self.OnVisitWebsite)
        Add(menu4, "&Visit Pynsource Youtube Channel...", "", self.OnVisitYoutube)
        Add(menu4, "&Check for Updates...", "", self.OnCheckForUpdates)
        Add(menu4, "&Report Bug...", "", self.OnReportBug)
        Add(menu4, "View &Log...", "", self.OnViewLog)
        if unregistered:
            menu4.AppendSeparator()
            if "wxGTK" in wx.PlatformInfo:
                Add(menu4, "&Purchase Pro Edition...  (go Pro)", "", self.OnVisitWebsite)
            else:
                Add(menu4, "&Purchase Pro Edition...", "", self.OnVisitWebsite, image=pro_image)
            Add(menu4, "&Enter License...", "", self.OnEnterLicense)
        if not "wxMac" in wx.PlatformInfo:
            menu4.AppendSeparator()
        helpID = Add(menu4, "&About...", "", self.OnAbout).GetId()

        self.add_last_viewed_files(menu1)

        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Edit")
        menuBar.Append(menu3, "&Layout")

        # Super Stoopid Hack (TM) is to just name the menu "View " instead of "View"
        # https://github.com/itsayellow/marcam/issues/52
        # https://github.com/wxWidgets/Phoenix/issues/347
        menuBar.Append(menu5, "&View ")  # the name "View" causes weird mac dock auto items

        menuBar.Append(menu4, "&Help")

        self.frame.SetMenuBar(menuBar)

    def add_last_viewed_files(self, menu):
        self.filehistory.Load(self.configwx)
        self.filehistory.UseMenu(menu)
        self._filehistory_linux_workaround()

        self.Bind(wx.EVT_MENU_RANGE, self.OnFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
        # self.frame.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)  # not working on Linux?  Cleanup on wx.EVT_CLOSE instead

    def _filehistory_linux_workaround(self):
        """
        Under Linux the paths, when loaded, they turn into horrible full paths.

        ...The paths are shown relative to the current working directory, so
        if that changes to the same location as the files then they are shown
        with no path... Robin Dunn https://groups.google.com/forum/#!topic/wxpython-users/ckmTSrF9l54

        Hmm - after loading one previous file from the history, or adding a new file to the history (which
        happens when you load a previous file), then the history menu repairs itself.
        So workaround by adding the latest menu item to the history again, to trigger the repair
        """
        if self.filehistory.Count > 0:
            if "wxGTK" in wx.PlatformInfo:
                path = self.filehistory.GetHistoryFile(0)
                self.filehistory.AddFileToHistory(path)

    def Cleanup(self, *args):
        # A little extra cleanup is required for the FileHistory control
        # print("Cleanup")
        self.filehistory.Save(self.configwx)
        del self.filehistory
        self.configwx.Write("keyword3", "a funny thing happened on the way to the cafe...")

    def OnFileHistory(self, event):
        # get the file based on the menu ID
        fileNum = event.GetId() - wx.ID_FILE1
        path = self.filehistory.GetHistoryFile(fileNum)
        # self.log.write("You selected %s\n" % path)

        try:
            self.app.run.CmdFileLoadWorkspaceFromFilepath(path)
        except FileNotFoundError as e:

            dlg = wx.MessageDialog(self.frame, f"{e}\n\nRemove it from File History?", "Could not open diagram file", style=wx.YES|wx.NO)
            if dlg.ShowModal() == wx.ID_YES:
                self.filehistory.RemoveFileFromHistory(fileNum)
        else:
            # add it back to the history so it will be moved up the list
            self.filehistory.AddFileToHistory(path)

    def OnNewDividedShape(self, event):
        from gui.uml_canvas import DividedShape
        # i = ogl.DividedShape(100,200)
        i = DividedShape(300, 200, self.umlcanvas)
        i.fill = ["AQUAMARINE"]
        i.BuildRegions(self.umlcanvas)  # hmm, why pass in canvas again?!!
        self.umlcanvas.InsertShape(i, 999)
        self.umlcanvas.deselect()
        self.umlcanvas.Refresh()

    def OnNewCodeBlock(self, event):
        i = ogl.CodeBlock()
        # self.canvas.AddShape(i)
        self.umlcanvas.InsertShape(i, 999)
        self.umlcanvas.deselect()
        self.umlcanvas.Refresh()

    def OnZoomIn(self, event):
        if self.viewing_uml_tab:
            self.umlcanvas.zoom_in()
        elif self.viewing_asciiart_tab:
            self.ascii_art_zoom(direction=1, amount=2)  # little bit stronger zoom when via menu
        elif self.viewing_plantuml_tab:
            self.plantuml.zoom(zoom_incr=0.1)

    def OnZoomOut(self, event):
        if self.viewing_uml_tab:
            self.umlcanvas.zoom_out()
        elif self.viewing_asciiart_tab:
            self.ascii_art_zoom(direction=-1, amount=2)
        elif self.viewing_plantuml_tab:
            self.plantuml.zoom(out=False, zoom_incr=0.1)

    def OnZoomToFit(self, event):
        if self.viewing_uml_tab:
            self.umlcanvas.zoom_to_fit()
        elif self.viewing_asciiart_tab:
            self.ascii_art_zoom(reset=True)
        elif self.viewing_plantuml_tab:
            self.plantuml.zoom_to_fit()

    def OnZoomReset(self, event):
        if self.viewing_uml_tab:
            self.umlcanvas.zoom_reset()
        elif self.viewing_asciiart_tab:
            self.ascii_art_zoom(reset=True)
        elif self.viewing_plantuml_tab:
            self.plantuml.zoom(reset=True)

    def OnPythonMode(self, event):
        log.info("python 3 syntax mode state now: %s" % self.item_python3_mode.IsChecked())

    def OnVisualiseModules(self, event):
        log.info("visualise Python Modules state now: %s" % self.item_visualise_modules.IsChecked())

    def OnRightButtonMenu(self, event):  # Menu
        x, y = event.GetPosition()
        if PRO_EDITION:
            hit_which_shapes = self.umlcanvas.getCurrentShape(event)
        else:
            # but hittest fails when canvas is scrolled !!  Fix.
            adjusted_x = x + self.umlcanvas.GetScrollPos(wx.HORIZONTAL)
            adjusted_y = y + self.umlcanvas.GetScrollPos(wx.VERTICAL)
            # Since our binding of wx.EVT_RIGHT_DOWN to here takes over all right click events
            # we have to manually figure out if we have clicked on shape
            # then allow natural shape node menu to kick in via UmlShapeHandler (defined above)
            hit_which_shapes = [
                s
                for s in self.umlcanvas.GetDiagram().GetShapeList()
                if s.HitTest(adjusted_x, adjusted_y)
            ]
        # print('hit_which_shapes', hit_which_shapes)  # hmm seems to pick up lines, too!
        if hit_which_shapes:
            event.Skip()  # will send the event on to the next handler, I think in the canvas
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

        # Developer only tools
        #
        # item = self.popupmenu.Append(wx.ID_ANY, "Load Graph from text...")
        # self.frame.Bind(wx.EVT_MENU, self.OnLoadGraphFromText, item)
        #
        # item = self.popupmenu.Append(wx.ID_ANY, "Dump Graph to console")
        # self.frame.Bind(wx.EVT_MENU, self.OnSaveGraphToConsole, item)
        # 

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "Load Diagram...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoadGraph, item)

        item = self.popupmenu.Append(wx.ID_ANY, "Save Diagram...")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraph, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "Dump Display Model (diagnostic)")
        self.frame.Bind(wx.EVT_MENU, self.OnDumpDisplayModel, item)

        item = self.popupmenu.Append(wx.ID_ANY, "Export Diagram to XML...")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraphToXML, item)

        self.frame.PopupMenu(self.popupmenu, wx.Point(x, y))

    def OnReportBug(self, event):
        # webbrowser.open("http://code.google.com/p/pynsource/issues/list")
        webbrowser.open("https://github.com/abulka/pynsource/issues")

    def OnViewLog(self, event):
        from common.logger import LOG_FILENAME
        webbrowser.open('file://' + LOG_FILENAME)

    def OnRememberLayout1(self, event):
        self.umlcanvas.CmdRememberLayout1()

    def OnRememberLayout2(self, event):
        self.umlcanvas.CmdRememberLayout2()

    def OnRestoreLayout1(self, event):
        self.umlcanvas.CmdRestoreLayout1()
        self.umlcanvas.extra_refresh()

    def OnRestoreLayout2(self, event):
        self.umlcanvas.CmdRestoreLayout2()
        self.umlcanvas.extra_refresh()

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
        visualise_modules = self.item_visualise_modules.IsChecked()
        self.app.run.CmdFileImportViaDialog(mode=mode, visualise_modules=visualise_modules)

    def OnViewTogglePlantUml(self, event):
        if GUI_LAYOUT == "MULTI_TAB_GUI":
            if self.notebook.GetSelection() in (0,1):
                self.notebook.SetSelection(2)
            else:
                self.notebook.SetSelection(0)

    def OnViewToggleAscii(self, event):
        if GUI_LAYOUT == "MULTI_TAB_GUI":
            if self.viewing_uml_tab or self.viewing_plantuml_tab:
                self.notebook.SetSelection(1)
                self.model_to_ascii()
                self.PostAsciiViewSwitch()
            else:
                self.switch_to_ogl_uml_view()
        elif GUI_LAYOUT == "SPLIT_GUI":
            pass
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
        if GUI_LAYOUT == "MULTI_TAB_GUI":
            if self.notebook.GetSelection() == 1:  # ascii uml
                self.notebook.SetSelection(0)
                self.PostOglViewSwitch()
        elif GUI_LAYOUT == "SPLIT_GUI":
            pass
        else:
            self.panel_one.Show()
            self.panel_two.Hide()
            self.PostOglViewSwitch()
            self.frame.Layout()

    def model_to_ascii(self):
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        m = model_to_ascii_builder()
        try:
            # wx.SafeYield()
            # print("avoided safe yield in model to ascii")
            s = m.main(self.umlcanvas.displaymodel.graph)
            self.multiText.SetValue(str(s))
            if str(s).strip() == "":
                self.multiText.SetValue(ASCII_UML_HELP_MSG)
            self.multiText.ShowPosition(0)
        finally:
            wx.EndBusyCursor()

    def FileNew(self, event):
        self.app.run.CmdFileNew()

    def OnPageSetup(self, evt):
        if not self.printData:
            self.printData = wx.PrintData()
        psdd = wx.PageSetupDialogData(self.printData)
        psdd.EnablePrinter(True)
        # psdd.CalculatePaperSizeFromId()
        dlg = wx.PageSetupDialog(self.frame, psdd)
        dlg.ShowModal()

        # this makes a copy of the wx.PrintData instead of just saving
        # a reference to the one inside the PrintDialogData that will
        # be destroyed when the dialog is destroyed
        self.printData = wx.PrintData(dlg.GetPageSetupData().GetPrintData())

        dlg.Destroy()

    def FilePrint(self, event):
        if not self.printData:
            self.printData = wx.PrintData()
        # self.printData = wx.PrintDialogData(self.printData)  # ??

        # Don't set any of these unless you want to override what
        # has been possibly set up in 'self.printData' by an earlier Page Setup.
        #
        # self.printData.SetPaperId(wx.PAPER_LETTER)  # setting paper works
        # self.printData.SetPaperId(wx.PAPER_A4)
        # self.printData.SetDuplex(wx.DUPLEX_VERTICAL)  # setting these doesn't work
        # self.printData.SetDuplex(wx.DUPLEX_HORIZONTAL)
        # self.printData.SetDuplex(wx.DUPLEX_SIMPLEX)  # not duplex
        # self.printData.SetOrientation(wx.LANDSCAPE)  # setting orientation works

        self.printData.SetNoCopies(1)  # setting this works, ensure you pick a non thermal printer
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)

        if self.viewing_plantuml_tab:
            printout = MyPrintout(self.plantuml, self.log)
            printout2 = MyPrintout(self.plantuml, self.log)

            def _fit_diagram_to_paper_for_image(maxX, maxY):
                return self.plantuml.maxWidth, self.plantuml.maxHeight

            printout.bounds_func = _fit_diagram_to_paper_for_image
            printout2.bounds_func = _fit_diagram_to_paper_for_image
        else:
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

        from wx.adv import AboutDialogInfo, AboutBox
        from gui.settings import registered_to

        license = "Community Edition" if unregistered else f"PRO Edition - registered to \"{registered_to}\"\nThank you for your support!"
        info = AboutDialogInfo()

        # image appears on left on all platforms, so make sure the image is small
        # info.SetIcon(wx.Icon('media/pynsource.png', wx.BITMAP_TYPE_PNG)) # TODO fix path when deployed, disable for now

        info.SetName(ABOUT_APPNAME)
        # info.SetVersion(str(APP_VERSION))
        info.SetVersion(APP_VERSION_FULL)
        info.SetWebSite(WEB_PYNSOURCE_HOME_URL, "Home Page")
        info.SetDescription(f"{ABOUT_MSG}\n{license}\n")
        # info.Description = wordwrap(ABOUT_MSG, 350, wx.ClientDC(self.frame))
        info.SetCopyright(ABOUT_AUTHOR)
        license = ABOUT_LICENSE if unregistered else ABOUT_LICENSE_PRO
        license += "\n\n" + ABOUT_LICENSE_DETAILS
        info.SetLicence(license)
        info.AddDeveloper(ABOUT_AUTHORS)
        # info.AddDocWriter(ABOUT_FEATURES)
        # info.AddArtist('Blah')
        # info.AddTranslator('Blah')

        AboutBox(info)

    def OnEnterLicense(self, event):
        from dialogs.DialogRego import RegoDialog
        from gui.settings import enter_license

        if "SNAP" in os.environ:
            wx.MessageBox(f"Please download a binary build of Pynsource to register - snaps cannot be registered.")
            return

        dialog = RegoDialog(None)
        dialog.m_textCtrl_name.Value = ""
        dialog.m_textCtrl_serial.Value = ""

        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.m_textCtrl_name.Value
            serial = dialog.m_textCtrl_serial.Value

            result = enter_license(name, serial)
            if result:
                wx.MessageBox(f"Registration successful - please restart Pynsource.")
            else:
                wx.MessageBox(f"The registration details you entered are invalid for this version of Pynsource.\n\n{name}\n{serial}")
        dialog.Destroy()

    def OnVisitWebsite(self, event):
        import webbrowser

        webbrowser.open(WEB_PYNSOURCE_HOME_URL)

    def OnVisitYoutube(self, event):
        import webbrowser

        webbrowser.open(WEB_PYNSOURCE_YOUTUBE_URL)

    async def mega_refresh_check(self):
        print("mrcheck")
        while True:
            if self.umlcanvas.mega_refresh_flag:
                print("mega refresh check find True!")
                self.umlcanvas.mega_refresh_flag = False
                self.umlcanvas._mega_refresh()
            else:
                self.umlcanvas.Refresh()
                print("plain insurance refresh")
            await asyncio.sleep(0.5)

    async def check_for_updates(self):
        # await asyncio.sleep(15)
        # print("hanging back even longer from doing a version check...")
        await asyncio.sleep(15)
        url = WEB_VERSION_CHECK_URL_TRACKED_DEVEL if self._running_andy_development_mode() else WEB_VERSION_CHECK_URL_TRACKED
        status_code = 0
        log.info(f"Version check url {url}")
        try:
            data, status_code = await url_to_data(url)
            response_text = data.decode('utf-8')
            # info = json.loads(response_text)
            info = eval(response_text)
        # except (ConnectionError, requests.exceptions.RequestException) as e:
        #     # log.exception("Trying to render using plantuml server %s str(e)" % plant_uml_server)
        #     log.error(
        #         f"Error trying to fetch initial html from plantuml server {plant_uml_server} {str(e)}")
        #     return None
        except asyncio.TimeoutError as e:  # there is no string repr of this exception
            log.info("TimeoutError getting latest version info")
        except aiohttp.client_exceptions.ClientConnectorError as e:
            log.info("connection error (no internet?) getting latest version info")
        else:
            log.info(f"Version update response: {status_code}")

        if status_code == 200:
            self._update_alert(info, alert_even_if_running_latest=False)

    def OnCheckForUpdates(self, event):
        url = WEB_VERSION_CHECK_URL_TRACKED_DEVEL if self._running_andy_development_mode() else WEB_VERSION_CHECK_URL_TRACKED
        s = urllib.request.urlopen(url).read().decode("utf-8")
        print(f"manually checked url for updates: {url}")
        s = s.replace("\r", "")
        info = eval(s)
        self._update_alert(info, alert_even_if_running_latest=True)

    def _update_alert(self, info, alert_even_if_running_latest):
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
            if alert_even_if_running_latest:
                self.MessageBox(
                    f"You seem to have a pre-release version {APP_VERSION_FULL} - congratulations!  Stable version is {ver}"
                )
            else:
                log.info("You have a future version of Pynsource!")
        else:
            if alert_even_if_running_latest:
                self.MessageBox("You already have the latest version:  %s" % APP_VERSION_FULL)
            else:
                log.info("latest version ok")

    def _running_andy_development_mode(self):
        return os.path.exists("/Users/Andy/Devel/pynsource-rego") or \
                os.path.exists("/Volumes/SSD/Users/andy/Devel/pynsource-rego") or \
                os.path.exists("/Users/andy/pynsource-rego") or \
                os.path.exists("/home/andy/Devel/pynsource-rego")

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
        from wx.html import EVT_HTML_LINK_CLICKED
        import webbrowser

        class Help(HelpWindow):
            def __init__(self, parent):
                HelpWindow.__init__(self, parent)

                # CMD-W to close Frame by attaching the key bind event to accellerator table
                randomId = wx.NewIdRef()  # was wx.NewId()
                self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=randomId)
                accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("W"), randomId)])
                self.SetAcceleratorTable(accel_tbl)

                self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)  # Close on ESC
                self.m_htmlWin1.Bind(EVT_HTML_LINK_CLICKED, self.link_click)

            def link_click(self, link):
                print("click on", link.GetLinkInfo().Href)
                webbrowser.open(link.GetLinkInfo().Href)

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

        dir = dialog_path_pyinstaller_push(self.frame)
        try:
            f.m_htmlWin1.LoadPage(os.path.join(dir, "HelpWindow.html"))
            f.Show(True)
        finally:
            dialog_path_pyinstaller_pop()

    def Enable_if_node_selected(self, event):
        selected = [s for s in self.umlcanvas.GetDiagram().GetShapeList() if s.Selected()]
        event.Enable(len(selected) > 0 and self.viewing_uml_tab)

    @property
    def viewing_plantuml_tab(self):
        return GUI_LAYOUT == "MULTI_TAB_GUI" and self.notebook.GetSelection() == 2

    @property
    def viewing_asciiart_tab(self):
        return GUI_LAYOUT == "MULTI_TAB_GUI" and self.notebook.GetSelection() == 1

    @property
    def viewing_uml_tab(self):
        if GUI_LAYOUT == "MULTI_TAB_GUI":
            if self.notebook:
                return self.notebook.GetSelection() == 0
            else:
                return False
        elif GUI_LAYOUT == "SPLIT_GUI":
            return True
        else:
            return self.panel_one.IsShown()

    def OnDeleteNode(self, event):
        self.app.run.CmdNodeDeleteSelected()

    def OnDeleteNode_update(self, event):
        self.Enable_if_node_selected(event)

    def OnDuplicateNode_update(self, event):
        self.Enable_if_node_selected(event)

    def uml_only_view_update(self, event):
        event.Enable(self.viewing_uml_tab)

    def save_plantuml_update(self, event):
        event.Enable(self.viewing_plantuml_tab and not unregistered)

    def OnPro_update(self, event):
        event.Enable(not unregistered)

    def OnPro_and_uml_view_only_update(self, event):
        event.Enable(not unregistered and self.viewing_uml_tab)

    def OnSavePlantUml(self, event):
        self.plantuml.OnHandleSaveImage(event)

    def OnInsertComment(self, event):
        self.app.run.CmdInsertComment()

    def OnInsertImage(self, event):
        self.app.run.CmdInsertImage()

    def OnInsertClass(self, event):
        self.app.run.CmdInsertUmlClass()

    def OnDuplicate(self, event):
        self.app.run.CmdDuplicate()

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
        if self.viewing_uml_tab:
            self.app.run.CmdRefreshUmlWindow()
        elif self.viewing_plantuml_tab:
            # self.refresh_plantuml_view()
            wx.PostEvent(self.frame, RefreshPlantUmlEvent(force=False))

    def MessageBox(self, msg):
        dlg = wx.MessageDialog(self.frame, msg, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnButton(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.umlcanvas.ShutdownDemo()
        self.Cleanup()
        evt.Skip()


def main():
    application = MainApp(0)
    # application = MainApp(redirect=True, filename='/tmp/pynsource.log')  # to view what's going on
    application.MainLoop()

# ASYNC VERSION

async def cleanup_tasks():
    try:
        pending = asyncio.all_tasks()
    except (AttributeError, RuntimeError):
        log.info("No pending running tasks on exit")
    else:
        cancelled = set()
        for task in pending:
            if task in cancelled:
                continue
            log.info(f"Cancelling leftover task... {task._coro.cr_code.co_name} {task._state}")
            task.cancel()
            cancelled.add(task)
            try:
                await task
            except asyncio.CancelledError:
                pass


async def main_async():
    # see https://github.com/sirk390/wxasync
    application = MainApp(0)  # an instance of WxAsyncApp

    try:
        await application.MainLoop()
    finally:
        await cleanup_tasks()


def run():
    if ASYNC:
        # main_async()
        asyncio.run(main_async())
    else:
        main()

if __name__ == "__main__":

    # Sanity check for paths, ensure there is not any .. and other relative crud in
    # our path.  You only need that stuff when running a module as a standalone.
    # in which case prefix such appends with if __name__ == '__main__':
    # Otherwise everything should be assumed to run from trunk/src/ as the root
    #
    # import sys, pprint
    # pprint.pprint(sys.path)

    """
    Adding this kind of WORKS to allow the app to run ok in a pyinstaller generated .app (and avoids
    infinite spawning of the main window - stop this with "pkill Pynsource" in bash).  But
    gui.settings still being loaded in an infinite loop, bugs occur, and pynsource keeps running
    (at least gui.settings does) when terminated, needing a pkill.  Very worrisome.  Will have 
    to stop using joblib.
    """
    # if getattr(sys, 'frozen', False):
    #     from multiprocessing import freeze_support  # allow joblib.Memory to be used in pyinstaller
    #     freeze_support()

    run()
