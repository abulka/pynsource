# LongRunningTasks - second example - yield
# http://wiki.wxpython.org/LongRunningTasks

"""
The second approach, using wxYield, should be fine too - just add a call to
wxYield() somewhere within the computation code such that it executes
periodically. At that point, any pending window events will be dispatched
(permitting the window to refresh, process button presses, etc...). Then, it's
similar to the above in that you set a flag so that when the original code gets
control after the wxYield() returns it knows to stop processing.

As with the threading case, since all events go through during the wxYield() you
need to protect against trying to run the same operation twice.

Here's the equivalent of the above but placing the computation right inside the
main window class. Note that one difference is that unlike with threading, the
responsiveness of your GUI is now directly related to how frequently you call
wxYield, so you may have delays refreshing your window dependent on that
frequency. You should notice that this is a bit more sluggish with its frequency
of a wxYield() each second.
"""

import time
import wx

# Button definitions
ID_START = wx.NewId()
ID_STOP = wx.NewId()

# GUI Frame class that spins off the worker thread
class MainFrame(wx.Frame):
    """Class MainFrame."""
    def __init__(self, parent, id):
        """Create the MainFrame."""
        wx.Frame.__init__(self, parent, id, 'wxYield Test')

        # Dumb sample frame with two buttons
        wx.Button(self, ID_START, 'Start', pos=(0,0))
        wx.Button(self, ID_STOP, 'Stop', pos=(0,50))
        self.status = wx.StaticText(self, -1, '', pos=(0,100))

        self.Bind (wx.EVT_BUTTON, self.OnStart, id=ID_START)
        self.Bind (wx.EVT_BUTTON, self.OnStop, id=ID_STOP)

        # Indicate we aren't working on it yet
        self.working = 0

    def OnStart(self, event):
        """Start Computation."""
        # Start the processing - this simulates a loop - you need to call
        # wx.Yield at some periodic interval.
        if not self.working:
            self.status.SetLabel('Starting Computation')
            self.working = 1
            self.need_abort = 0

            for i in range(10):
                time.sleep(1)
                wx.Yield()
                if self.need_abort:
                    self.status.SetLabel('Computation aborted')
                    break
            else:
                # Here's where you would process the result
                # Note you should only do this if not aborted.
                self.status.SetLabel('Computation Completed')

            # In either event, we aren't running any more
            self.working = 0

    def OnStop(self, event):
        """Stop Computation."""
        if self.working:
            self.status.SetLabel('Trying to abort computation')
            self.need_abort = 1

class MainApp(wx.App):
    """Class Main App."""
    def OnInit(self):
        """Init Main App."""
        self.frame = MainFrame(None,-1)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = MainApp(0)
    app.MainLoop()