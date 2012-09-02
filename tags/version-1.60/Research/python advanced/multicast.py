# from http://code.activestate.com/recipes/52289-multicasting-on-objects/

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

if __name__ == "__main__":
    import StringIO

    file1 = StringIO.StringIO()
    file2 = StringIO.StringIO()

    m = multicast()
    m[id(file1)] = file1
    m[id(file2)] = file2

    assert not m.closed

    m.write("Testing")
    assert file1.getvalue() == file2.getvalue() == "Testing"

    m.close()
    assert m.closed

    print "Test complete"

    # Andy's tests

    print "Andy's tests:"
    
    class Model:
        def __init__(self):
            self.value = 0
            self.observers = multicast()
        def addObserver(self, o):
            self.observers.addObserver(o)
        def addValue(self, v):
            self.value += v
            self.observers.notifyOfModelValueChange(v, self.value)
            
    class Observer1:
        def notifyOfModelValueChange(self, value, new_total_value):
            print "Observer1 got notified, added value %(value)4d - total now %(new_total_value)4d" % vars()
                
    model = Model()
    o1 = Observer1()
    model.addObserver(o1)                          # Use model's addobserver method which wraps the use of the multicast
    model.addValue(10)
    model.addValue(605)
    
    class Observer2:
        def __init__(self):
            self.num_calls = 0
        def notifyOfModelValueChange(self, value, new_total_value):
            self.num_calls += 1
            print "Observer2 got notified %2d times" % self.num_calls

    o2 = Observer2()
    model.observers.addObserver(o2)                         # Or access the multicast directly. 
    model.addValue(100)
    model.addValue(2000)
    
    model.observers.removeObserver(o1)                      # Or access the multicast directly.
    model.addValue(33)
    model.addValue(44)
    
    ## Test extra __add__ syntax
    #
    #model.observers += o1
    #model.addValue(1)
    #model.addValue(1)
    