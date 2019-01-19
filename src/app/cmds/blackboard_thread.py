# LongRunningTasks - first example - threading
# http://wiki.wxpython.org/LongRunningTasks

from threading import *
import wx

# Button definitions
ID_START = wx.NewId()
ID_STOP = wx.NewId()

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, statusmsg=None, logmsg=None, progress=-1, shouldStop=False, cmd=None):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)

        self.logmsg = logmsg
        self.statusmsg = statusmsg
        self.progress = progress
        self.shouldStop = shouldStop
        self.cmd = cmd

    def __str__(self):
        return (
            f"ResultEvent: "
            f"shouldStop={str(self.shouldStop):<6}"
            f"progress={self.progress if self.progress is not None else '':<2} "
            f"cmd={self.cmd if self.cmd is not None else '':<25} "
            f"statusmsg={self.statusmsg if self.statusmsg is not None else '':<15} "
            f"logmsg={self.logmsg if self.logmsg is not None else '':<30} "
        )


# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""

    def __init__(self, notify_window, blackboard, num_attempts):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = False
        self.blackboard = blackboard
        self.NUM_BLACKBOARD_ATTEMPTS = num_attempts
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def Cmd(self, cmd):
        wx.PostEvent(self._notify_window, ResultEvent(cmd=cmd))

    def Log(self, logmsg):
        wx.PostEvent(self._notify_window, ResultEvent(logmsg=logmsg))

    def CheckContinue(self, statusmsg=None, logmsg=None, progress=-1):
        # print statusmsg, logmsg
        if self._want_abort:
            return False
        else:
            wx.PostEvent(self._notify_window, ResultEvent(statusmsg, logmsg, progress))
            return True

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable

        if self.blackboard:
            self.blackboard.outer_thread = self
            self.blackboard.LayoutMultipleChooseBest(numlayouts=self.NUM_BLACKBOARD_ATTEMPTS)

        if self._want_abort:
            # Use a result with shouldStop set to true
            # to acknowledge the abort
            # (of course you can use whatever you'd like or even
            # a separate event type)
            wx.PostEvent(
                self._notify_window, ResultEvent(statusmsg="Layout aborted", shouldStop=True)
            )
            return

        # Here's where the result would be returned
        wx.PostEvent(
            self._notify_window,
            ResultEvent(
                statusmsg="Layout complete",
                progress=self.NUM_BLACKBOARD_ATTEMPTS + 1,
                shouldStop=True,
            ),
        )
        # self.GoodHalt()

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = True
