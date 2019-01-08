import wx
import wx.lib.ogl as ogl

import os, stat

# from app.app import App
import wx.lib.mixins.inspection  # Ctrl-Alt-I

WINDOW_SIZE = (1024, 768)
MIN_SENSIBLE_CANVAS_SIZE = 200


class MainApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        # self.log = Log()
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

        self.notebook = wx.Notebook(self.frame, -1)
        self.umlwin = UmlCanvas(self.notebook, None, self.frame)
        self.asciiart = wx.Panel(self.notebook, -1)
        self.notebook.AddPage(self.umlwin, "UML")
        self.notebook.AddPage(self.asciiart, "Ascii Art")
        self.multiText = wx.TextCtrl(
            self.asciiart, -1, "ASCII_UML_HELP_MSG", style=wx.TE_MULTILINE | wx.HSCROLL
        )
        bsizer = wx.BoxSizer()
        bsizer.Add(self.multiText, 1, wx.EXPAND)
        self.asciiart.SetSizerAndFit(bsizer)
        self.multiText.SetFont(
            wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        )  # see http://www.wxpython.org/docs/api/wx.Font-class.html for more fonts
        # self.multiText.Bind( wx.EVT_CHAR, self.onKeyChar_Ascii_Text_window)
        # self.multiText.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom_ascii)

        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.

        # import pdb; pdb.set_trace()

        # Set the frame to a good size for showing stuff
        self.frame.SetSize(WINDOW_SIZE)
        self.umlwin.SetFocus()
        self.SetTopWindow(self.frame)

        self.frame.Show(True)
        print(self.umlwin.GetSize())  # should be bigger now.  but it isn't???
        # self.frame.SetSizer(self.sizer)

        self.umlwin.InitSizeAndObjs()  # Now that frame is visible and calculated, there should be sensible world coords to use
        return True


class UmlCanvas(ogl.ShapeCanvas):
    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)

        # self.observers = multicast()
        self.app = None  # assigned later by app boot

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE")

        self.SetDiagram(ogl.Diagram())
        self.GetDiagram().SetCanvas(self)

        # wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)
        # self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        # self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        # self.Bind(wx.EVT_CHAR, self.onKeyChar)

        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

        # self.working = False
        # self._kill_layout = False   # flag to communicate with layout engine.  aborting keypress in gui should set this to true
        #
        # @property
        # def kill_layout(self):
        #   return self._kill_layout
        # @kill_layout.setter
        # def kill_layout(self, value):
        #   self._kill_layout = value

    def InitSizeAndObjs(self):
        # Only call this once enclosing frame has been set up, so that get correct world coord dimensions

        width, height = self.GetSize()
        print(width < MIN_SENSIBLE_CANVAS_SIZE or height < MIN_SENSIBLE_CANVAS_SIZE)

        # assert not self.canvas_resizer.canvas_too_small(), "InitSizeAndObjs being called too early - please set up enclosing frame size first"


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
