# LongRunningTasks - first example - threading
# http://wiki.wxpython.org/LongRunningTasks

import time
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
    def __init__(self, statusmsg=None, logmsg=None, progress=-1, shouldStop=False):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        
        self.logmsg = logmsg
        self.statusmsg = statusmsg
        self.progress = progress
        self.shouldStop = shouldStop

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

    def Log(self, logmsg):
        wx.PostEvent(self._notify_window, ResultEvent(logmsg=logmsg))
        
    def CheckContinue(self, statusmsg=None, logmsg=None, progress=-1):
        if self._want_abort:
            return False
        else:
            wx.PostEvent(self._notify_window, ResultEvent(statusmsg, logmsg, progress))
            return True
    #def GoodHalt(self):
        
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
            wx.PostEvent(self._notify_window, ResultEvent(statusmsg="Layout aborted", shouldStop=True))
            return
        
        # Here's where the result would be returned
        wx.PostEvent(self._notify_window, ResultEvent(statusmsg="Layout complete", progress=self.NUM_BLACKBOARD_ATTEMPTS+1, shouldStop=True))
        #self.GoodHalt()

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = True


# GUI Frame class that spins off the worker thread
from dialogs.FrameDeepLayout import FrameDeepLayout
class MainBlackboardFrame(FrameDeepLayout):
    
    def __init__(self, *args, **kwargs):
        super(MainBlackboardFrame, self).__init__(*args, **kwargs) 
        self.InitUI()
        
    def InitUI(self):
        self.status = self.m_staticText3
        self.progressbar = self.m_gauge1
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self,self.OnResult)

        # And indicate we don't have a worker thread yet
        self.worker = None
        self.blackboard = None
        
    def Start(self, num_attempts):
        self.progressbar.SetRange(num_attempts)
        self.progressbar.SetValue(1)  # range is 0..num_attempts inclusive. 0 shows no progress.
        
        """Start Computation."""
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            self.status.SetLabel('Starting Layout')
            self.worker = WorkerThread(self, self.blackboard, num_attempts)

    def StopComputation(self):
        """Stop Computation."""
        # Flag the worker thread to stop if running
        if self.worker:
            self.status.SetLabel('Trying to abort')
            self.worker.abort()
        
    def OnClose( self, event ):
        self.StopComputation()
        wx.FutureCall(500, self.Destroy)

    def OnCancelClick( self, event ):
        if self.btnCancelClose.GetLabel() == 'Close':
            self.Destroy()
        self.StopComputation()
        self.btnCancelClose.SetLabel('Close')
        
    def SetBlackboardObject(self, b):
        self.blackboard = b

    def OnResult(self, event):
        """Show Result status."""

        def log(msg):
            self.m_textCtrl1.AppendText(msg + "\n")
            
        if event.logmsg:
            log(event.logmsg)

        if event.statusmsg:
            self.status.SetLabel(event.statusmsg)
            log("** " + event.statusmsg)

        if event.progress <> -1:
            self.progressbar.SetValue(event.progress)
        
        if event.shouldStop:
            # the worker is done
            self.worker = None
            
            self.btnCancelClose.SetLabel('Close')
            #self.Destroy()  # auto close the frame
        
# GUI Frame class that spins off the worker thread
#class MainBlackboardFrame_OLD(wx.Frame):
#    """Class MainFrame."""
#    def __init__(self, parent):
#        """Create the MainFrame."""
#        wx.Frame.__init__(self, parent, wx.ID_ANY, 'Blackboard Layout Manager')
#
#        # Dumb sample frame with two buttons
#        wx.Button(self, ID_START, 'Start', pos=(0,0))
#        wx.Button(self, ID_STOP, 'Stop', pos=(0,50))
#        self.status = wx.StaticText(self, -1, '', pos=(0,100))
#
#        self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
#        self.Bind(wx.EVT_BUTTON, self.OnStop, id=ID_STOP)
#
#        # Set up event handler for any worker thread results
#        EVT_RESULT(self,self.OnResult)
#
#        # And indicate we don't have a worker thread yet
#        self.worker = None
#
#        self.blackboard = None
#
#    def SetBlackboardObject(self, b):
#        self.blackboard = b
#        
#    def Start(self):
#        pass  # use button to start
#    
#    def OnStart(self, event):
#        """Start Computation."""
#        # Trigger the worker thread unless it's already busy
#        if not self.worker:
#            self.status.SetLabel('Starting computation')
#            self.worker = WorkerThread(self, self.blackboard)
#
#
#    def OnStop(self, event):
#        """Stop Computation."""
#        # Flag the worker thread to stop if running
#        if self.worker:
#            self.status.SetLabel('Trying to abort computation')
#            self.worker.abort()
#
#    def OnResult(self, event):
#        """Show Result status."""
#        
#        if event.data is None:
#            # Thread aborted (using our convention of None return)
#            self.status.SetLabel('Computation aborted')
#        else:
#            # Process results here
#            self.status.SetLabel('Computation Result: %s' % event.data)
#
#        if event.data_shouldStop:
#            # the worker is done
#            self.worker = None
#



if __name__ == '__main__':

    class MainApp(wx.App):
        """Class Main App."""
        def OnInit(self):
            """Init Main App."""
            self.frame = MainBlackboardFrame(None)
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            return True
    
    if __name__ == '__main__':
        app = MainApp(0)
        app.MainLoop()
        