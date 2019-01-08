# Unit tests for pyNsource that
# check for nested classes

import unittest
import os

import sys
from generate_code.gen_asciiart import PySourceAsText
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE


class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def testNestedClasses01(self):
        """
        class ParseMeTest:
            a = 100
            class A:
                pass
            def __init__(self):
                self.b = []
                class B:
                    ba = 99
                    class C:
                        def __init__(self):
                            self.cc = 88
            def Hi(self):
                pass

        class D:
            pass
        """
        """
        result should be
            ParseMeTest:
            ParseMeTest_A:
            ParseMeTest_B:
            ParseMeTest_B_C:
            D:
        """

        self.p = PySourceAsText(ast=False)  # override the setUp() so we force using the old parser

        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule05.py"
        self.p.Parse(FILE)

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0
        gotevent4 = 0
        gotevent5 = 0
        gotevent6 = 0
        gotevent7 = 0
        for classname, classentry in list(self.p.classlist.items()):
            if classname == "ParseMeTest":
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 2
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == "a":
                        gotevent2 = 1
                    if attrname == "b":
                        gotevent3 = 1

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 2
                assert "__init__" in classentry.defs
                assert "Hi" in classentry.defs

            if classname == "ParseMeTest_A":
                gotevent4 = 1
                assert len(classentry.attrs) == 0
                assert len(classentry.defs) == 0

            if classname == "ParseMeTest_B":
                gotevent5 = 1
                assert len(classentry.attrs) == 1
                assert len(classentry.defs) == 0

            if classname == "ParseMeTest_B_C":
                gotevent6 = 1
                assert len(classentry.attrs) == 1
                assert len(classentry.defs) == 1

                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    assert attrname == "cc"

            if classname == "D":
                gotevent7 = 1
                assert len(classentry.attrs) == 0
                assert len(classentry.defs) == 0

        assert gotevent1
        assert gotevent2
        assert gotevent3
        assert gotevent4
        assert gotevent5
        assert gotevent6
        assert gotevent7
