# LongRunningTasks - third example - easy
# http://wiki.wxpython.org/LongRunningTasks

"""
Easiest Implementation *Ever* :)

So you say you want to perform a long running task from a wxPython GUI? Well, it
don't get no simpler than this! Use threads but don't mess with a separate
thread class. Make sure if you're running in the other thread that you interact
with the GUI via wx.CallAfter.

Can't get this to be interruptable!!!

"""

import wx
import _thread
from time import sleep


class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        self.label = wx.StaticText(self, label="Ready")
        self.btn = wx.Button(self, label="Start")
        self.gauge = wx.Gauge(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, proportion=1, flag=wx.EXPAND)
        sizer.Add(self.btn, proportion=0, flag=wx.EXPAND)
        sizer.Add(self.gauge, proportion=0, flag=wx.EXPAND)

        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_BUTTON, self.onButton)

        self.btn.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)  # self.Bind doesn't work
        self.working = False
        self.kill_layout = False

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html

        if self.working:
            event.Skip()
            return
        self.working = True

        if keycode == wx.WXK_ESCAPE:
            print("ESC key detected: Abort")
            self.kill_layout = True

        self.working = False
        event.Skip()

    def onButton(self, evt):
        self.btn.Enable(False)
        self.gauge.SetValue(0)
        self.label.SetLabel("Running")
        self.kill_layout = False
        _thread.start_new_thread(self.longRunning, ())

    def onLongRunDone(self):
        self.gauge.SetValue(100)
        self.label.SetLabel("Done")
        self.btn.Enable(True)

    def longRunning(self):
        """This runs in a different thread.  Sleep is used to simulate a long running task."""
        sleep(3)
        wx.Yield()
        wx.CallAfter(self.gauge.SetValue, 20)
        if self.kill_layout:
            return
        sleep(5)
        wx.Yield()
        wx.CallAfter(self.gauge.SetValue, 50)
        if self.kill_layout:
            return
        sleep(1)
        wx.Yield()
        wx.CallAfter(self.gauge.SetValue, 70)
        if self.kill_layout:
            return
        sleep(10)
        wx.Yield()
        wx.CallAfter(self.onLongRunDone)


if __name__ == "__main__":
    app = wx.PySimpleApp()
    app.TopWindow = MainFrame(None)
    app.TopWindow.Show()
    app.MainLoop()
