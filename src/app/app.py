from .controller import Controller


class App(object):
    def __init__(self, context):
        # self.model = model
        # self.server = server
        # self.gui = gui
        self.context = context

        self.controller = Controller(app=self)
        self.run = self.controller.invoker

        # model.app = self.controller.app = gui.app = server.app = self

        # Inject multicast dependencies / observers
        # self.context.umlcanvas.observers.add(self)

        # Inject normal dependencies
        # self.server.model = model

    # Housekeeping.

    # def NOTIFY_EVT_HANDLER_CREATED(self, evthandler):
    #     # For new objects created during the lifetime of the app
    #     evthandler.app = self

    # Startup and Shutdown

    def Boot(self):
        # self.context.wxapp.app = \
        ## Everyone knows app - hmm some of these may not be necessary
        # self.context.wxapp.app = \
        # self.config.app = \
        # self.umlcanvas.app = \
        # self.model.app = \
        # self.snapshot_mgr.app = \
        # self.coordmapper.app = \
        # self.layouter.app = \
        # self.overlap_remover.app = \
        # self.frame.app = \
        # self.multiText.app = \
        # self.asciiart.app = \
        #                    self

        self.context.umlcanvas.app = self

        # self.gui.Boot()
        # self.model.Boot()
        # if self.model.size == 0:
        #    self.model.AddThing("initial thing")
        # self.server.StartServer()
        pass

    def Shutdown(self):
        # self.server.StopServer()
        pass

    # Thread control utility methods. E.g. When server thread calls in to main thread
    # which then makes triggers a GUI update in the main thread, we need to manage this
    # in wx under linux, and possibly other configurations.

    # def MainThreadMutexGuiEnter(self):
    #    self.gui.MainThreadMutexGuiEnter()
    #
    # def MainThreadMutexGuiLeave(self):
    #    self.gui.MainThreadMutexGuiLeave()

    # Some methods/properties the app has to define itself - rather than exposing
    # ring objects to one another for such trivial stuff

    # @property
    # def url_server(self):
    #    return self.server.url_server
