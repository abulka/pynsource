# Interfaces
# Fantastic article http://www.doughellmann.com/PyMOTW/abc/
#

import abc

class PluginBase(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def load(self, input):
        """Retrieve data from the input source and return an object."""
        return
    
    @abc.abstractmethod
    def save(self, output, data):
        """Save the data object to the output."""
        return

class SubclassImplementation(PluginBase):
    
    def load(self, input):
        return input.read()
    
    def save(self, output, data):
        return output.write(data)

#o = PluginBase()  # Can't instantiate base class
o = SubclassImplementation()
print o

class IncompleteImplementation(PluginBase):
    
    def save(self, output, data):
        return output.write(data)
        
#o = IncompleteImplementation() # Can't instantiate Incomplete Implementation
#print o
        
print "done"