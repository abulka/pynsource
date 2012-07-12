#
# Support Stuff
#

# Multicasting based on objects

import operator

class multicast(dict):
    "Class multiplexes messages to registered objects"

    def __init__(self, objs=[]):
        super(multicast, self).__init__()
        for alias, obj in objs:
            self.setdefault(alias, obj)

    def __call__(self, *args, **kwargs):
        "Invoke method attributes and return results through another multicast"
        return self.__class__( [ (alias, obj(*args, **kwargs) ) \
                for alias, obj in self.items() if callable(obj) ] )

    def __nonzero__(self):
        "A multicast is logically true if all delegate attributes are logically true"

        return operator.truth(reduce(lambda a, b: a and b, self.values(), 1))

    def __getattr__(self, name):
        "Wrap requested attributes for further processing"
        return self.__class__( [ (alias, getattr(obj, name) ) \
                for alias, obj in self.items() if hasattr(obj, name) ] )

    def __setattr__(self, name, value):
        """Wrap setting of requested attributes for further
        processing"""

        for o in self.values():
            o.setdefault(name, value)

    # Andy Modifications

    def addObserver(self, o):
        self[id(o)] = o

    def removeObserver(self, o):
        if id(o) in self:
            del self[id(o)]

# Decorators

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
