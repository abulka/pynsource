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
    def __init__(self, data, data_shouldStop):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
        self.data_shouldStop = data_shouldStop

# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, blackboard):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.blackboard = blackboard
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def CheckContinue(self, progress=None):
        if self._want_abort:
            return False
        else:
            if progress:
                wx.PostEvent(self._notify_window, ResultEvent(progress, data_shouldStop=False))
            return True
    
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        
        if self.blackboard:
            self.blackboard.outer_thread = self
            self.blackboard.LayoutMultipleChooseBest(4)
            
        if self._want_abort:
            # Use a result of None to acknowledge the abort (of
            # course you can use whatever you'd like or even
            # a separate event type)
            wx.PostEvent(self._notify_window, ResultEvent(None, data_shouldStop=True))
            return
        
        # Here's where the result would be returned (this is an
        # example fixed result of the number 10, but it could be
        # any Python object)
        wx.PostEvent(self._notify_window, ResultEvent("Layout complete", data_shouldStop=True))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1


# GUI Frame class that spins off the worker thread
from dialogs.FrameDeepLayout import FrameDeepLayout
class MainBlackboardFrame(FrameDeepLayout):
    
    def __init__(self, *args, **kwargs):
        super(MainBlackboardFrame, self).__init__(*args, **kwargs) 
        self.InitUI()
        
    def InitUI(self):
        self.status = self.m_staticText3
        self.progressbar = self.m_gauge1
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self,self.OnResult)

        # And indicate we don't have a worker thread yet
        self.worker = None
        self.blackboard = None
        
    def Start(self):
        """Start Computation."""
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            self.status.SetLabel('Starting Layout')
            self.worker = WorkerThread(self, self.blackboard)
            
    def OnCancelClick( self, event ):
        print "got cancel"
        
        """Stop Computation."""
        # Flag the worker thread to stop if running
        if self.worker:
            self.status.SetLabel('Trying to abort')
            self.worker.abort()
            
        self.Destroy()
        
    def SetBlackboardObject(self, b):
        self.blackboard = b

    def OnResult(self, event):
        """Show Result status."""
        
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.status.SetLabel('Layout aborted')
        else:
            # Process results here
            self.status.SetLabel('Analysing layout: %s' % event.data)
            
            if not event.data_shouldStop:
                #print "setting progress bar to", event.data
                self.progressbar.SetValue(event.data)

        if event.data_shouldStop:
            # the worker is done
            self.worker = None
            
            self.Destroy()  # close the frame
        
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
        