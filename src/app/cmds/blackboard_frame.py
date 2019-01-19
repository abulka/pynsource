# LongRunningTasks - first example - threading
# http://wiki.wxpython.org/LongRunningTasks

import time
from threading import *
import wx

from .blackboard_thread import WorkerThread, ResultEvent, EVT_RESULT

if __name__ == "__main__":
    import sys

    sys.path.append("../..")

# GUI Frame class that spins off the worker thread
from dialogs.FrameDeepLayout import FrameDeepLayout

SHOW_FINAL_LAYOUT_ONLY = False


class MainBlackboardFrame(FrameDeepLayout):
    def __init__(self, *args, **kwargs):
        super(MainBlackboardFrame, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        self.status = self.m_staticText3
        self.progressbar = self.m_gauge1

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)
        self.Bind(
            wx.EVT_CHAR_HOOK, self.onKeyPress
        )  # http://stackoverflow.com/questions/3570254/in-wxpython-how-do-you-bind-a-evt-key-down-event-to-the-whole-window
        self.working = False

        # And indicate we don't have a worker thread yet
        self.worker = None
        self.blackboard = None

    def Start(self, num_attempts):
        wx.CallAfter(self.progressbar.SetRange, num_attempts + 1)
        wx.CallAfter(
            self.progressbar.SetValue, 1
        )  # range is 0..num_attempts inclusive. 0 shows no progress.
        wx.CallAfter(self.btnCancelClose.SetFocus)

        """Start Computation."""
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            wx.CallAfter(self.status.SetLabel, "Starting Layout")
            self.worker = WorkerThread(self, self.blackboard, num_attempts)

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html

        if self.working:
            event.Skip()
            return
        self.working = True

        if keycode == wx.WXK_ESCAPE:
            print("ESC key detected in Blackboard: Abort Layout")
            self.OnClose(None)

        self.working = False
        event.Skip()

    def StopComputation(self):
        """Stop Computation."""
        # Flag the worker thread to stop if running
        if self.worker:
            wx.CallAfter(self.status.SetLabel, "Trying to abort")
            self.worker.abort()

    def OnClose(self, event):
        self.StopComputation()
        wx.CallLater(500, self.Destroy)

    def OnCancelClick(self, event):
        if self.btnCancelClose.GetLabel() == "Close":
            self.Destroy()
        self.StopComputation()
        wx.CallAfter(self.btnCancelClose.SetLabel, "Close")

    def SetBlackboardObject(self, b):
        self.blackboard = b

    def OnResult(self, event):
        """Show Result status."""
        # print(event)  # uncomment this to watch our custom events come streaming in

        def log(msg):
            wx.CallAfter(self.m_textCtrl1.AppendText, msg + "\n")

        if event.logmsg:
            log(event.logmsg)

        if event.cmd:
            if event.cmd == "snapshot_mgr_restore_0":  # show final, best result
                if SHOW_FINAL_LAYOUT_ONLY:
                    # keep dialog up and just show final result
                    wx.CallAfter(
                        self.blackboard.umlcanvas.snapshot_mgr.Restore, 0
                    )  # this causes recursion bug
                    wx.CallAfter(self.btnCancelClose.SetFocus)
                    wx.CallAfter(self.blackboard.umlcanvas.mega_refresh)
                else:
                    # close blackboard dialog and show 'animation' of worst to best layouts
                    wx.CallAfter(self.blackboard.umlcanvas.mega_from_blackboard)
                    self.Close()
            elif event.cmd == "mega_refresh":
                # dangerous to call this if mega_refresh contains wx.SafeYield - causes recursion
                wx.CallAfter(self.blackboard.umlcanvas.mega_refresh)

        if event.statusmsg:
            wx.CallAfter(self.status.SetLabel, event.statusmsg)
            log("** " + event.statusmsg)

        if event.progress != -1:
            wx.CallAfter(self.progressbar.SetValue, event.progress)

        if event.shouldStop:
            # the worker is done
            self.worker = None

            wx.CallAfter(self.btnCancelClose.SetLabel, "Close")
            # self.Destroy()  # auto close the frame


if __name__ == "__main__":
    from time import sleep

    class MockLayoutBlackboard:
        @property
        def kill_layout(self):
            if not self.outer_thread.CheckContinue():
                return True
            else:
                return False

        @kill_layout.setter
        def kill_layout(self, value):
            pass

        def LayoutMultipleChooseBest(self, numlayouts=3):
            for i in range(numlayouts):
                sleep(1)
                progress_val = (
                    i + 1
                )  # range is 1..n inclusive whereas for loop is 0..n-1 excluding n, so adjust by adding 1 for visual progress
                if not self.outer_thread.CheckContinue(
                    statusmsg="Layout #%d of %d" % (progress_val, numlayouts), progress=progress_val
                ):
                    break

                # Do a layout
                self.outer_thread.Log("spring layout started")

                sleep(0.4)

    class MainApp(wx.App):
        """Class Main App."""

        def OnInit(self):
            """Init Main App."""
            self.frame = MainBlackboardFrame(None)
            self.frame.Show(True)
            self.SetTopWindow(self.frame)

            b = (
                MockLayoutBlackboard()
            )  # LayoutBlackboard(graph=self.context.displaymodel.graph, umlcanvas=self.context.umlcanvas)

            self.frame.SetBlackboardObject(b)

            self.frame.Start(6)
            return True

    if __name__ == "__main__":
        app = MainApp(0)
        app.MainLoop()
