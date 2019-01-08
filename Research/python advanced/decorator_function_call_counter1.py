# from http://wiki.python.org/moin/PythonDecoratorLibrary

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

   @staticmethod
   def count(f):
      "Return the number of times the function f was called."
      return countcalls.__instances[f].__numcalls

   @staticmethod
   def counts():
      "Return a dict of {function: # of calls} for all registered functions."
      return dict([(f, countcalls.count(f)) for f in countcalls.__instances])
      
# ANDY EXAMPLE

if __name__ == "__main__":

   @countcalls
   def andy1():
       print("andy1 called")
       
   andy1()
   andy1()
   andy1()
   
   # same
   print(countcalls.counts())
   print(andy1.counts())

   #print countcalls.count(andy1)  # this doesn't work - why?
   print(countcalls.counts())
   print("done")