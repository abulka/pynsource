"""
Simple ogl scrolling canvas to test frame resize so that workspace contents are
always visible.
"""

import wx
import wx.lib.ogl as ogl
import os, stat
import random
import wx.lib.mixins.inspection  # Ctrl-Alt-I 


#from gui.coord_utils import setpos, getpos

class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)
    write = WriteText

# compensate for the fact that x, y for a ogl shape are the centre of the shape, not the top left
def setpos(shape, x, y):
    width, height = shape.GetBoundingBoxMax()
    shape.SetX( x + width/2 )
    shape.SetY( y + height/2 )
def getpos(shape):
    width, height = shape.GetBoundingBoxMax()
    x = shape.GetX()
    y = shape.GetY()
    return x - width/2, y - height/2

class UmlCanvas(ogl.ShapeCanvas):
    #scrollStepX = 10
    #scrollStepY = 10

    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        #maxWidth  = 1000
        #maxHeight = 1000
        #self.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)
        
        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE") #wxWHITE)

        self.SetDiagram(ogl.Diagram())
        self.GetDiagram().SetCanvas(self)
        self.save_gdi = []
        wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)

        self.Bind(wx.EVT_CHAR, self.onKeyChar)
        self.working = False

        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

    def onKeyChar(self, event):
        if event.GetKeyCode() >= 256:
            event.Skip()
            return
        if self.working:
            event.Skip()
            return
        self.working = True

        from ogl_redraw_f_logic import process_key

        canvas = self
        keycode = chr(event.GetKeyCode())

        process_key(keycode, self.frame, canvas, canvas.GetDiagram().GetShapeList())

        self.working = False
        event.Skip()
        
        # END OPTIONAL
  
    def OnDestroy(self, evt):
        for shape in self.GetDiagram().GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)

    def OnLeftClick(self, x, y, keys):  # Override of ShapeCanvas method
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        #self.app.run.CmdDeselectAllShapes()
        pass

    # UTILITY - not used, possibly could be called by pynsourcegui.BootStrap
    def set_uml_canvas_size(self, size):
        """
        Currently unused, but it works and sets the canvas size
        and the scrollbars adjust accordingly.
        Set to something big and always have a large scrollable region e.g.
            self.umlwin.set_uml_canvas_size((9000,9000))
        """
        return
        #size = wx.Size(size[0], size[1])
        #nvsx, nvsy = size.x / self.scrollStepX, size.y / self.scrollStepY
        #self.Scroll(0, 0)
        #self.SetScrollbars(self.scrollStepX, self.scrollStepY, nvsx, nvsy)
        #canvas = self
        #canvas.SetSize(canvas.GetVirtualSize()) # Sets the size of the window in pixels.


WINDOW_SIZE = (600, 400)
USENOTEBOOK = False

class MainApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        self.log = Log()
        self.working = False
        wx.InitAllImageHandlers()
        self.andyapptitle = 'ogl scroll testPyNsource GUI - Python Code into UML'

        self.frame = wx.Frame(None, -1, self.andyapptitle, pos=(450,450), size=WINDOW_SIZE,
                        style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.DEFAULT_FRAME_STYLE)
        #wx.FULL_REPAINT_ON_RESIZE
        #wx.NO_FULL_REPAINT_ON_RESIZE
        #self.frame.CreateStatusBar()
        
        if USENOTEBOOK:
            self.notebook = wx.Notebook(self.frame, -1)
            self.umlwin = UmlCanvas(self.notebook, Log(), self.frame)
            self.notebook.AddPage(self.umlwin, "test")
            self.notebook.AddPage(wx.Panel(self.notebook, -1), "Ascii Art")
        else:
            self.umlwin = UmlCanvas(self.frame, Log(), self.frame)

        self.umlwin.frame = self.frame
        
        self.umlwin.SetScrollbars(1, 1, 1200, 800)
        
        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.
        
        # Set the frame to a good size for showing stuff
        #self.frame.SetSize(WINDOW_SIZE)
        
        self.umlwin.SetFocus()
        self.SetTopWindow(self.frame)

        self.frame.Show(True)
        wx.EVT_CLOSE(self.frame, self.OnCloseFrame)
        self.Bind(wx.EVT_SIZE, self.OnResizeFrame)
        
        wx.CallAfter(self.BootStrap)    # doesn't make a difference calling this via CallAfter
        
        return True
    
    def OnResizeFrame (self, event):   # ANDY  interesting - GetVirtualSize grows when resize frame
        #if event.EventObject == self.umlwin:
        #    #print "OnResizeFrame"
        #    self.umlwin.coordmapper.Recalibrate(self.frame.GetClientSize()) # may need to call self.GetVirtualSize() if scrolled window
        #    #self.umlwin.coordmapper.Recalibrate(self.umlwin.GetVirtualSize())

        sz = self.frame.GetClientSize()
        #self.umlwin.set_uml_canvas_size(sz)  # (9000,9000)

        event.Skip()

    def BootStrap(self):
        y = 0
        for x in range(0, 1200, 70):
            shape = ogl.RectangleShape( 60, 60 )
            shape.AddText("%d,%d"%(x,y))
            setpos(shape, x, y)
            self.umlwin.AddShape( shape )
            
            y += 70

        self.umlwin.GetDiagram().ShowAll( 1 )
        print("bounds", self.GetBoundsAllShapes())
        print("canvas.GetVirtualSize()", self.umlwin.GetVirtualSize())
        print("canvas.GetSize()", self.umlwin.GetSize())
        print("frame.GetVirtualSize()", self.frame.GetVirtualSize())
        print("frame.GetSize()", self.frame.GetSize())
        print("frame.GetClientSize()", self.frame.GetClientSize())
        
        # MAGIC solution !!!
        width, height = self.GetBoundsAllShapes()
        self.umlwin.SetScrollbars(1, 1, width, height)
        
        # And you don't need to change anything during a frame resize
        
        
    def GetBoundsAllShapes(self):
        maxx = 0
        maxy = 0

        for shape in self.umlwin.GetDiagram().GetShapeList():
            left = shape.GetX() - shape.GetWidth() / 2
            top = shape.GetY() - shape.GetHeight() / 2
            maxx = max(left, maxx)
            maxy = max(top, maxy)

        return (maxx, maxy)        
        
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


