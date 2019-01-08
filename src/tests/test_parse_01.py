# Basic unit tests for pyNsource
#
# Run with
# python -m unittest tests.test_parse_01
# python -m unittest -v tests.test_parse_01
#
# from the src directory

import unittest
from generate_code.gen_asciiart import PySourceAsText
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE


class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def testBasics01(self):
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
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule01.py"
        self.p.Parse(FILE)

        # print self.p

        assert len(self.p.classlist) == 2

        gotevent1 = 0
        gotevent2 = 0
        gotevents = 0
        for classname, classentry in list(self.p.classlist.items()):
            if classname == "ParseMeTest":
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 6
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    compositescreatedforattr = self.p.GetCompositeClassesForAttr(
                        attrobj.attrname, classentry
                    )

                    if attrname == "a":
                        gotevents += 1
                        assert not compositescreatedforattr

                    if attrname == "b":
                        gotevents += 1
                        assert len(compositescreatedforattr) == 1
                        assert compositescreatedforattr[0] == "Blah"

                    if attrname == "c":
                        assert (
                            0
                        ), "Should not get attribute c cos it is setting a sub.sub.sub object"

                    if attrname == "d":
                        gotevents += 1
                        assert "static" in attrobj.attrtype
                        assert not compositescreatedforattr

                    if attrname == "e":
                        gotevents += 1
                        assert "many" in attrobj.attrtype
                        assert not compositescreatedforattr

                    if attrname == "e2":
                        gotevents += 1
                        assert "many" in attrobj.attrtype
                        assert not compositescreatedforattr

                    if attrname == "f":
                        gotevents += 1
                        assert "many" in attrobj.attrtype
                        assert len(compositescreatedforattr) == 1
                        assert compositescreatedforattr[0] == "Blah"

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 3
                assert "__init__" in classentry.defs
                assert "IsInBattle" in classentry.defs
                assert "DoA" in classentry.defs

            if classname == "ParseMeTest2":
                gotevent2 = 1
                assert classentry.classesinheritsfrom == ["ParseMeTest"]

                assert len(classentry.attrs) == 1

                assert len(classentry.defs) == 1
                assert "DoB" in classentry.defs

        assert gotevent1
        assert gotevent2
        assert gotevents == 6

    def testBasicsCommentGlitch01(self):
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule02.py"
        self.p.Parse(FILE)

        # print self.p

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0
        gotevent4 = 0
        for classname, classentry in list(self.p.classlist.items()):
            if classname == "ParseMeTest":
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 3
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == "timejoinedbattle":
                        gotevent2 = 1
                    if attrname == "fightingvalue":
                        gotevent3 = 1
                    if attrname == "damagepointsincurred":
                        gotevent4 = 1
        assert gotevent1
        assert gotevent2
        assert gotevent3
        assert gotevent4
