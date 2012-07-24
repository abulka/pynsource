"""
Simple ogl scrolling canvas to test redraw algorithms.
"""

import wx
import wx.lib.ogl as ogl
import os, stat
import random

WINDOW_SIZE = (1024,768)

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
    scrollStepX = 10
    scrollStepY = 10

    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        maxWidth  = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)
        
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
        
        keycode = chr(event.GetKeyCode())

        if keycode == 'm':
            #print len(self.GetDiagram().GetShapeList())
            
            shape = self.GetDiagram().GetShapeList()[random.randint(0,17)]
            
            dc = wx.ClientDC(self)
            self.PrepareDC(dc)

            # V1
            #setpos(shape, random.randint(1,300), 0)
            #self.GetDiagram().Clear(dc)
            #self.GetDiagram().Redraw(dc)
        
            # V2 - duplicates cos no clear
            #shape.Move(dc, shape.GetX(), shape.GetY())
        
            # V3 - duplicates cos no clear
            #x = random.randint(1,300)
            #y = 0
            #width, height = shape.GetBoundingBoxMax()
            #x += width/2
            #y += height/2
            #shape.Move(dc, x, y)

            x = random.randint(1,600)
            y = shape.GetY()
            width, height = shape.GetBoundingBoxMax()
            x += width/2
            #y += height/2
            shape.Move(dc, x, y, display=False)
            self.GetDiagram().Clear(dc)
            self.GetDiagram().Redraw(dc)

        elif keycode == 'w':
            pass
            
        elif keycode in ['1','2','3','4','5','6','7','8']:
            pass

        elif keycode in ['b', 'B']:
            pass
                
        self.working = False
        event.Skip()
  
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
        size = wx.Size(size[0], size[1])
        nvsx, nvsy = size.x / self.scrollStepX, size.y / self.scrollStepY
        self.Scroll(0, 0)
        self.SetScrollbars(self.scrollStepX, self.scrollStepY, nvsx, nvsy)
        canvas = self
        canvas.SetSize(canvas.GetVirtualSize())



class MainApp(wx.App):
    def OnInit(self):
        self.log = Log()
        self.working = False
        wx.InitAllImageHandlers()
        self.andyapptitle = 'ogl scroll testPyNsource GUI - Python Code into UML'

        self.frame = wx.Frame(None, -1, self.andyapptitle, pos=(50,50), size=(0,0),
                        style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.DEFAULT_FRAME_STYLE)
        self.frame.CreateStatusBar()

        self.umlwin = UmlCanvas(self.frame, Log(), self.frame)
            
        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.
        
        # Set the frame to a good size for showing stuff
        self.frame.SetSize(WINDOW_SIZE)
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
        self.umlwin.set_uml_canvas_size(sz)  # (9000,9000)

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


