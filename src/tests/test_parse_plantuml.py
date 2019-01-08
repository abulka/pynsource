# Unit tests for pyNsource that
# check that module functions are not treated as classes

import unittest
from generate_code.gen_plantuml import PySourceAsPlantUml
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE

# python -m unittest tests.test_parse_plantuml

class TestCasePlantUml01(unittest.TestCase):
    def setUp(self):
        self.p = PySourceAsPlantUml()

    def _dump(self, p, expected):
        print()
        print("_"*80 + " PlantUml CALCULATED:")
        print(str(p).strip())
        print("-"*80 + " PlantUml EXPECTED:")
        print(expected)
        print("_"*80 + " PlantUml END DUMP")


    def test01(self):
        """
        class Fred(Mary, Sam):
            pass
        """
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + 'testmodule08_multiple_inheritance.py'
        self.p.Parse(FILE)
        self.p.calc_plant_uml(optimise=False)
        expected = """

class Fred {
}

Mary <|- Fred
Sam <|- Fred
""".strip()
        # self._dump(self.p, expected)
        self.assertEqual(expected, str(self.p).strip())

    def test01ParseMeTestUnoptimised(self):
        """
        class ParseMeTest:
            def __init__(self):
                self.a = 10            # class attribute
                self.b = Blah()        # class attribute COMPOSITE
                self.a.c = 20          # skip
                self.__class__.d = 30  # static class attribute
                self.e.append(10)      # class attribute (list/vector)
                self.e2.append("10")   # class attribute (list/vector)
                self.f.append(Blah())  # class attribute (list/vector) COMPOSITE

            def IsInBattle(self):
                if not self.tileinfo:
                    return 0
                return self.tileinfo.battletriggered

            def DoA(self):
                pass
        class ParseMeTest2(ParseMeTest):
            def DoB(self):
                self._secretinfo = 2
        """
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + 'testmodule01.py'
        self.p.Parse(FILE)
        self.p.calc_plant_uml(optimise=False)
        expected = """

class ParseMeTest {
    a
    b
    d
    e
    e2
    f
    __init__()
    IsInBattle()
    DoA()
}

ParseMeTest ..> Blah : b
ParseMeTest *--> "*" Blah : f

class ParseMeTest2 {
    _secretinfo
    DoB()
}

ParseMeTest <|- ParseMeTest2
""".strip()
        # self._dump(self.p, expected)
        self.assertEqual(expected, str(self.p).strip())