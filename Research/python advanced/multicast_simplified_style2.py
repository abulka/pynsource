class multicast_1:
    def __init__(self):
        self.objects = []

    def add(self, o):
        self.objects.append(o)

    def __getattr__(self, method):
        self.method = method
        return self.broadcaster
    
    def broadcaster(self, *args, **kwargs):
        for o in self.objects:
            func = getattr(o, self.method, None)
            if func:
                func(*args, **kwargs)

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

#class multicast:
#    def __init__(self):
#        self.objects = []
#
#    def add(self, o):
#        self.objects.append(o)
#
#    # needs to return a callable function which will then be called by python,
#    # with the arguments to the original 'method' call.
#    def __getattr__(self, method): 
#        def broadcaster(*args, **kwargs):
#            print args, kwargs
#            for o in self.objects:
#                func = getattr(o, method, None)
#                if func:
#                    if callable(func):
#                        func(*args, **kwargs)
#                    else: # treat as attribute assignment
#                        # DOESNT WORK BECAUSE CAN'T ACCESS THE VALUE BEING ASSIGNED
#                        setattr(o, method, 50) # ASSIGNING 50 COS CAN'T THINK OF ANYTHING ELSE
#        return broadcaster
         
    
#class Thing(object):
#    def __init__(self):
#        self.__missing_method_name = None # Hack!
#    
#    def __getattribute__(self, name):
#        return object.__getattribute__(self, name)
#    
#    def __getattr__(self, name):
#        self.__missing_method_name = name # Could also be a property
#        return getattr(self, '__methodmissing__')
#
#    def __methodmissing__(self, *args, **kwargs):
#        print "Missing method %s called (args = %s) and (kwargs = %s)" % (self.__missing_method_name, str(args), str(kwargs))
#
#t = Thing()
#t.badness(123, 'an arg', blah="another argument here", zesty="woot")

class Fred:
    ugg = 1
    def hi(self):
        print("hi from Fred")
    def count(self, n):
      for i in range(n): print(i)

class Mary:
    def hi(self):
        print("hi from Mary")
    def count(self, n):
      for i in range(n): print(i+100)
  
observers = multicast()
observers.add(Fred())
observers.add(Mary())
observers.hi()
observers.count(5)
observers.ugg()   # ugg method doesn't exist, so no calls made

#observers.someattr = 100

print("done")

