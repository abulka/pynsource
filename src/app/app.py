import sys
if ".." not in sys.path: sys.path.append("..")
from command_pattern import CommandManager
from controller import Controller

class App(object):
    def __init__(self, context):
        #self.model = model
        #self.server = server
        #self.gui = gui
        self.context = context
        self.controller = Controller(app=self)
        #model.app = self.controller.app = gui.app = server.app = self
        self.cmd_mgr = CommandManager(100)
        
        # Inject multicast dependencies / observers
        self.context.wxapp.observers.addObserver(self.controller)
        self.context.umlwin.observers.addObserver(self)
        #gui.observers.addObserver(self.controller)
        #model.observers.addObserver(gui)
        #model.observers.addObserver(self.controller) # diagnostic, optional
        #server.observers.addObserver(self.controller)
        
        # Inject normal dependencies
        #self.server.model = model
        
    # Housekeeping.
    # Inject multicast dependencies / observers
    # for new objects created during the lifetime of the app
    def NOTIFY_EVT_HANDLER_CREATED(self, evthandler):
        evthandler.observers.addObserver(self.controller)
        
    # Startup and Shutdown
    
    def Boot(self):
        #self.context.wxapp.app = \
        ## Everyone knows app - hmm some of these may not be necessary
        #self.context.wxapp.app = \
        #self.config.app = \
        #self.umlwin.app = \
        #self.model.app = \
        #self.snapshot_mgr.app = \
        #self.coordmapper.app = \
        #self.layouter.app = \
        #self.overlap_remover.app = \
        #self.frame.app = \
        #self.multiText.app = \
        #self.asciiart.app = \
        #                    self
        
        #self.gui.Boot()
        #self.model.Boot()
        #if self.model.size == 0:
        #    self.model.AddThing("initial thing")
        #self.server.StartServer()
        pass

    def Shutdown(self):
        #self.server.StopServer()
        pass

    # Thread control utility methods. E.g. When server thread calls in to main thread
    # which then makes triggers a GUI update in the main thread, we need to manage this
    # in wx under linux, and possibly other configurations.

    #def MainThreadMutexGuiEnter(self):
    #    self.gui.MainThreadMutexGuiEnter()
    #
    #def MainThreadMutexGuiLeave(self):
    #    self.gui.MainThreadMutexGuiLeave()

    # Some methods/properties the app has to define itself - rather than exposing
    # ring objects to one another for such trivial stuff

    #@property
    #def url_server(self):
    #    return self.server.url_server

    