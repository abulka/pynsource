# Basic unit tests for pyNsource
#

import unittest

import sys
if not '..'in sys.path: sys.path.append('..')
from pynsource.pynsource import PySourceAsText

class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def checkBasics01(self):
        """
        --------------------
        ParseMeTest  --------|> []
        --------------------
        a
        b  <@>----> ['Blah']
        d  static
        e  1..*         // interpreted as array of numbers
        e2  1..*        // interpreted as array of strings
        f  <@>----> ['Blah'] 1..*
        --------------------
        __init__
        IsInBattle
        DoA
        --------------------


        --------------------
        ParseMeTest2  --------|> ['ParseMeTest']
        --------------------
        _secretinfo
        --------------------
        DoB
        --------------------
        """
        FILE = 'python-in/testmodule01.py'
        self.p.Parse(FILE)

        #print self.p

        assert len(self.p.classlist) == 2

        gotevent1 = 0
        gotevent2 = 0
        gotevents = 0
        for classname, classentry in self.p.classlist.items():
            if classname == 'ParseMeTest':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 6
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    compositescreatedforattr = self.p.GetCompositeClassesForAttr(attrobj.attrname, classentry)

                    if attrname == 'a':
                        gotevents += 1
                        assert not compositescreatedforattr

                    if attrname == 'b':
                        gotevents += 1
                        assert len(compositescreatedforattr) == 1
                        assert compositescreatedforattr[0] == 'Blah'
                        
                    if attrname == 'c':
                        assert 0, 'Should not get attribute c cos it is setting a sub.sub.sub object'

                    if attrname == 'd':
                        gotevents += 1
                        assert 'static' in attrobj.attrtype
                        assert not compositescreatedforattr

                    if attrname == 'e':
                        gotevents += 1
                        assert 'many' in attrobj.attrtype
                        assert not compositescreatedforattr

                    if attrname == 'e2':
                        gotevents += 1
                        assert 'many' in attrobj.attrtype
                        assert not compositescreatedforattr

                    if attrname == 'f':
                        gotevents += 1
                        assert 'many' in attrobj.attrtype
                        assert len(compositescreatedforattr) == 1
                        assert compositescreatedforattr[0] == 'Blah'
                        
                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 3
                assert '__init__' in classentry.defs
                assert 'IsInBattle' in classentry.defs
                assert 'DoA' in classentry.defs
                
            if classname == 'ParseMeTest2':
                gotevent2 = 1
                assert classentry.classesinheritsfrom == ['ParseMeTest']

                assert len(classentry.attrs) == 1
                
                assert len(classentry.defs) == 1
                assert 'DoB' in classentry.defs
                
        assert gotevent1
        assert gotevent2 
        assert gotevents == 6

    def checkBasicsCommentGlitch01(self):
        FILE = 'python-in/testmodule02.py'
        self.p.Parse(FILE)

        #print self.p

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0
        gotevent4 = 0
        for classname, classentry in self.p.classlist.items():
            if classname == 'ParseMeTest':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 3
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == 'timejoinedbattle':
                        gotevent2 = 1
                    if attrname == 'fightingvalue':
                        gotevent3 = 1
                    if attrname == 'damagepointsincurred':
                        gotevent4 = 1
        assert gotevent1
        assert gotevent2 
        assert gotevent3 
        assert gotevent4 
        

def suite():
    suite1 = unittest.makeSuite(TestCase01, 'check')
    alltests = unittest.TestSuite((suite1, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()



