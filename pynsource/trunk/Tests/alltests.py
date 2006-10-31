#!/usr/bin/env python
#
# Example of assembling all available unit tests into one suite. This usually
# varies greatly from one project to the next, so the code shown below will not
# be incorporated into the 'unittest' module. Instead, modify it for your own
# purposes.
# 
# $Id:  $
"""
  ANDY NOTES:  Example of assembling all available unit tests into one suite.   
               You should put a copy of this alltests.py into the folder you
               are testing.
               
   1. You simply have to list the modules (.py files) in the folder to test.
   
   2. My version assumes all modules have a suite() function.  I
      don't know why the original idea of unittest.findTestCases(module) doesn't work.
      
   3. If you want verbosity (test docstring displayed as they are run)
      like we used to in python 2.0 then I had to change
      
          #unittest.main(defaultTest='suite')
          unittest.main(defaultTest='suite',argv=('andyDummySomeapp', '-v') )
          
      NOTE if you are running from within a unit, then a similar change is
      
          #runner = unittest.TextTestRunner()
          runner = unittest.TextTestRunner(descriptions=0, verbosity=2) # default is descriptions=1, verbosity=1

   --------------
   
   PS. Another version of 'alltests' module called 'TestRunner.py' is in a comment at the end of the module.
      I did't try hard to get this working, but it seems to try to achieve the
      same thing

"""

import unittest

def suite():
    modules_to_test = (
            'unittests_parse_01',
            'unittests_parse_02',
            'unittests_parse_03',
            'unittests_parse_04',
            'unittests_parse_05',
            'unittests_parse_06',
            'unittests_parse_07'
            )   # ANDY - and so on
    alltests = unittest.TestSuite()
    for module in map(__import__, modules_to_test):
        #alltests.addTest(unittest.findTestCases(module))  # ANDY - this doesn't seem to work
        alltests.addTest( module.suite() )  # ANDY CHANGED since all my modules have .suite() module function.
    return alltests

if __name__ == '__main__':
    #unittest.main(defaultTest='suite')
    unittest.main(defaultTest='suite',argv=('andyDummySomeapp', '-v') )  # ANDY - made this verbose.  had to put dummy text into tuple that simulates this being run from shell comman line.


"""Regression testing framework
This module will search for scripts in the same directory named
XYZTest.py.  Each such script should be a test suite that tests a
module through PyUnit.  (As of Python 2.1, PyUnit is included in
the standard library as "unittest".)  This script will aggregate all
found test suites into one big test suite and run them all at once.

TestRunner.py - An automated unit test system 

Mark Pilgrim gives a short but very useful program to run all
your tests automatically. If your testfiles all end in "test.py",
this program will import all the classes in these files, make
a ?TestSuite out of the ?TestCases or ?TestSuites they contain,
and start unittest with that ?TestSuite. I call this
program '?TestRunner.py': 



import unittest

import sys, os, re, unittest

def regressionTest():
    path = os.path.split(sys.argv[0])[0] or os.getcwd()
    files = os.listdir(path)
    test = re.compile("*test.py$", re.IGNORECASE)
    files = filter(test.search, files)
    filenameToModuleName = lambda f: os.path.splitext(f)[0]
    moduleNames = map(filenameToModuleName, files)
    modules = map(__import__, moduleNames)
    load = unittest.defaultTestLoader.loadTestsFromModule
    return unittest.TestSuite(map(load, modules))

if __name__ == "__main__":
    unittest.main(defaultTest="regressionTest")
"""
