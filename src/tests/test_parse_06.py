# Unit tests for pyNsource that
# check that module functions are not treated as classes

import unittest
from generate_code.gen_asciiart import PySourceAsText
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE


class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def test01(self):
        """
        """
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule66.py"
        self.p.Parse(FILE)

        # print self.p

        # -------------------------------------------------------

        gotevent1 = 0
        gotevent2 = 0
        gotevent3 = 0
        gotevent4 = 0
        gotevent5 = 0
        gotevent6 = 0
        gotevent7 = 0

        for classname, classentry in list(self.p.classlist.items()):
            if classname == "Flag":
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 3, len(classentry.attrs)
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == "flagx":
                        gotevent5 = 1
                    if attrname == "flagy":
                        gotevent6 = 1
                    if attrname == "owner":
                        gotevent7 = 1

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 3
                assert "__init__" in classentry.defs
                assert "readflag" in classentry.defs
                assert "__repr__" in classentry.defs

            if classname == "Flags":
                gotevent2 = 2
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 2
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname
                    if attrname == "flags":
                        gotevent3 = 1
                        compositescreatedforattr = self.p.GetCompositeClassesForAttr(
                            attrobj.attrname, classentry
                        )
                        # 'flags is pointing at composite of flag'
                        assert len(compositescreatedforattr) == 1
                        assert compositescreatedforattr[0] == "Flag"

                    if attrname == "numberOfFlags":
                        gotevent4 = 1
                        assert not "static" in attrobj.attrtype

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 4
                assert "__init__" in classentry.defs
                assert "readFlags" in classentry.defs
                assert "AddFlag" in classentry.defs
                assert "__repr__" in classentry.defs

        assert gotevent1
        assert gotevent2
        assert gotevent3
        assert gotevent4
        assert gotevent5
        assert gotevent6
        assert gotevent7
