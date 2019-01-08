# Unit tests for pyNsource that
# check eval() statement and packages for java.

import unittest
from generate_code.gen_asciiart import PySourceAsText
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE


class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def testNestedClasses01(self):
        """
        class ParseMeTest(undo.UndoItem):

            DEFAULT_ELEVATION = 30

            def __init__(self, map):
                self.map = map

            def PlaceTile(self, coord, terrainbmp):
                self.EnsureGraphicsSubDictAllocated(coord)
                newterraintype = self.bmpUtils.BmpToTerrainType(terrainbmp)


        """
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule07.py"
        self.p.Parse(FILE)

        # print self.p

        # -------------------------------------------------------

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0

        for classname, classentry in list(self.p.classlist.items()):
            if classname == "ParseMeTest":
                gotevent1 = 1
                assert classentry.classesinheritsfrom == ["undo.UndoItem"]

                assert len(classentry.attrs) == 2
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == "map":
                        gotevent2 = 1
                    if attrname == "DEFAULT_ELEVATION":
                        gotevent3 = 1
                        assert "static" in attrobj.attrtype

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 2
                assert "__init__" in classentry.defs
                assert "PlaceTile" in classentry.defs

        assert gotevent1
        assert gotevent2
        assert gotevent3
