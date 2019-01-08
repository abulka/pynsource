# Various ways of using subverting method calling syntax and using it to
# instantiate command objects instead - and call execute on them.


class CmdInvoker1:
    """
    A version which 
    instantiates class 'klass' and call 'execute()' on it
    # passing 'context' as first param and then any other params supplied here.
    """

    def __init__(self, context):
        self.context = context

    # needs to return a callable function which will then be called by python,
    # with the arguments to the original 'method' call.
    def __getattr__(self, klass):
        # print klass, type(klass)
        def broadcaster(*args, **kwargs):
            o = eval(klass + "()")
            # print o, type(o)
            func = getattr(o, "execute", None)
            # print args, type(args)
            args2 = list(args)
            args2.insert(0, self.context)
            if func and callable(func):
                # func(*args, **kwargs)
                func(*args2, **kwargs)

        return broadcaster


class CmdFred:
    ugg = 1

    def execute(self, context):
        print("hi from Fred and context is", context)


invoker = CmdInvoker1(context={"a": 1})
invoker.CmdFred()  # instantiates class CmdFred and calls execute(context, ...) on it


class CmdInvoker2:
    """
    A version which 
    instantiates class 'klass' with the constructor being passed
    self.context
    and calls 'execute()' on it
    passing on all params
    """

    def __init__(self, context):
        self.context = context

    # needs to return a callable function which will then be called by python,
    # with the arguments to the original call to '.method/klass' call.
    def __getattr__(self, klass):
        # print klass, type(klass)
        def broadcaster(*args, **kwargs):
            o = eval(
                klass + "(self.context)", dict(list(globals().items()) + [("self", self)])
            )  # http://stackoverflow.com/questions/7349785/eval-calling-lambda-dont-see-self

            # print o, type(o)
            func = getattr(o, "execute", None)
            # print args, type(args)
            # args2 = list(args)
            # args2.insert(0, self.context)
            if func and callable(func):
                func(*args, **kwargs)
                # func(*args2, **kwargs)

        return broadcaster


class CmdMary:
    def __init__(self, context):
        self.context = context

    ugg = 1

    def execute(self):
        print("hi from Mary and context is", self.context)


invoker = CmdInvoker2(context={"a": 2})
invoker.CmdMary()  # instantiates class CmdMary and calls execute(...) on it


class CmdInvoker3:
    """
    A version which 
    instantiates class 'klass' with the constructor being passed i.e.
        self.context
    and passes cmd instance to a command manager which calls 'execute()'
    No passing of params - since command pattern doesn't support this.
    Get all the params in there using the command constructor please.
    """

    def __init__(self, context, cmd_mgr):
        self.context = context
        self.cmd_mgr = cmd_mgr

    # needs to return a callable function which will then be called by python,
    # with the arguments to the original call to '.method/klass' call.
    #
    def __getattr__(self, klass):
        def broadcaster(*args, **kwargs):
            # the g supplies the namespace in which the eval operates, which not only
            # needs to pick up the command class, but also the self, args, kwargs
            # which need to be manually injected into g for some reason because they are locals
            #
            # g = dict(globals().items() + [('self', self), ('args', args), ('kwargs', kwargs)])  # http://stackoverflow.com/questions/7349785/eval-calling-lambda-dont-see-self
            # cmd = eval(klass+'(self.context, *args, **kwargs)', g)

            cmd = eval(klass + "(self.context, *args, **kwargs)", globals(), locals())

            self.cmd_mgr.run(cmd)

        return broadcaster


class CmdMgr:
    def run(self, cmd):
        cmd.execute()


# print "-"*200
invoker = CmdInvoker3(context={"a": 3}, cmd_mgr=CmdMgr())
invoker.CmdMary()  # instantiates class CmdMary and calls execute() on it - NO PARAMS !

# Try some paramters now


class CmdSam:
    ugg = 1

    def __init__(self, context, num, num2=98):
        self.context = context
        self.num = num
        self.num2 = num2

    def execute(self):
        print(
            "hi from Sam and context is %(context)s and num is %(num)d and num2 is %(num2)d"
            % self.__dict__
        )


invoker.CmdSam(
    100
)  # instantiates class CmdSam with constructor value (100) and calls execute() on it
invoker.CmdSam(100, 97)
invoker.CmdSam(100, num2=96)


# Experimental version where context is plugged in later, rather than being on
# the constructor.  The benefit of this version is that command classes would
# not have to be constantly call the base class to
# so that the base class sets the context in the base constructor.
# Is this saving worth it?
# Probably - when creating a constructor for any command, just ignore
# base class super calls.


class CmdInvoker4:
    """
    When you call any method on an instance of this invoker class, the method is
    interpreted as the name of a command class to be instantiated. Parameters in
    the method call are used as paramters to the constructor. After the command
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
        def broadcaster(*args, **kwargs):
            cmd = eval(klass + "(*args, **kwargs)", globals(), locals())
            cmd.context = self.context
            self.cmd_mgr.run(cmd)

        return broadcaster


invoker = CmdInvoker4(context={"a": 4}, cmd_mgr=CmdMgr())


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
