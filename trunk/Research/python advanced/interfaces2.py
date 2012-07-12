# Interfaces
# Fantastic article http://www.doughellmann.com/PyMOTW/abc/
#

import abc

class IPersist(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def load(self, input):
        return
    @abc.abstractmethod
    def save(self, output, data):
        return

class ISing(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def sing(self):
        return

#####

class MyClass(IPersist, ISing):
    
    def load(self, input):
        return input.read()
    
    def save(self, output, data):
        return output.write(data)

    def sing(self):
        return

o = MyClass()
print o

print "done"