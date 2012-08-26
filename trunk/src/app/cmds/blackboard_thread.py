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
        return "ResultEvent(wx.PyEvent) logmsg=%(logmsg)s statusmsg=%(statusmsg)s progress=%(progress)d shouldStop=%(shouldStop)s cmd=%(cmd)s" % self.__dict__

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
        #print statusmsg, logmsg
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
            wx.PostEvent(self._notify_window, ResultEvent(statusmsg="Layout aborted", shouldStop=True))
            return
        
        # Here's where the result would be returned
        wx.PostEvent(self._notify_window, ResultEvent(statusmsg="Layout complete", progress=self.NUM_BLACKBOARD_ATTEMPTS+1, shouldStop=True))
        #self.GoodHalt()

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = True


if __name__ == '__main__':
    import sys
    sys.path.append("../..")
    
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
        #print event
        
        def log(msg):
            self.m_textCtrl1.AppendText(msg + "\n")
            
        if event.logmsg:
            log(event.logmsg)

        if event.cmd:
            if event.cmd == 'snapshot_mgr_restore_0':
                self.blackboard.umlwin.snapshot_mgr.Restore(0)
            elif event.cmd == 'stateofthenation':
                self.blackboard.umlwin.stateofthenation()

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
        

if __name__ == '__main__':
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
              progress_val = i+1 # range is 1..n inclusive whereas for loop is 0..n-1 excluding n, so adjust by adding 1 for visual progress
              if not self.outer_thread.CheckContinue(statusmsg="Layout #%d of %d" % (progress_val, numlayouts), progress=progress_val):
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
            
            b = MockLayoutBlackboard()    # LayoutBlackboard(graph=self.context.model.graph, umlwin=self.context.umlwin)
            
            self.frame.SetBlackboardObject(b)
        
            self.frame.Start(6)
            return True
    
    if __name__ == '__main__':
        app = MainApp(0)
        app.MainLoop()
        