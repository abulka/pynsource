"""Control: the same window driven by the *plain* wx main loop.

Expected: ALWAYS smooth, on both framework and shared-libpython builds. This is the
control that isolates wxasync's macOS loop as the trigger rather than wx itself.

Run:  LOG=/tmp/control.log python wx_control.py
"""
import os
import sys
import time

import wx

LOG = os.environ.get("LOG", "/tmp/wx_control.log")
log = open(LOG, "w", buffering=1)


def out(*a):
    line = " ".join(str(x) for x in a)
    print(line, file=log, flush=True)
    print(line)


out("python", sys.version.split()[0], "framework=", repr(getattr(sys, "_framework", None)),
    "wx", wx.version())


class Frame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="plain wx control", size=(900, 650), pos=(300, 160))
        self.canvas = wx.Window(self)
        self.canvas.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.canvas.Bind(wx.EVT_MOTION, self.on_motion)
        self.paints = self.motion = self.drag = 0
        self.maxgap = 0.0
        self.t0 = time.perf_counter()
        self.last = self.t0
        self.window_start = self.t0
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_tick, self.timer)
        self.timer.Start(8)
        self.Show()

    def on_paint(self, evt):
        dc = wx.PaintDC(self.canvas)
        dc.SetBrush(wx.Brush(wx.Colour(210, 225, 255)))
        dc.DrawRectangle(20, 20, 300, 200)
        self.paints += 1

    def on_motion(self, evt):
        self.motion += 1
        if evt.Dragging():
            self.drag += 1
        self.canvas.Refresh()

    def on_tick(self, evt):
        now = time.perf_counter()
        gap = (now - self.last) * 1000.0
        self.last = now
        self.maxgap = max(self.maxgap, gap)
        self.canvas.Refresh()
        if now - self.window_start >= 1.0:
            out("t=%5.1f paints/s=%5.1f motion=%4d drag=%4d maxgap=%6.0fms"
                % (now - self.t0, self.paints / max(0.001, now - self.t0),
                   self.motion, self.drag, self.maxgap))
            self.window_start = now


class App(wx.App):
    def OnInit(self):
        self.frame = Frame()
        return True


if __name__ == "__main__":
    App(0).MainLoop()
