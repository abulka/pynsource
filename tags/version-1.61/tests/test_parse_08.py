# Unit tests for pyNsource that
# check that one to many works in the case of a test submitted by Antonio

import unittest
import os

import sys
sys.path.append("../src")
from parsing.api import old_parser, new_parser

class TestCase08(unittest.TestCase):
    def setUp(self):
        pass
                
    def test01(self):
        """
        """
        FILE = 'python-in/testmodule08_multiple_inheritance.py'

        #self.p, debuginfo = old_parser(FILE)
        self.p, debuginfo = new_parser(FILE)

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
            if classname == 'Fred':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == ['Mary', 'Sam'], classentry.classesinheritsfrom

            if classname == 'MarySam':
                gotevent3 = False  # should not get this


        assert gotevent1
        assert not gotevent3

    def test_parse_power_operator(self):
        """
        """
        FILE = 'python-in/testmodule11_incoming_bugs.py'

        #self.p, debuginfo = old_parser(FILE)
        self.p, debuginfo = new_parser(FILE)

        #print self.p

        # -------------------------------------------------------

        gotevent1 = 0
        gotevent2 = 0

        for classname, classentry in self.p.classlist.items():
            if classname == 'Incoming1':
                gotevent1 = 1


        assert gotevent1




def suite():
    suite1 = unittest.makeSuite(TestCase08, 'test')
    alltests = unittest.TestSuite((suite1, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()



