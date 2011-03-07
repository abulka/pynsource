# Unit tests for pyNsource that 
# check for nested classes

import unittest
import os

import sys
if not '..'in sys.path: sys.path.append('..')
from pynsource.pynsource import PySourceAsText

class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def checkNestedClasses01(self):
        """
        class ParseMeTest:
            a = 100
            class A:
                pass
            def __init__(self):
                self.b = []
                class B:
                    ba = 99
                    class C:
                        def __init__(self):
                            self.cc = 88
            def Hi(self):
                pass

        class D:
            pass
        """        
        FILE = 'python-in/testmodule05.py'
        self.p.Parse(FILE)

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0
        gotevent4 = 0
        gotevent5 = 0
        gotevent6 = 0
        gotevent7 = 0
        for classname, classentry in self.p.classlist.items():
            if classname == 'ParseMeTest':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 2
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == 'a':
                        gotevent2 = 1
                    if attrname == 'b':
                        gotevent3 = 1

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 2
                assert '__init__' in classentry.defs
                assert 'Hi' in classentry.defs

            if classname == 'ParseMeTest_A':
                gotevent4 = 1
                assert len(classentry.attrs) == 0
                assert len(classentry.defs) == 0

            if classname == 'ParseMeTest_B':
                gotevent5 = 1
                assert len(classentry.attrs) == 1
                assert len(classentry.defs) == 0

            if classname == 'ParseMeTest_B_C':
                gotevent6 = 1
                assert len(classentry.attrs) == 1
                assert len(classentry.defs) == 1

                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    assert attrname == 'cc'
                

            if classname == 'D':
                gotevent7 = 1
                assert len(classentry.attrs) == 0
                assert len(classentry.defs) == 0


        assert gotevent1
        assert gotevent2 
        assert gotevent3 
        assert gotevent4 
        assert gotevent5 
        assert gotevent6
        assert gotevent7
        

       
def suite():
    suite1 = unittest.makeSuite(TestCase01, 'check')
    alltests = unittest.TestSuite((suite1, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()



