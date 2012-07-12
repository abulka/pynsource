# Unit tests for pyNsource that
# check eval() statement and packages for java.

import unittest
import os

import sys
sys.path.append("../pynsource")
from generate_code.gen_asciiart import PySourceAsText

class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def testParsesCorrectly01(self):
        """
        class ParseMeTest:
            ...
            ...
            def SetFlagsFromMemento(self, memento):
                if memento:
                    self.flagsdict = eval(memento)
                else:
                    self.flagsdict = {}
        """
        FILE = 'python-in/testmodule06.py'
        self.p.Parse(FILE)

        #print self.p
        #return

        # -------------------------------------------------------

        for classname, classentry in self.p.classlist.items():
            if classname == 'ParseMeTest':
                gotevent1 = 1
                assert classentry.classesinheritsfrom == ['undo.UndoItem']

                assert len(classentry.attrs) == 7
                attrnames = [a.attrname for a in classentry.attrs]
                assert 'scenario' in attrnames
                assert 'flagsdict' in attrnames
                assert 'pointsdict' in attrnames
                assert 'weatherdict' in attrnames
                assert 'flageditor' in attrnames
                assert 'weathereditor' in attrnames
                assert 'turnseditor' in attrnames

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 2
                assert '__init__' in classentry.defs
                assert 'SetFlagsFromMemento' in classentry.defs



def suite():
    suite1 = unittest.makeSuite(TestCase01, 'test')
    alltests = unittest.TestSuite((suite1, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()



