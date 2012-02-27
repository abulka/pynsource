class Controller():
    def __init__(self, model):
        self.app = None
        self.model = model

    # Events from Gui
    
    def CMD_FILE_NEW(self):
        self.model.Clear()

    def CMD_FILE_LOAD_ALL(self):
        self.model.LoadAll()

    def CMD_FILE_SAVE_ALL(self):
        self.model.SaveAll()

    def CMD_ADD_THING(self, info):
        thing = self.model.AddThing(info)

    def CMD_ADD_INFO_TO_THING(self, thing, moreinfo):
        #thing.AddInfo(moreinfo)
        self.model.AddInfoToThing(thing, moreinfo)

    def CMD_DELETE_THING(self, thing):
        self.model.DeleteThing(thing)
        
    # Other events
    
    def MODEL_THING_ADDED(self, thing, modelsize):
        print "App observer got notified, added value %(thing)s - modelsize now %(modelsize)d" % vars()
