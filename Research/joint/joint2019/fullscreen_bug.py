import wx
# import wx.lib.ogl as ogl
import wx.html2 as webview
import time
import random

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Demo", size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # put stuff into sizer

        self.original = wx.ClientDisplayRect()

        self.pnl = DrawPanel(self, self.draw_test)

        self.wv = wx.TextCtrl(self, style = wx.TE_MULTILINE)
        font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')
        self.wv.SetFont(font1)

        self.sp = wx.TextCtrl(self)
        font2 = wx.Font(28, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')
        self.sp.SetFont(font2)

        sizer.Add(self.pnl, 2, wx.GROW)
        sizer.Add( self.sp, 1, wx.ALL|wx.EXPAND, 5 )
        sizer.Add(self.wv, 2, wx.GROW)
        self.SetSizer( sizer )
        self.Layout()

        self.wv.WriteText(f"DisplaySize() = {wx.DisplaySize()}\n--------\n")
        self.rectangles = None

        self.Bind(wx.EVT_SIZE, self.OnResizeFrame)
        self.Bind(wx.EVT_IDLE, self.idle)

        # apply sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Show(1)


    def idle(self, event):
        self.pnl.Refresh()

    def OnResizeFrame(self, event):

        # Proportionally constrained resize.  Nice trick from http://stackoverflow.com/questions/6005960/resizing-a-wxpython-window
        # hsize = event.GetSize()[0] * 0.75
        # self.frame.SetSizeHints(minW=-1, minH=hsize, maxH=hsize)
        # self.frame.SetTitle(str(event.GetSize()))

        # print("GetClientSize()", self.GetClientSize(), wx.ClientDisplayRect(), wx.DisplaySize())
        msg = f" <--- ClientDisplayRect() changed/broken?" if self.original != wx.ClientDisplayRect() else ""
        self.wv.WriteText(f"frame.GetClientSize() {self.GetClientSize()}     "
                          f"wx.ClientDisplayRect() {wx.ClientDisplayRect()} {msg}\n"
                          )
        # if self.original != wx.ClientDisplayRect():
        #     self.wv.WriteText(f"BROKEN!!! ClientDisplayRect has always been {self.original} but now is {wx.ClientDisplayRect} !!?\n")

        if self.GetClientSize() == wx.DisplaySize():
            print("FULLSCREEN!!!")

        # Make random rectangles
        if not self.rectangles:
            w = self.GetClientSize().width
            h = self.GetClientSize().height
            if w < 600: w = 600
            if h < 400: h = 400
            self.rectangles = makeRandomRectangles(w, h, 200)

        event.Skip()


    def draw_test(self, dc):
        # Draw speed test
        start = time.time()
        dc.SetPen( wx.Pen("BLACK",1) )
        dc.SetBrush( wx.Brush("RED") )
        dc.DrawEllipseList(self.rectangles)
        msg = "DrawTime: %0.2f seconds" % (time.time() - start)
        # print(msg)
        self.sp.SetValue(msg)

class DrawPanel(wx.Panel):
    def __init__(self, parent, drawFun, log=None):
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundColour(wx.WHITE)

        self.log = log
        self.drawFun = drawFun
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.Clear()
        self.drawFun(dc)

def makeRandomRectangles(num, W, H):
    rects = []

    for i in range(num):
        w = random.randint(10, int(W/2))
        h = random.randint(10, int(H/2))
        x = random.randint(0, W - w)
        y = random.randint(0, H - h)
        rects.append( (x, y, w, h) )

    return rects

app = wx.App()
frame = AppFrame()
app.MainLoop()
app.Destroy()
