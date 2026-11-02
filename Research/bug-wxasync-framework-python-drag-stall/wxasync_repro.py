"""Minimal reproducer: a wx app driven by wxasync's event loop stalls while the mouse
button is held, but only when Python is a *framework* build (macOS).

Drag inside the window in a circle for ~5 seconds and watch the per-second lines.
On a healthy interpreter they keep coming (~50/s worth of paints, "maxgap" stays
two- to three-digit ms). On the affected interpreter the lines stop for as long as
the button is held and "maxgap" jumps to thousands of ms.

Run:  LOG=/tmp/repro.log python wxasync_repro.py
Stop: close the window (or Ctrl-C).
"""
import asyncio
import os
import sys
import time

import wx
from wxasync import WxAsyncApp

LOG = os.environ.get("LOG", "/tmp/wxasync_repro.log")
log = open(LOG, "w", buffering=1)


def out(*a):
    line = " ".join(str(x) for x in a)
    print(line, file=log, flush=True)
    print(line)


out("python", sys.version.split()[0], "framework=", repr(getattr(sys, "_framework", None)),
    "wx", wx.version())
out("Drag inside the window in a circle for ~5s; watch paints/s and maxgap.")


class Frame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxasync drag reproducer", size=(900, 650), pos=(300, 160))
        self.canvas = wx.Window(self)
        self.canvas.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.canvas.Bind(wx.EVT_MOTION, self.on_motion)
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_down)
        self.canvas.Bind(wx.EVT_LEFT_UP, self.on_up)

        self.paints = self.motion = self.drag = self.down = 0
        self.maxgap = 0.0
        self.t0 = time.perf_counter()
        self.last = self.t0
        self.window_start = self.t0

        self.timer = wx.Timer(self)              # 8 ms -> should repaint ~125/s
        self.Bind(wx.EVT_TIMER, self.on_tick, self.timer)
        self.timer.Start(8)
        self.Show()

    def on_paint(self, evt):
        dc = wx.PaintDC(self.canvas)
        dc.SetBrush(wx.Brush(wx.Colour(210, 225, 255)))
        dc.DrawRectangle(20, 20, 300, 200)
        dc.DrawText("paint %d  drag %d  maxgap %.0f ms" % (self.paints, self.drag, self.maxgap), 40, 40)
        self.paints += 1

    def on_motion(self, evt):
        self.motion += 1
        if evt.Dragging():
            self.drag += 1
        self.canvas.Refresh()

    def on_down(self, evt):
        self.down += 1

    def on_up(self, evt):
        self.canvas.Refresh()

    def on_tick(self, evt):
        now = time.perf_counter()
        gap = (now - self.last) * 1000.0
        self.last = now
        self.maxgap = max(self.maxgap, gap)
        self.canvas.Refresh()
        if now - self.window_start >= 1.0:
            out("t=%5.1f paints/s=%5.1f motion=%4d drag=%4d down=%d maxgap=%6.0fms"
                % (now - self.t0,
                   self.paints / max(0.001, now - self.t0),
                   self.motion, self.drag, self.down, self.maxgap))
            self.window_start = now


class App(WxAsyncApp):
    def OnInit(self):
        self.frame = Frame()
        return True


async def main():
    app = App(0, sleep_duration=0.02)            # same 20 ms cadence Pynsource uses
    await app.MainLoop()


if __name__ == "__main__":
    asyncio.run(main())
