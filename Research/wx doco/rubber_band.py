import wx
from pydbg import dbg

class SelectableFrame(wx.Frame):

    c1 = None
    c2 = None

    def __init__(self, parent=None, id=-1, title=""):
        # wx.Frame.__init__(self, parent, id, title, size=wx.DisplaySize())
        wx.Frame.__init__(self, parent, id, title, size=(800,800))

        self.panel = wx.Panel(self, size=self.GetSize())

        self.panel.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRDown)
        self.panel.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))

        # self.SetTransparent(50)

    def OnMouseMove(self, event):
        if event.Dragging():
            self.c2 = event.GetPosition()
        self.Refresh()
        #if event.Dragging() and event.LeftIsDown():
        #    self.c2 = event.GetPosition()
        #    self.Refresh()

    def OnMouseDown(self, event):
        self.c1 = event.GetPosition()
        
    def OnMouseRDown(self, event):
        self.c1 = event.GetPosition()

    def OnMouseUp(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.c2 = None  # ANDY
        print("mouse up")
        dbg(self.c1)
        dbg(self.c2)
        self.Refresh()

    def OnPaint(self, event):
        # dbg(self.c1)
        # dbg(self.c2)
        if self.c1 is None or self.c2 is None: return

        dc = wx.PaintDC(self.panel)

        # Fun - draw crosshairs
        maxx = 2000
        maxy = 2000
        dc.SetPen(wx.Pen('BLACK', 1, wx.DOT))
        dc.SetBrush(wx.Brush("BLACK", wx.TRANSPARENT))
        dc.DrawLine(0, self.c2.y, maxx, self.c2.y)  # horizontal line
        dc.DrawLine(self.c2.x, 0, self.c2.x, maxy)  # vert line

        # Draw rubber band
        dc.SetPen(wx.Pen('red', 1, wx.SHORT_DASH))
        dc.SetBrush(wx.Brush("BLACK", wx.TRANSPARENT))
        dc.DrawRectangle(self.c1.x, self.c1.y, self.c2.x - self.c1.x, self.c2.y - self.c1.y)

    def PrintPosition(self, pos):
        return str(pos.x) + " " + str(pos.y)


class MyApp(wx.App):

    def OnInit(self):
        frame = SelectableFrame()
        frame.Show(True)
        self.SetTopWindow(frame)

        return True


app = MyApp(0)
app.MainLoop()
# del app

