# Unit tests for pyNsource that
# check that module functions are not treated as classes

import unittest
import os

import sys
if not '..'in sys.path: sys.path.insert(0, '..')  # get to local version of pynsource and avoid any version of pynsource in the site-packages folder.
from pynsource.pynsource import PySourceAsText

class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def check01(self):
        """
        """
        FILE = 'python-in/testmodule66.py'
        self.p.Parse(FILE)

        #print self.p

        # -------------------------------------------------------

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0
        gotevent4 = 0
        gotevent5 = 0
        gotevent6 = 0
        gotevent7 = 0

        for classname, classentry in self.p.classlist.items():
            if classname == 'Flag':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 3, len(classentry.attrs)
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == 'flagx':
                        gotevent5 = 1
                    if attrname == 'flagy':
                        gotevent6 = 1
                    if attrname == 'owner':
                        gotevent7 = 1

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 3
                assert '__init__' in classentry.defs
                assert 'readflag' in classentry.defs
                assert '__repr__' in classentry.defs


            if classname == 'Flags':
                gotevent2 = 2
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 2
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == 'flags':
                        gotevent3 = 1
                        compositescreatedforattr = self.p.GetCompositeClassesForAttr(attrobj.attrname, classentry)
                        # 'flags is pointing at composite of flag'
                        assert len(compositescreatedforattr) == 1
                        assert compositescreatedforattr[0] == 'Flag'

                    if attrname == 'numberOfFlags':
                        gotevent4 = 1
                        assert not 'static' in attrobj.attrtype

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 4
                assert '__init__' in classentry.defs
                assert 'readFlags' in classentry.defs
                assert 'AddFlag' in classentry.defs
                assert '__repr__' in classentry.defs

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



