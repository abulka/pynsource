# Unit tests for pyNsource that 
# check that we can parse a class 
# and stop when the indent 
# deindents back to the margin.
# Also check we can scan module 
# level functions and global vars 
# and treat them like attrs of a class 
# named after the module.

import unittest
import os

import sys
if not '..'in sys.path: sys.path.append('..')
from pynsource.pynsource import PySourceAsText

class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def checkModuleVarsAndFunctions01(self):
        """
        class ParseMeTest:
            def __init__(self):
                self.a = None
                self.b = None
        x=20

        class ParseMeTest2:
            pass

        def y(): pass

        class ParseMeTest3:
            pass

        if __name__ == '__main__':
            y()

        class ParseMeTest4:
            pass

        """        
        CHECK_MODULE_LEVEL_PARSING = 1

        FILE = 'python-in/testmodule03.py'
        self.p.optionModuleAsClass = CHECK_MODULE_LEVEL_PARSING
        self.p.Parse(FILE)

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0
        gotevent4 = 0
        gotevent5 = 0
        gotevent6 = 0
        gotevent7 = 0
        gotevent8 = 0
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
                assert len(classentry.defs) == 1
                assert '__init__' in classentry.defs

            if classname == 'ParseMeTest2':
                gotevent4 = 1
                assert len(classentry.attrs) == 0
                assert len(classentry.defs) == 0

            if classname == 'ParseMeTest3':
                gotevent5 = 1
                assert len(classentry.attrs) == 0
                assert len(classentry.defs) == 0

            if classname == 'ParseMeTest4':
                gotevent6 = 1
                assert len(classentry.attrs) == 0
                assert len(classentry.defs) == 0


            # module level extra logic
            if CHECK_MODULE_LEVEL_PARSING:

                if classname == 'Module_'+os.path.splitext(os.path.basename(FILE))[0]:
                    gotevent7 = 1
                    assert classentry.classesinheritsfrom == []

                    for adef in classentry.defs:
                        pass
                    assert len(classentry.defs) == 1
                    assert 'y' in classentry.defs

                    assert len(classentry.attrs) == 1
                    for attrobj in classentry.attrs:
                        attrname = attrobj.attrname
                        if attrname == 'x':
                            gotevent8 = 1



        assert gotevent1
        assert gotevent2 
        assert gotevent3 
        assert gotevent4 
        assert gotevent5 
        assert gotevent6
        if CHECK_MODULE_LEVEL_PARSING:
            assert gotevent7 
            assert gotevent8 
        

    def checkModuleVarsAndFunctions02(self):
        """
        class ParseMeTest:
            a = 100
            b = [1,2,3]
            def __init__(self):
                self.c = []
                self.d = [1,2,3]
                self.e = (1,2,3)
                self.f = (1*10)
                
        x=[1,2]
        y=[]
        """        
        CHECK_MODULE_LEVEL_PARSING = 1

        FILE = 'python-in/testmodule04.py'
        self.p.optionModuleAsClass = CHECK_MODULE_LEVEL_PARSING
        self.p.Parse(FILE)

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0
        gotevent4 = 0
        gotevent5 = 0
        gotevent6 = 0
        gotevent7 = 0
        gotevent8 = 0
        gotevent9 = 0
        for classname, classentry in self.p.classlist.items():
            if classname == 'ParseMeTest':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []
                assert classentry.ismodulenotrealclass == 0

                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    #print attrname
                    if attrname == 'a':
                        gotevent2 = 1
                        assert 'static' in attrobj.attrtype
                    if attrname == 'b':
                        gotevent3 = 1
                        assert 'static' in attrobj.attrtype
                    if attrname == 'c':
                        gotevent4 = 1
                        assert 'static' not in attrobj.attrtype
                    if attrname == 'd':
                        gotevent3 = 1
                        assert 'static' not in attrobj.attrtype
                    if attrname == 'e':
                        gotevent5 = 1
                        assert 'static' not in attrobj.attrtype
                    if attrname == 'f':
                        gotevent6 = 1
                        assert 'static' not in attrobj.attrtype
                assert len(classentry.attrs) == 6, 'Only got ' + `len(classentry.attrs)` + ' attributes'

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 1
                assert '__init__' in classentry.defs

            # module level extra logic
            if CHECK_MODULE_LEVEL_PARSING:
                if classname == 'Module_'+os.path.splitext(os.path.basename(FILE))[0]:
                    gotevent7 = 1
                    assert classentry.classesinheritsfrom == []
                    assert classentry.ismodulenotrealclass

                    for adef in classentry.defs:
                        pass
                    assert len(classentry.defs) == 0

                    for attrobj in classentry.attrs:
                        attrname = attrobj.attrname
                        #print 'attr', attrname
                        if attrname == 'x':
                            gotevent8 = 1
                        if attrname == 'y':
                            gotevent9 = 1
                    assert len(classentry.attrs) == 2, 'Only got ' + `len(classentry.attrs)` + ' attributes'



        assert gotevent1
        assert gotevent2 
        assert gotevent3 
        assert gotevent4 
        assert gotevent5 
        assert gotevent6
        if CHECK_MODULE_LEVEL_PARSING:
            assert gotevent7 
            assert gotevent8 
            assert gotevent9
        
        
def suite():
    suite1 = unittest.makeSuite(TestCase01, 'check')
    alltests = unittest.TestSuite((suite1, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()



