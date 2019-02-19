# Controller

# Uses a CmdInvoker to create command instances, assigns the
# context object and then runs the command via the command manager.

if __name__ == "__main__":
    import sys

    if ".." not in sys.path:
        sys.path.append("..")

from common.command_pattern import CommandManager

from .cmds.diagnostics import *
from .cmds.deletion import *
from .cmds.insertion import *
from .cmds.selection import *
from .cmds.filemgmt import *
from .cmds.layouts import *
from .cmds.colouring import *
from .cmds.line_edge_type import *

# TODO: Perhaps can add these modules to the globals within the
# invoker class, to avoid having to import each module explicitly?

# IMPORTANT: Command Invoker has to be defined here in order to access the scope
# of the above cmds modules


class CmdInvoker:  # version 4 - see pyNsource\trunk\Research\python advanced\command_invokers1.py
    """
    When you call any method on an instance of this invoker class, the method is
    interpreted as the name of a command class to be instantiated. Parameters in
    the method call are used as parameters to the constructor. After the command
    class is instantiated, a context object is attached, and the command passed
    to a command manager to be run. No extra parameters are injected into the
    constructor or to the execute() call.
    """

    def __init__(self, context, cmd_mgr):
        self.context = context
        self.cmd_mgr = cmd_mgr

    # needs to return a callable function which will then be called by python,
    # with the arguments to the original call to '.method/klass' call.
    def __getattr__(self, klass):
        def cmd_invoker_f(*args, **kwargs):
            cmd = eval(klass + "(*args, **kwargs)", globals(), locals())
            cmd.context = self.context
            self.cmd_mgr.run(cmd)

        return cmd_invoker_f


class Controller:
    def __init__(self, app):
        self.app = app

        self.cmd_mgr = CommandManager(100)
        self.invoker = CmdInvoker(self.app.context, self.cmd_mgr)

    """
    # Events from Gui
    

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
        try:
            self.app.MainThreadMutexGuiEnter()
            thing = self.model.AddThing(info) # will typically indirectly update a gui
            if thing:
                return thing.to_dict()
            return "Couldn't create thing with info %(info)s" % vars()
        finally:
            self.app.MainThreadMutexGuiLeave()

    def CmdModifyThing(self, id, info):
        try:
            self.app.MainThreadMutexGuiEnter()
            thing = self.model.FindThing(int(id))
            if thing:
                self.model.AddInfoToThing(thing, info)
                return thing.to_dict()
            return "Thing id %(id)s not found" % vars()
        finally:
            self.app.MainThreadMutexGuiLeave()

    def CmdDeleteThing(self, id):
        try:
            self.app.MainThreadMutexGuiEnter()
            thing = self.model.FindThing(int(id))
            if thing:
                self.model.DeleteThing(thing)
                return "ok deleted"
            return "Thing id %(id)s not found" % vars()
        finally:
            self.app.MainThreadMutexGuiLeave()
    """

    """
    Used to redirect via app - lets not do this as too indirect.
    let server see app.controller  !!
    """
    # def CmdGetThingsAsDict(self):
    #    return self.controller.CmdGetThingsAsJson()
    #
    # def CmdGetThingAsDict(self, id):
    #    return self.controller.CmdGetThingAsJson(id)


if __name__ == "__main__":

    class CmdMgr:
        def run(self, cmd):
            cmd.execute()

    invoker = CmdInvoker(context={"a": 4}, cmd_mgr=CmdMgr())

    class CmdWoody:
        ugg = 1

        def __init__(self, num, num2=98):
            # self.context = context
            self.num = num
            self.num2 = num2

        def execute(self):
            print(
                "hi from Woody and context is %(context)s and num is %(num)d and num2 is %(num2)d"
                % self.__dict__
            )

    invoker.CmdWoody(
        100
    )  # instantiates class CmdWoody with constructor value (100) and calls execute() on it
    invoker.CmdWoody(100, 97)

    # Test again with base class idea

    class CmdBase:
        def setContext(self, context):
            self.context = context

        def execute(self):
            raise RuntimeError("virtual")

        def redo(self):
            self.execute()

    class CmdBob(CmdBase):
        def __init__(self, num, num2=98):
            self.num = num
            self.num2 = num2

        def execute(self):
            assert self.context
            print(
                "hi from Bob and context is %(context)s and num is %(num)d and num2 is %(num2)d"
                % self.__dict__
            )

    invoker.CmdBob(
        100
    )  # instantiates class CmdBob with constructor value (100) and calls execute() on it
    invoker.CmdBob(100, 97)

    # Using command outside of the invoker framework
    c = CmdBob(100, 88)
    c.setContext({"a": 44})  # Need to do this if not using the framework
    c.execute()

    print("done")
