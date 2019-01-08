# Unit tests for pyNsource that
# check that one to many works in the case of a test submitted by Antonio

import unittest
from generate_code.gen_asciiart import PySourceAsText
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE


class TestCase01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsText()

    def test01(self):
        """
        """
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule67clippy.py"
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
            if classname == "Polygon":
                gotevent1 = 1
                assert classentry.classesinheritsfrom == []

                assert len(classentry.attrs) == 1, len(classentry.attrs)
                for attrobj in classentry.attrs:
                    attrname = attrobj.attrname

                    if attrname == "verts":
                        gotevent2 = 1
                        compositescreatedforattr = self.p.GetCompositeClassesForAttr(
                            attrobj.attrname, classentry
                        )
                        # 'flags is pointing at composite of Vert class'
                        assert len(compositescreatedforattr) == 1
                        assert compositescreatedforattr[0] == "Vert"

                for adef in classentry.defs:
                    pass
                assert len(classentry.defs) == 2
                assert "__init__" in classentry.defs
                assert "appendVert" in classentry.defs

            if classname == "V":
                gotevent3 = False  # should not get this

            if classname == "Vert":
                gotevent4 = 2
                assert classentry.classesinheritsfrom == []

        assert gotevent1
        assert gotevent2
        assert not gotevent3
        assert gotevent4
