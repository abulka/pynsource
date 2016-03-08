import  wx
import sys

BUFFERED = False
ALLOW_DRAWING = True

FILE = "Images/fish1.png"
#FILE = "C:/Users/Andy/Documents/My Dropbox/Photos/Other Good1/german_autopanogiga_sample1.jpg"
# hmmm, with bigger image zoom doesnt work in buffered mode?

if BUFFERED:
    TRIMTO_VIRTUALSIZE = False   # complications in buffered mode
else:
    TRIMTO_VIRTUALSIZE = True
    
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

        self.maxWidth, self.maxHeight = max(self.maxWidth, bmp.GetSize()[0]), max(self.maxHeight, bmp.GetSize()[1])
        
        if TRIMTO_VIRTUALSIZE:
            self.maxWidth, self.maxHeight = bmp.GetSize()[0], bmp.GetSize()[1]
        print self.maxWidth, self.maxHeight
        
        mask = wx.Mask(bmp, wx.BLUE)
        bmp.SetMask(mask)
        self.bmp = bmp

        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        #self.SetScrollRate(20,20)
        self.SetScrollRate(1,1)

        # ANDY
        self.andyscale = 1.0
        self.bufferedzoom = 1.0
        self.clear_whole_window = False

        if BUFFERED:
            # Initialize the buffer bitmap.  No real DC is needed at this point.
            self.buffer = wx.EmptyBitmap(self.maxWidth, self.maxHeight)
            dc = wx.BufferedDC(None, self.buffer)
            dc.SetUserScale(self.andyscale, self.andyscale)
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            self.DoDrawing(dc)

        if ALLOW_DRAWING:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftButtonEvent)
            self.Bind(wx.EVT_LEFT_UP,   self.OnLeftButtonEvent)
            self.Bind(wx.EVT_MOTION,    self.OnLeftButtonEvent)
            self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonEvent)  # ANDY
            
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        # ANDY
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase) # ANDY
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel) # ANDY
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel2) # ANDY
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)  # ANDY
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)  # ANDY
        self.Bind(wx.EVT_MOTION, self.OnMove)  # ANDY
        self.Bind ( wx.EVT_SIZE, self.OnResize ) # ANDY
        self.was_dragging = False               # True if dragging map
        self.move_dx = 0                        # drag delta values
        self.move_dy = 0
        self.last_drag_x = None                 # previous drag position
        self.last_drag_y = None
        self.SetScrollbars(1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1])
        #print "self.GetVirtualSize", self.GetVirtualSize()

        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
        self.andywheelScroll = 0
        ##############
        
    def onKeyPress(self, event):   #ANDY
        keycode = event.GetKeyCode()
        #print keycode
        #if keycode == wx.WXK_SPACE:
        #    print "you pressed the spacebar!"
        if event.ShiftDown():
            self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))
            #self.zoom(reset=True)
        event.Skip()
        
    def onKeyUp(self, event):   #ANDY
        #print "up"
        self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        event.Skip()
        
    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight

    def OnErase(self, event):     # ANDY
        pass
    
    def OnWheel(self, event):    # ANDY
        #print "wheeeeel %s" % event.ControlDown()  # http://www.cs.cofc.edu/~jimmy/wxPython/wx153.htm#topic592
        #self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        
        #print event
        delta = event.GetWheelDelta() 
        rot = event.GetWheelRotation() 
        #print 'delta', delta, 'rot', rot
        
        if event.ControlDown():
            self.zoom(rot < 0)
        else:
            event.Skip()

    def OnWheel2(self, event):
        if event.ControlDown():
            event.Skip()
            return

## This is an example of what to do for the EVT_MOUSEWHEEL event,
## but since wx.ScrolledWindow does this already it's not
## necessary to do it ourselves.
#
# ANDY
# But since I set the ScrollRate to 1
# in order for panning to work nicely
# scrolling is too slow.  So invoke this code!!
#
        delta = event.GetWheelDelta()
        rot = event.GetWheelRotation()
        linesPer = event.GetLinesPerAction()
        #print delta, rot, linesPer
        linesPer *= 20   # ANDY trick to override the small ScrollRate
        ws = self.andywheelScroll
        ws = ws + rot
        lines = ws / delta
        ws = ws - lines * delta
        self.andywheelScroll = ws
        if lines != 0:
            lines = lines * linesPer
            vsx, vsy = self.GetViewStart()
            scrollTo = vsy - lines
            self.Scroll(-1, scrollTo)
        event.Skip()
        
        
    def zoom(self, out=True, reset=False):
        if not BUFFERED:
            out = not out  # For some reason in non buffred mode, zoom is in reverse!?
        if reset:
            self.andyscale = 1.0
        else:
            INCR = 1.3
            if out:
                self.andyscale *= INCR
                self.bufferedzoom /= INCR
            else:
                self.andyscale /= INCR
                self.bufferedzoom *= INCR
        if self.andyscale == 0:
            self.andyscale = 1.0
            self.bufferedzoom = 1.0
        #print "zoom %f bufferedzoom %f" % (self.andyscale, self.bufferedzoom)
        print "zoom %f " % self.andyscale

        if TRIMTO_VIRTUALSIZE:
            if BUFFERED:
                self.SetVirtualSize((self.maxWidth*self.bufferedzoom, self.maxHeight*self.bufferedzoom))
                self.SetScrollbars(1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1])
            else:
                if out:
                    jumptox, jumptoy = self.GetViewStart()[0]*INCR, self.GetViewStart()[1]*INCR
                else:
                    jumptox, jumptoy = self.GetViewStart()[0]/INCR, self.GetViewStart()[1]/INCR
                self.SetVirtualSize(self.CalcVirtSize())
                self.SetScrollbars(1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1], jumptox, jumptoy, True) # boolean is skip refresh or not, doesn't seem to matter
               
                # If zoom out so much you need to clear the whole window to get rid of bigger image remnants
                if self.NeedToClear():
                    self.clear_whole_window = True
                    self.SetScrollbars(1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1], 0, 0, True) # workaround a bug where whole screen doesn't clear if you are scrolled to the right and y is non scrolled, and you zoom out - you see a screen fragment not erased
                self.DebugSizez("zoom")

        # self.BufferRedraw()  # Doesn't help with quality problem nor with virtual size issues
        self.Refresh()

    def OnResize (self, event):   # ANDY  interesting - GetVirtualSize grows when resize frame
        self.DebugSizez("resize")
        if self.NeedToClear():
            self.clear_whole_window = True
            self.Refresh()

    def CalcVirtSize(self):
        # VirtualSize is essentially the visible picture
        return (self.maxWidth*self.andyscale, self.maxHeight*self.andyscale)  # if BUFFERED may need to use self.bufferedzoom instead.
    
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
        if BUFFERED:
            # Create a buffered paint DC.  It will create the real
            # wx.PaintDC and then blit the bitmap to it when dc is
            # deleted.  Since we don't need to draw anything else
            # here that's all there is to it.
            dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
            dc.SetUserScale(self.andyscale, self.andyscale)
        else:
            dc = wx.PaintDC(self)
            self.PrepareDC(dc)
            dc.SetUserScale(self.andyscale, self.andyscale)
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

        # Only gets called ONCE at startup, when in doublebuffered mode. (except when clear user drawn pen lines)
        
        #import random
        #print "++DoDrawing++ %d" % random.randint(1,99999)
        
        if not BUFFERED and self.clear_whole_window:
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            self.clear_whole_window = False
        
        dc.BeginDrawing()

        dc.DrawBitmap(self.bmp, 0, 0, True)

        dc.SetPen(wx.Pen('RED'))
        dc.DrawRectangle(5, 5, 50, 50)

        dc.SetBrush(wx.LIGHT_GREY_BRUSH)
        dc.SetPen(wx.Pen('BLUE', 4))
        dc.DrawRectangle(15, 15, 50, 50)

        dc.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL))
        dc.SetTextForeground(wx.Colour(0xFF, 0x20, 0xFF))
        te = dc.GetTextExtent("Hello World")
        dc.DrawText("Hello World", 60, 65)

        dc.SetPen(wx.Pen('VIOLET', 4))
        dc.DrawLine(5, 65+te[1], 60+te[0], 65+te[1])

        lst = [(100,110), (150,110), (150,160), (100,160)]
        dc.DrawLines(lst, -60)
        dc.SetPen(wx.GREY_PEN)
        dc.DrawPolygon(lst, 75)
        dc.SetPen(wx.GREEN_PEN)
        dc.DrawSpline(lst+[(100,100)])

        #dc.DrawBitmap(self.bmp, 200, 20, True)

        dc.SetTextForeground(wx.Colour(0, 0xFF, 0x80))
        dc.DrawText("a bitmap", 200, 85)

##         dc.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL))
##         dc.SetTextForeground("BLACK")
##         dc.DrawText("TEST this STRING", 10, 200)
##         print dc.GetFullTextExtent("TEST this STRING")

        font = wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL)
        dc.SetFont(font)
        dc.SetTextForeground(wx.BLACK)

        for a in range(0, 360, 45):
            dc.DrawRotatedText("Rotated text...", 300, 300, a)

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.BLUE_BRUSH)
        dc.DrawRectangle(50,500, 50,50)
        dc.DrawRectangle(100,500, 50,50)

        dc.SetPen(wx.Pen('RED'))
        dc.DrawEllipticArc(200,500, 50,75, 0, 90)

        if not printing:
            # This has troubles when used on a print preview in wxGTK,
            # probably something to do with the pen styles and the scaling
            # it does...
            y = 20

            for style in [wx.DOT, wx.LONG_DASH, wx.SHORT_DASH, wx.DOT_DASH, wx.USER_DASH]:
                pen = wx.Pen("DARK ORCHID", 1, style)
                if style == wx.USER_DASH:
                    pen.SetCap(wx.CAP_BUTT)
                    pen.SetDashes([1,2])
                    pen.SetColour("RED")
                dc.SetPen(pen)
                dc.DrawLine(300,y, 400,y)
                y = y + 10

        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(wx.Colour(0xFF, 0x20, 0xFF), 1, wx.SOLID))
        dc.DrawRectangle(450,50,  100,100)
        old_pen = dc.GetPen()
        new_pen = wx.Pen("BLACK", 5)
        dc.SetPen(new_pen)
        dc.DrawRectangle(470,70,  60,60)
        dc.SetPen(old_pen)
        dc.DrawRectangle(490,90, 20,20)

        dc.GradientFillLinear((20, 260, 50, 50),
                              "red", "blue")
        dc.GradientFillConcentric((20, 325, 50, 50),
                                  "red", "blue", (25,25))

        self.DrawSavedLines(dc)  # not usually necessary for buffered mode unless clearing lines,
                                 # in which case don't need this line anyway cos no lines to draw.
                                 # But it MIGHT be used when zooming.
                        
        dc.EndDrawing()


    def DrawSavedLines(self, dc):   # PEN DRAWING
        dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
        for line in self.lines:
            for coords in line:
                apply(dc.DrawLine, coords)


    def SetXY(self, event):   # PEN DRAWING
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):    # PEN DRAWING
        # ANDY
        if BUFFERED:
            newpos = self.CalcUnscrolledPosition(event.GetX()*self.GetScaleX(), event.GetY()*self.GetScaleY())
        else:
            newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
            newpos = newpos[0]*self.GetScaleX()/self.andyscale, newpos[1]*self.GetScaleY()/self.andyscale
        #print newpos
        return newpos

    
    def OnRightButtonEvent(self, event):   # PEN DRAWING - ANDY
        if event.ShiftDown():
            #print "Clearing pen lines!"
            self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))
            self.lines = []

            if BUFFERED:
                self.BufferRedraw()
            self.Refresh()
            
    def BufferRedraw(self):  # ANDY
        assert BUFFERED
        #self.buffer = wx.EmptyBitmap(self.GetVirtualSize()[0], self.GetVirtualSize()[1])
        dc = wx.BufferedDC(None, self.buffer)
        #dc.SetUserScale(self.andyscale, self.andyscale)  # DO NOT or else lose zoom
        #dc.SetUserScale(self.bufferedzoom, self.bufferedzoom)  # DO NOT or else lose zoom
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DoDrawing(dc)
        
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
            if BUFFERED:
                # If doing buffered drawing we'll just update the
                # buffer here and then refresh that portion of the
                # window, then that portion of the buffer will be
                # redrawn in the EVT_PAINT handler.
                dc = wx.BufferedDC(None, self.buffer)
                #dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)   # ANDY
                dc.SetUserScale(self.andyscale, self.andyscale)
            else:
                # otherwise we'll draw directly to a wx.ClientDC
                dc = wx.ClientDC(self)
                self.PrepareDC(dc)
                dc.SetUserScale(self.andyscale, self.andyscale)

            dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
            coords = (self.x, self.y) + self.ConvertEventCoords(event)
            self.curLine.append(coords)    # For when we are not double buffering  #ANDY
            dc.DrawLine(*coords)
            self.SetXY(event)
            
            if BUFFERED:
                # figure out what part of the window to refresh
                x1,y1, x2,y2 = dc.GetBoundingBox()
                x1,y1 = self.CalcScrolledPosition(x1, y1)
                x2,y2 = self.CalcScrolledPosition(x2, y2)
                # make a rectangle
                rect = wx.Rect()
                rect.SetTopLeft((x1,y1))
                rect.SetBottomRight((x2,y2))
                rect.Inflate(2,2)
                # refresh it
                self.RefreshRect(rect)

        elif event.LeftUp() and self.drawing:
            self.lines.append(self.curLine)
            #print "Appended line count is now %d" % len(self.lines)
            #print self.curLine
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
        frame = TestFrame(None, title="Andy wxBitmap Test")
        frame.Show(True)
        frame.Centre()
        return True
    
if __name__ == "__main__":
    app = App(0)
    app.MainLoop()
    
    
    

