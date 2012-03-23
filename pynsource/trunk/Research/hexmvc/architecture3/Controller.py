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

    # Methods that adapters need, which require immediate response vs.
    # using the multicasting / eventing approach.  Typically these are
    # called by the server layer which needs to block and build a reponse there and then.

    def CmdGetThingsAsDict(self):
        things = []
        for thing in self.model.things:
            thing_json = thing.to_dict()
            thing_json["link"] = "%s/things/%d" % (self.app.url_server, thing.id)
            things.append(thing_json)
        return {"things": things}
    
    def CmdGetThingAsDict(self, id):
        thing = self.model.FindThing(int(id))
        if thing:
            return thing.to_dict()
        return "Thing id %(id)s not found" % vars()

    def CmdAddThing(self, info):
        #import wx # yuk
        #wx.MutexGuiEnter()  # prevent threading problems in linux
        self.app.MainThreadMutexGuiEnter()
        thing = self.model.AddThing(info) # will typically indirectly update a gui
        #wx.MutexGuiLeave()
        self.app.MainThreadMutexGuiLeave()
        if thing:
            return thing.to_dict()
        return "Couldn't create thing with info %(info)s" % vars()

    def CmdModifyThing(self, id, info):
        #import wx # yuk
        #wx.MutexGuiEnter()  # prevent threading problems in linux
        thing = self.model.FindThing(int(id))
        #wx.MutexGuiLeave()
        if thing:
            self.model.AddInfoToThing(thing, info)
            return thing.to_dict()
        return "Thing id %(id)s not found" % vars()

    def CmdDeleteThing(self, id):
        #import wx # yuk
        #wx.MutexGuiEnter()  # prevent threading problems in linux
        thing = self.model.FindThing(int(id))
        #wx.MutexGuiLeave()
        if thing:
            self.model.DeleteThing(thing)
            return "ok deleted"
        return "Thing id %(id)s not found" % vars()


    """
    Used to redirect via app - lets not do this as too indirect.
    let server see app.controller  !!
    """
    #def CmdGetThingsAsDict(self):
    #    return self.controller.CmdGetThingsAsJson()
    #
    #def CmdGetThingAsDict(self, id):
    #    return self.controller.CmdGetThingAsJson(id)

        