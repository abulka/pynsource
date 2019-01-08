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
        def broadcaster(*args, **kwargs):
            for o in self.objects:
                func = getattr(o, method, None)
                if func and callable(func):
                    func(*args, **kwargs)

        return broadcaster


# Who Called me - Useful call stack analysis

import inspect


def whoami():
    return inspect.stack()[1][3]


def whosdaddy():
    return inspect.stack()[2][3]


def whosgranddaddy():
    return inspect.stack()[3][3]


def whoscalling1():
    return [inspect.stack()[i][3] for i in range(1, len(inspect.stack()))]


def whoscalling2():
    msg = ""
    TOK = " <-- "
    for i in range(2, len(inspect.stack())):
        curr = inspect.stack()[i][3]
        if curr == "MainLoop" or curr == "<lambda>":
            break
        if curr == "cmd_invoker_f":
            frame = inspect.getouterframes(inspect.currentframe())[i][0]
            argvals = inspect.getargvalues(frame)
            curr = argvals[3]["cmd"].__class__.__name__
        msg += curr + TOK
    msg = msg[0 : (len(msg) - len(TOK))]  # strip out the last TOK
    msg = "." + TOK + msg
    return msg


# Utils

import collections


def listdiff(list1, list2):
    """
    Difference between two lists, taking into account duplicates too
    """
    dups = []

    def finddups(lzt):
        y = collections.Counter(lzt)
        dups.extend([i for i in y if y[i] > 1])

    def realdiffs(a, b):
        """
        Now lets say you wanted to know which elements in the two lists did not
        overlap at all between them. This is sometimes referred to as the
        symmetric distance. The following code should serve this purpose and
        should give you "jkl" and "abc".
        http://code.hammerpig.com/find-the-difference-between-two-lists-with-python.html
        """
        c = set(a).union(set(b))
        d = set(a).intersection(set(b))
        return list(c - d)

    finddups(list1)
    finddups(list2)
    realdiffs = realdiffs(list1, list2)
    realdiffs.extend(dups)
    return realdiffs


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
        # return self.__numcalls # ANDY - THIS WORKS TOO!? SO WHY IS THE ABOVE COMPLICATED THING USED?

    @staticmethod
    def counts():
        "Return a dict of {function: # of calls} for all registered functions."
        return dict(
            [(f.__name__, countcalls.__instances[f].__numcalls) for f in countcalls.__instances]
        )


dodumpargs = True


def dump_args(func):
    "This decorator dumps out the arguments passed to a function before calling it"
    argnames = func.__code__.co_varnames[: func.__code__.co_argcount]
    fname = func.__name__

    if not dodumpargs:
        return func

    def echo_func(*args, **kwargs):
        print(
            fname,
            ":",
            ", ".join(
                "%s=%r" % entry for entry in list(zip(argnames, args)) + list(kwargs.items())
            ),
        )
        return func(*args, **kwargs)

    return echo_func
