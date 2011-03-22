# Unit tests for pyNsource that
# check that module functions are not treated as classes

import unittest
import os

import sys
if not '..'in sys.path: sys.path.insert(0, '..')  # get to local version of pynsource and avoid any version of pynsource in the site-packages folder.
from pynsource.gen_yuml import PySourceAsYuml

class TestCaseYuml01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsYuml()

    def _dump(self, p, expected):
        print
        print "_"*80 + " yUML CALCULATED:"
        print str(p).strip()
        print "-"*80 + " yUML EXPECTED:"
        print expected
        print "_"*80 + " yUML END DUMP"


    def test01ParseMeTestUnoptimised(self):
        FILE = 'python-in/testmodule01.py'
        self.p.Parse(FILE)
        self.p.CalcYumls(optimise=False)
        expected = """
[ParseMeTest]b-.->[Blah]
[ParseMeTest]f++-*[Blah]
[ParseMeTest|a;b;d;e;e2;f|__init__();IsInBattle();DoA()]
[ParseMeTest]^[ParseMeTest2|_secretinfo|DoB()]
""".strip()
        #self._dump(self.p, expected)
        self.assertEquals(expected, str(self.p).strip())

    def test02ParseMeTestOptimised(self):
        FILE = 'python-in/testmodule01.py'
        self.p.Parse(FILE)
        self.p.CalcYumls(optimise=True)
        expected = """
[ParseMeTest|a;b;d;e;e2;f|__init__();IsInBattle();DoA()]b-.->[Blah]
[ParseMeTest]f++-*[Blah]
[ParseMeTest]^[ParseMeTest2|_secretinfo|DoB()]
""".strip()
        #self._dump(self.p, expected)
        self.assertEquals(expected, str(self.p).strip())

    def test01FlagUnoptimised(self):
        FILE = 'python-in/testmodule66.py'
        self.p.Parse(FILE)
        self.p.CalcYumls(optimise=False)
        expected = """
[Flag|flagx;flagy;owner|__init__();readflag();__repr__()]
[Flags]flags++-*[Flag]
[Flags|flags;numberOfFlags|__init__();readFlags();AddFlag();__repr__()]
        """.strip()
        #self._dump(self.p, expected)
        self.assertEquals(expected, str(self.p).strip())

    def test02FlagOptimised(self):
        FILE = 'python-in/testmodule66.py'
        self.p.Parse(FILE)
        self.p.CalcYumls(optimise=True)
        expected = """
[Flags|flags;numberOfFlags|__init__();readFlags();AddFlag();__repr__()]flags++-*[Flag|flagx;flagy;owner|__init__();readflag();__repr__()]
        """.strip()
        #self._dump(self.p, expected)
        self.assertEquals(expected, str(self.p).strip())

        
def suite():
    suite1 = unittest.makeSuite(TestCaseYuml01, 'test')
    alltests = unittest.TestSuite((suite1, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()

