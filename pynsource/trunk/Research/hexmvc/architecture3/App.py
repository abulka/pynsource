from Controller import Controller

class App(object):
    def __init__(self, model, server, gui):
        self.model = model
        self.server = server
        self.gui = gui
        self.controller = Controller(model)
        model.app = self.controller.app = gui.app = server.app = self

        # Inject multicast dependencies / observers
        gui.observers.addObserver(self.controller)
        model.observers.addObserver(gui)
        model.observers.addObserver(self.controller) # diagnostic, optional
        server.observers.addObserver(self.controller)
        
        # Inject normal dependencies
        self.server.model = model
        
    # Startup and Shutdown
    
    def Boot(self):
        self.gui.Boot()
        self.model.Boot()
        if self.model.size == 0:
            self.model.AddThing("initial thing")
        self.server.StartServer()

    def Shutdown(self):
        self.server.StopServer()

    # Some methods the app has to define itself - rather than exposing
    # ring objects to one another for such trivial stuff

    @property
    def url_server(self):
        return self.server.url_server
