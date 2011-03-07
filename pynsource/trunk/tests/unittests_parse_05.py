# Unit tests for pyNsource that
# check eval() statement and packages for java.

import unittest
import os

import sys
if not '..'in sys.path: sys.path.insert(0, '..')  # get to local version of pynsource and avoid any version of pynsource in the site-packages folder.
from pynsource.pynsource import PySourceAsText

class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def checkNestedClasses01(self):
        """
        class ParseMeTest(undo.UndoItem):

            DEFAULT_ELEVATION = 30

            def __init__(self, map):
                self.map = map

            def PlaceTile(self, coord, terrainbmp):
                self.EnsureGraphicsSubDictAllocated(coord)
                newterraintype = self.bmpUtils.BmpToTerrainType(terrainbmp)


        """
        FILE = 'python-in/testmodule07.py'
        self.p.Parse(FILE)

        #print self.p

        # -------------------------------------------------------

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0

        for classname, classentry in self.p.classlist.items():
            if classname == 'ParseMeTest':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == ['undo.UndoItem']

                assert len(classentry.attrs) == 2
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == 'map':
                        gotevent2 = 1
                    if attrname == 'DEFAULT_ELEVATION':
                        gotevent3 = 1
                        assert 'static' in attrobj.attrtype

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 2
                assert '__init__' in classentry.defs
                assert 'PlaceTile' in classentry.defs



        assert gotevent1
        assert gotevent2
        assert gotevent3




def suite():
    suite1 = unittest.makeSuite(TestCase01, 'check')
    alltests = unittest.TestSuite((suite1, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()



