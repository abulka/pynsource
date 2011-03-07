# Unit tests for pyNsource that
# check that one to many works in the case of a test submitted by Antonio

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
        FILE = 'python-in/testmodule67clippy.py'
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
            if classname == 'Polygon':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 1, len(classentry.attrs)
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    
                    if attrname == 'verts':
                        gotevent2 = 1
                        compositescreatedforattr = self.p.GetCompositeClassesForAttr(attrobj.attrname, classentry)
                        # 'flags is pointing at composite of Vert class'
                        assert len(compositescreatedforattr) == 1
                        assert compositescreatedforattr[0] == 'Vert'
                        
                        
                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 2
                assert '__init__' in classentry.defs
                assert 'appendVert' in classentry.defs

            if classname == 'V':
                gotevent3 = False  # should not get this

            if classname == 'Vert':
                gotevent4 = 2
                assert classentry.classesinheritsfrom == []


        assert gotevent1
        assert gotevent2
        assert not gotevent3
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



