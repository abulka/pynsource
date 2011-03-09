# Unit tests for pyNsource that
# check that module functions are not treated as classes

import unittest
import os

import sys
if not '..'in sys.path: sys.path.insert(0, '..')  # get to local version of pynsource and avoid any version of pynsource in the site-packages folder.
from pynsource.pynsource import PySourceAsYuml

class TestCaseYuml01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsYuml()

    def check01(self):
        FILE = 'python-in/testmodule01.py'
        self.p.Parse(FILE)
        
        OLDexpected = """
[ParseMeTest]b-.->[Blah]
[ParseMeTest]f++-*[Blah]
[ParseMeTest|a;b;d;e;e2;f|__init__();IsInBattle();DoA()]
[ParseMeTest]^[ParseMeTest2|_secretinfo|DoB()]
""".strip()
        expected = """
[ParseMeTest|a;b;d;e;e2;f|__init__();IsInBattle();DoA()]^[ParseMeTest2|_secretinfo|DoB()]
[ParseMeTest]b-.->[Blah]
[ParseMeTest]f++-*[Blah]
""".strip()
        self.assertEquals(expected, str(self.p).strip())

    def check02(self):
        FILE = 'python-in/testmodule66.py'
        self.p.Parse(FILE)

        OLDexpected = """
[Flag|flagx;flagy;owner|__init__();readflag();__repr__()]
[Flags]flags++-*[Flag]
[Flags|flags;numberOfFlags|__init__();readFlags();AddFlag();__repr__()]
        """.strip()
        expected = """
[Flags|flags;numberOfFlags|__init__();readFlags();AddFlag();__repr__()]flags++-*[Flag|flagx;flagy;owner|__init__();readflag();__repr__()]
        """.strip()
        self.assertEquals(expected, str(self.p).strip())

def suite():
    suite1 = unittest.makeSuite(TestCaseYuml01, 'check')
    alltests = unittest.TestSuite((suite1, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()

