import wx
from pydbg import dbg
import time

from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
import asyncio
from asyncio.events import get_event_loop

ASYNC_VERSION = True

class SelectableFrame(wx.Frame):

    c1 = None
    c2 = None

    def __init__(self, parent=None, id=-1, title=""):
        # wx.Frame.__init__(self, parent, id, title, size=wx.DisplaySize())
        wx.Frame.__init__(self, parent, id, title, size=(800,800))
        self.CreateStatusBar()

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
        if ASYNC_VERSION:
            StartCoroutine(self.update_clock, self)

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

        dc = wx.PaintDC(self.panel)
        dc.SetTextForeground((204, 102, 0))  # dark orange
        dc.DrawText("right click once to start timer", 2, 2)

        if self.c1 is None or self.c2 is None: return


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

    async def async_callback(self, event):
        self.SetStatusText("Button clicked")
        await asyncio.sleep(1)
        self.SetStatusText("Working")
        await asyncio.sleep(1)
        self.SetStatusText("Completed")

    async def update_clock(self):
        while True:
            self.SetStatusText(time.strftime('%H:%M:%S'))
            await asyncio.sleep(0.5)

def main():
    class MyApp(wx.App):

        def OnInit(self):
            frame = SelectableFrame()
            frame.Show(True)
            self.SetTopWindow(frame)

            return True

    app = MyApp(0)
    app.MainLoop()
    # del app

def main_async():
    # see https://github.com/sirk390/wxasync
    app = WxAsyncApp()
    frame = SelectableFrame()
    frame.Show(True)
    app.SetTopWindow(frame)
    loop = get_event_loop()
    loop.run_until_complete(app.MainLoop())

if __name__ == "__main__":
    if ASYNC_VERSION:
        main_async()
    else:
        main()
