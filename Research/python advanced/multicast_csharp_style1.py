## {{{ http://code.activestate.com/recipes/410686/ (r7)
"""
This recipe differs from Multiplex in that arbitrarily named event handlers are
bound to an arbitrarily named event, whereas Mutliplex dispatches a call of the
form multiplex.f() to the method f in every object in the Multiplex.

ANDY COMMENTARY:
This version you add actual functions as observers.
The functions can have parameters, so you better be sure the subject and
observer match up in their expectations in this regard.
"""

######################################################################
##
## Events
##
######################################################################


class Events:
    def __getattr__(self, name):
        if hasattr(self.__class__, "__events__"):
            assert name in self.__class__.__events__, "Event '%s' is not declared" % name
        self.__dict__[name] = ev = _EventSlot(name)
        return ev

    def __repr__(self):
        return "Events" + str(list(self))

    __str__ = __repr__

    def __len__(self):
        return NotImplemented

    def __iter__(self):
        def gen(dictitems=list(self.__dict__.items())):
            for attr, val in dictitems:
                if isinstance(val, _EventSlot):
                    yield val

        return gen()


class _EventSlot:
    def __init__(self, name):
        self.targets = []
        self.__name__ = name

    def __repr__(self):
        return "event " + self.__name__

    def __call__(self, *a, **kw):
        for f in self.targets:
            f(*a, **kw)

    def __iadd__(self, f):
        self.targets.append(f)
        return self

    def __isub__(self, f):
        while f in self.targets:
            self.targets.remove(f)
        return self


######################################################################
##
## Demo
##
######################################################################

if __name__ == "__main__":

    class MyEvents(Events):
        __events__ = ("OnChange",)

    class ValueModel(object):
        def __init__(self):
            self.events = MyEvents()
            self.__value = None

        def __set(self, value):
            if self.__value == value:
                return
            self.__value = value
            self.events.OnChange()
            ##self.events.OnChange2() # would fail

        def __get(self):
            return self.__value

        Value = property(__get, __set, None, "The actual value")

    class SillyView(object):
        def __init__(self, model):
            self.model = model
            model.events.OnChange += self.DisplayValue
            ##model.events.OnChange2 += self.DisplayValue # would raise exeception

        def DisplayValue(self):
            print(self.model.Value)

    model = ValueModel()
    view = SillyView(model)

    print("\n--- Events Demo ---")
    # Events in action
    for i in range(5):
        model.Value = 2 * i + 1
    # Events introspection
    print(model.events)
    for event in model.events:
        print(event)
    ## end of http://code.activestate.com/recipes/410686/ }}}

    # Andy's tests

    print("Andy's tests:")

    class AndyEvents(Events):
        __events__ = ("OnChange",)

    class Model:
        def __init__(self):
            self.value = 0
            self.observers = AndyEvents()

        def addObserver(self, f):
            self.observers.OnChange += f

        def addValue(self, v):
            self.value += v
            self.observers.OnChange(v, self.value)

    class Observer1:
        def notifyOfModelValueChange(self, value, new_total_value):
            print(
                "Observer1 got notified, added value %(value)4d - total now %(new_total_value)4d"
                % vars()
            )

    model = Model()
    o1 = Observer1()
    model.addObserver(
        o1.notifyOfModelValueChange
    )  # Use model's addobserver method which wraps the use of the multicast
    model.addValue(10)
    model.addValue(605)

    class Observer2:
        def __init__(self):
            self.num_calls = 0

        def notifyOfModelValueChange(self, value, new_total_value):
            self.num_calls += 1
            print("Observer2 got notified %2d times" % self.num_calls)

    o2 = Observer2()
    model.observers.OnChange += o2.notifyOfModelValueChange  # Or access the multicast directly.
    model.addValue(100)
    model.addValue(2000)

    model.observers.OnChange -= o1.notifyOfModelValueChange  # Or access the multicast directly.
    model.addValue(33)
    model.addValue(44)
