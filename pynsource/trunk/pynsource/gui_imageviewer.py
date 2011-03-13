import  wx
import sys

ALLOW_DRAWING = True
ZOOM_INCR = 1.3

#FILE = "Images/fish1.png"
FILE = "C:/Users/Andy/Documents/My Dropbox/Photos/Other Good1/german_autopanogiga_sample1.jpg"

class MyCanvas(wx.ScrolledWindow):
    def __init__(self, parent, id = -1, size = wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)# | wx.FULL_REPAINT_ON_RESIZE)

        self.lines = []
        self.maxWidth  = 2000
        self.maxHeight = 2000
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        self.SetBackgroundColour("WHITE")

        img = wx.Image(FILE, wx.BITMAP_TYPE_ANY)
        bmp = img.ConvertToBitmap()

        self.maxWidth, self.maxHeight = bmp.GetSize()[0], bmp.GetSize()[1]
        
        mask = wx.Mask(bmp, wx.BLUE)
        bmp.SetMask(mask)
        self.bmp = bmp

        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(1,1)  # set the ScrollRate to 1 in order for panning to work nicely
        self.zoomscale = 1.0
        self.clear_whole_window = False

        if ALLOW_DRAWING:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftButtonEvent)
            self.Bind(wx.EVT_LEFT_UP,   self.OnLeftButtonEvent)
            self.Bind(wx.EVT_MOTION,    self.OnLeftButtonEvent)
            self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonEvent)  # ANDY
            
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase) # ANDY
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom) # ANDY
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelScroll) # ANDY
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)  # ANDY
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)  # ANDY
        self.Bind(wx.EVT_MOTION, self.OnMove)  # ANDY
        self.Bind ( wx.EVT_SIZE, self.OnResize ) # ANDY
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
        self.was_dragging = False               # True if dragging map
        self.move_dx = 0                        # drag delta values
        self.move_dy = 0
        self.last_drag_x = None                 # previous drag position
        self.last_drag_y = None
        self.SetScrollbars(1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1])
        self.mywheelscroll = 0
        
    def onKeyPress(self, event):   #ANDY
        keycode = event.GetKeyCode()
        if event.ShiftDown():
            self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))
        event.Skip()
        
    def onKeyUp(self, event):   #ANDY
        self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        event.Skip()
        
    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight

    def OnErase(self, event):     # ANDY
        pass
    
    def OnWheelZoom(self, event):    # ANDY
        delta = event.GetWheelDelta() 
        rot = event.GetWheelRotation() 
        if event.ControlDown():
            self.zoom(rot > 0)
        else:
            event.Skip()

    def OnWheelScroll(self, event):
        ## This is an example of what to do for the EVT_MOUSEWHEEL event,
        ## but since wx.ScrolledWindow does this already it's not
        ## necessary to do it ourselves.
        #
        # ANDY
        # But since I set the ScrollRate to 1
        # in order for panning to work nicely
        # scrolling is too slow.  So invoke this code!!
        #

        if event.ControlDown():
            event.Skip()
            return
        
        delta = event.GetWheelDelta()
        rot = event.GetWheelRotation()
        linesPer = event.GetLinesPerAction()
        #print delta, rot, linesPer
        linesPer *= 20   # ANDY trick to override the small ScrollRate
        ws = self.mywheelscroll
        ws = ws + rot
        lines = ws / delta
        ws = ws - lines * delta
        self.mywheelscroll = ws
        if lines != 0:
            lines = lines * linesPer
            vsx, vsy = self.GetViewStart()
            scrollTo = vsy - lines
            self.Scroll(-1, scrollTo)
        event.Skip()
        
    def zoom(self, out=True, reset=False):
        if reset:
            self.zoomscale = 1.0
        else:
            if out:
                self.zoomscale *= ZOOM_INCR
            else:
                self.zoomscale /= ZOOM_INCR
        if self.zoomscale == 0:
            self.zoomscale = 1.0
        print "zoom %f " % self.zoomscale

        if out:
            jumptox, jumptoy = self.GetViewStart()[0]*ZOOM_INCR, self.GetViewStart()[1]*ZOOM_INCR
        else:
            jumptox, jumptoy = self.GetViewStart()[0]/ZOOM_INCR, self.GetViewStart()[1]/ZOOM_INCR
            
        self.SetVirtualSize(self.CalcVirtSize())
        self.SetScrollbars(1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1], jumptox, jumptoy, True) # boolean is skip refresh or not, doesn't seem to matter
       
        # If zoom out so much you need to clear the whole window to get rid of bigger image remnants
        if self.NeedToClear():
            self.clear_whole_window = True
            self.SetScrollbars(1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1], 0, 0, True) # workaround a bug where whole screen doesn't clear if you are scrolled to the right and y is non scrolled, and you zoom out - you see a screen fragment not erased
        self.DebugSizez("zoom")

        self.Refresh()

    def OnResize (self, event):   # ANDY  interesting - GetVirtualSize grows when resize frame
        self.DebugSizez("resize")
        if self.NeedToClear():
            self.clear_whole_window = True
            self.Refresh()

    def CalcVirtSize(self):
        # VirtualSize is essentially the visible picture
        return (self.maxWidth*self.zoomscale, self.maxHeight*self.zoomscale)
    
    def NeedToClear(self):
        # Since VirtualSize auto grows when resize frame, can't rely on it to know if client area is bigger than visible pic.
        # Need to rederive the original VirtualSize set when zoom calculated rather than relying on calls to self.GetVirtualSize()
        return self.GetClientSize()[0] > self.CalcVirtSize()[0] or self.GetClientSize()[1] > self.CalcVirtSize()[1]
                
    def DebugSizez(self, fromwheremsg):
        return
        if self.NeedToClear():
            msg = "!!!!!!! "
        else:
            msg = "!       "
        print msg + "(%s) NeedToClear %s GetVirtualSize %d getWidth %d GetClientSize %d self.GetViewStart() %d self.maxWidth %d " % \
        (fromwheremsg, self.NeedToClear(), self.GetVirtualSize()[0], self.getWidth(), self.GetClientSize()[0], self.GetViewStart()[0], self.maxWidth)
        
    def OnPaint(self, event):   # ANDY
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self.zoomscale, self.zoomscale)
        # since we're not buffering in this case, we have to
        # paint the whole window, potentially very time consuming.
        self.DoDrawing(dc)

    def OnLeftDown(self, event):   # ANDY some PAN ideas from http://code.google.com/p/pyslip/
        """Left mouse button down. Prepare for possible drag."""
        if event.ShiftDown():
            event.Skip()
            return
        click_posn = event.GetPositionTuple()
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        (self.last_drag_x, self.last_drag_y) = click_posn
        event.Skip()

    def OnLeftUp(self, event): # ANDY PAN
        """Left mouse button up."""
        if event.ShiftDown():
            event.Skip()
            return
        self.last_drag_x = self.last_drag_y = None
        self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        # turn off drag
        self.was_dragging = False
        # force PAINT event to remove selection box (if required)
        #self.Update()
        event.Skip()
        
    def OnMove(self, event): # ANDY PAN
        """Handle a mouse move (map drag).
        event  the mouse move event
        """
        if event.ShiftDown():
            event.Skip()
            return
        
        # for windows, set focus onto pyslip window
        # linux seems to do this automatically
        if sys.platform == 'win32' and self.FindFocus() != self:
            self.SetFocus()

        # get current mouse position
        (x, y) = event.GetPositionTuple()

        #self.RaiseMousePositionEvent((x, y))

        if event.Dragging() and event.LeftIsDown():
            # are we doing box select?
            if not self.last_drag_x is None:
                # no, just a map drag
                self.was_dragging = True
                dx = self.last_drag_x - x
                dy = self.last_drag_y - y

                #print "PAN %d %d" % (dx, dy)
                #print self.GetViewStart()
                currx, curry = self.GetViewStart()
                self.Scroll(currx+dx, curry+dy)  # Note The positions are in scroll units, not pixels, so to convert to pixels you will have to multiply by the number of pixels per scroll increment. If either parameter is -1, that position will be ignored (no change in that direction).
                #print "Scroll pan %d %d" % (currx+dx, curry+dy)

                # adjust remembered X,Y
                self.last_drag_x = x
                self.last_drag_y = y

            # redraw client area
            self.Update()

    def DoDrawing(self, dc, printing=False):

        if self.clear_whole_window:
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            self.clear_whole_window = False
        
        dc.BeginDrawing()
        dc.DrawBitmap(self.bmp, 0, 0, True)
        self.DrawSavedLines(dc)
        dc.EndDrawing()

    def DrawSavedLines(self, dc):   # PEN DRAWING
        dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
        for line in self.lines:
            for coords in line:
                apply(dc.DrawLine, coords)

    def SetXY(self, event):   # PEN DRAWING
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):    # PEN DRAWING
        newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        newpos = newpos[0]*self.GetScaleX()/self.zoomscale, newpos[1]*self.GetScaleY()/self.zoomscale
        return newpos

    def OnRightButtonEvent(self, event):   # PEN DRAWING - ANDY
        if event.ShiftDown():
            self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))
            self.lines = []
            self.Refresh()
        
    def OnLeftButtonEvent(self, event):   # PEN DRAWING
        if event.ShiftDown():
            self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

        if event.LeftDown():
            self.SetFocus()
            self.SetXY(event)
            self.curLine = []
            self.CaptureMouse()
            self.drawing = True

        elif event.Dragging() and self.drawing:
            # otherwise we'll draw directly to a wx.ClientDC
            dc = wx.ClientDC(self)
            self.PrepareDC(dc)
            dc.SetUserScale(self.zoomscale, self.zoomscale)

            dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
            coords = (self.x, self.y) + self.ConvertEventCoords(event)
            self.curLine.append(coords)    # For when we are not double buffering  #ANDY
            dc.DrawLine(*coords)
            self.SetXY(event)
            
        elif event.LeftUp() and self.drawing:
            self.lines.append(self.curLine)
            self.curLine = []
            self.ReleaseMouse()
            self.drawing = False

            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        MyCanvas(self)
        
class App(wx.App):
    def OnInit(self):
        frame = TestFrame(None, title="Andy Image Viewer")
        frame.Show(True)
        frame.Centre()
        return True
    
if __name__ == "__main__":
    app = App(0)
    app.MainLoop()
    
    
    

