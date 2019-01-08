# Unit tests for pyNsource that
# check that module functions are not treated as classes

import unittest
from generate_code.gen_yuml import PySourceAsYuml
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE


class TestCaseYuml01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsYuml()

    def _dump(self, p, expected):
        print()
        print("_" * 80 + " yUML CALCULATED:")
        print(str(p).strip())
        print("-" * 80 + " yUML EXPECTED:")
        print(expected)
        print("_" * 80 + " yUML END DUMP")

    def test01ParseMeTestUnoptimised(self):
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule01.py"
        self.p.Parse(FILE)
        self.p.CalcYumls(optimise=False)
        expected = """
[ParseMeTest]b-.->[Blah]
[ParseMeTest]f++-*[Blah]
[ParseMeTest|a;b;d;e;e2;f|__init__();IsInBattle();DoA()]
[ParseMeTest]^[ParseMeTest2|_secretinfo|DoB()]
""".strip()
        # self._dump(self.p, expected)
        self.assertEqual(expected, str(self.p).strip())

    def test02ParseMeTestOptimised(self):
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule01.py"
        self.p.Parse(FILE)
        self.p.CalcYumls(optimise=True)
        expected = """
[ParseMeTest|a;b;d;e;e2;f|__init__();IsInBattle();DoA()]b-.->[Blah]
[ParseMeTest]f++-*[Blah]
[ParseMeTest]^[ParseMeTest2|_secretinfo|DoB()]
""".strip()
        # self._dump(self.p, expected)
        self.assertEqual(expected, str(self.p).strip())

    def test01FlagUnoptimised(self):
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule66.py"
        self.p.Parse(FILE)
        self.p.CalcYumls(optimise=False)
        expected = """
[Flags]flags++-*[Flag]
[Flags|flags;numberOfFlags|__init__();readFlags();AddFlag();__repr__()]
[Flag|flagx;flagy;owner|__init__();readflag();__repr__()]
        """.strip()
        # self._dump(self.p, expected)
        self.assertEqual(expected, str(self.p).strip())

    def test02FlagOptimised(self):
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule66.py"
        self.p.Parse(FILE)
        self.p.CalcYumls(optimise=True)
        expected = """
[Flags|flags;numberOfFlags|__init__();readFlags();AddFlag();__repr__()]flags++-*[Flag|flagx;flagy;owner|__init__();readflag();__repr__()]
        """.strip()
        # self._dump(self.p, expected)
        self.assertEqual(expected, str(self.p).strip())
