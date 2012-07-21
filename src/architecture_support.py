#
# Support Stuff
#

# Multicasting based on objects
# My own simpler version -
# see http://code.activestate.com/recipes/52289-multicasting-on-objects/

class multicast:
    def __init__(self):
        self.objects = []

    def add(self, o):
        self.objects.append(o)

    # needs to return a callable function which will then be called by python,
    # with the arguments to the original 'method' call.
    def __getattr__(self, method):
        print method
        def broadcaster(*args, **kwargs):
            for o in self.objects:
                func = getattr(o, method, None)
                if func and callable(func):
                    func(*args, **kwargs)
        return broadcaster
    

# Misc Decorators

class countcalls(object):
    "Decorator that keeps track of the number of times a function is called."

    __instances = {}

    def __init__(self, f):
        self.__f = f
        self.__numcalls = 0
        countcalls.__instances[f] = self

    def __call__(self, *args, **kwargs):
        self.__numcalls += 1
        return self.__f(*args, **kwargs)

    def count(self):
        "Return the number of times the function f was called."
        return countcalls.__instances[self.__f].__numcalls
        #return self.__numcalls # ANDY - THIS WORKS TOO!? SO WHY IS THE ABOVE COMPLICATED THING USED?

    @staticmethod
    def counts():
        "Return a dict of {function: # of calls} for all registered functions."
        return dict([(f.__name__, countcalls.__instances[f].__numcalls) for f in countcalls.__instances])


dodumpargs = True

def dump_args(func):
    "This decorator dumps out the arguments passed to a function before calling it"
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name

    if not dodumpargs:
        return func

    def echo_func(*args,**kwargs):
        print fname, ":", ', '.join(
            '%s=%r' % entry
            for entry in zip(argnames,args) + kwargs.items())
        return func(*args, **kwargs)
    return echo_func
