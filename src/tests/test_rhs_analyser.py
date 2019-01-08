# RhsAnalyser tests

import sys

sys.path.append("../src")
from common.architecture_support import whosdaddy, whosgranddaddy
from parsing.keywords import pythonbuiltinfunctions
from parsing.parse_rhs_analyser import RhsAnalyser

"""

 TEST - BASE CLASS
 
"""

import unittest
import sys


class MockQuickParse:
    def __init__(self):
        self.quick_found_classes = []
        self.quick_found_module_defs = []
        self.quick_found_module_attrs = []


class MockOldParseModel:
    def __init__(self):
        self.classlist = {}
        self.modulemethods = []


class MockVisitor:
    def __init__(self, quick_parse):
        self.model = MockOldParseModel()
        self.stack_classes = []
        self.stack_module_functions = [False]
        self.quick_parse = quick_parse
        self.init_lhs_rhs()
        self.imports_encountered = []

    def init_lhs_rhs(self):
        self.lhs = []
        self.rhs = []
        self.lhs_recording = True
        self.made_rhs_call = False
        self.made_assignment = False
        self.made_append_call = False
        self.made_import = False
        self.pos_rhs_call_pre_first_bracket = None


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.qp = MockQuickParse()
        self.v = MockVisitor(self.qp)
        self.v.imports_encountered = ["a"]
        self.v.model.modulemethods = []

        self.modes = ["assign", "append"]

    def get_visitor(self, rhs, assign_or_append):
        self.v.rhs = rhs
        if assign_or_append == "assign":
            self.v.made_append_call = False
            self.v.made_assignment = True
        else:
            self.v.made_append_call = True
            self.v.made_assignment = False
        return self.v

    def do(
        self,
        rhs,
        made_rhs_call,
        call_pos,
        quick_classes,
        quick_defs,
        result_should_be,
        rhs_ref_to_class_should_be,
        imports,
    ):
        for mode in self.modes:
            v = self.get_visitor(rhs, mode)
            v.made_rhs_call = made_rhs_call
            v.quick_parse.quick_found_classes = quick_classes
            v.quick_parse.quick_found_module_defs = quick_defs
            v.pos_rhs_call_pre_first_bracket = call_pos
            v.imports_encountered = imports

            ra = RhsAnalyser(v)
            self.assertEqual(ra.is_rhs_reference_to_a_class(), result_should_be)
            self.assertEqual(ra.rhs_ref_to_class, rhs_ref_to_class_should_be)


"""

 TESTS
 
"""


class TestCase_A_Classic(TestCaseBase):
    # self.w = Blah()
    # self.w.append(Blah())

    """
    if Blah class exists and its NOT in module methods
    Blah() where: class Blah - T Blah
    """

    def test_1(self):
        self.do(
            rhs=["Blah"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=[],
            result_should_be=True,
            rhs_ref_to_class_should_be="Blah",
        )

    """
    if Blah class does NOT exist and it IS in module methods
    Blah() where: def Blah() - F
    """

    def test_2(self):
        self.do(
            rhs=["Blah"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=[],
            quick_defs=["Blah"],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    """
    if Blah class exists and it IS in module methods - CONTRADICATION, assume Blah is class
    Blah() where: class Blah, def Blah() - T Blah
    """

    def test_3(self):
        self.do(
            rhs=["Blah"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=["Blah"],
            imports=[],
            result_should_be=True,
            rhs_ref_to_class_should_be="Blah",
        )

    """
    if Blah class does NOT exist and its NOT in module methods - GUESS yes, if starts with uppercase letter
    Blah() where: - T Blah
    blah() where: - F
    """

    def test_4(self):
        self.do(
            rhs=["Blah"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=[],
            quick_defs=[],
            imports=[],
            result_should_be=True,
            rhs_ref_to_class_should_be="Blah",
        )

    def test_5(self):
        self.do(
            rhs=["blah"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=[],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )


class TestCase_B_RhsIsInstance(TestCaseBase):
    # self.w = blah
    # self.w.append(blah)

    def test_1(self):
        """
        if Blah class exists and blah is NOT in module methods ==> (token transmografied)
        blah where: class Blah - T Blah
        """
        self.do(
            rhs=["blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=[],
            result_should_be=True,
            rhs_ref_to_class_should_be="Blah",
        )

    def test_2(self):
        """
        if Blah class exists and blah IS in module methods (clear intent that blah is a function ref)
        blah where: class Blah, def blah() - F
        """
        self.do(
            rhs=["blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=["blah"],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_3(self):
        """
        if Blah class exists and blah is NOT in module methods but Blah IS in module methods
            (if Blah is a function this is unrelated to blah instance)  ==> (token transmografied)
        blah where: class Blah, def Blah() - T Blah
        """
        self.do(
            rhs=["blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=["Blah"],
            imports=[],
            result_should_be=True,
            rhs_ref_to_class_should_be="Blah",
        )

    def test_4(self):
        """
        if Blah class doesn't exist
        blah where: - F
        """
        self.do(
            rhs=["blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=[],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

        # the state of module methods doesn't matter:
        # blah where: def Blah() - F
        # blah where: def blah() - F

        self.do(
            rhs=["blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=[],
            quick_defs=["Blah"],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

        self.do(
            rhs=["blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=[],
            quick_defs=["blah"],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_5(self):
        """
        if blah class exists - syntax is just plain wrong for class creation.
        blah where: class blah - F
        """
        self.do(
            rhs=["blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["blah"],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

        # the state of module methods doesn't matter:
        # blah where: class blah, def Blah() - F

        self.do(
            rhs=["blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["blah"],
            quick_defs=["Blah"],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )


class TestCase_C_AttrBeforeClassic(TestCaseBase):
    # self.w = a.Blah()
    # self.w.append(a.Blah())

    def test_1(self):
        """
        a.Blah() where: class Blah, import a - T a.Blah
        """
        self.do(
            rhs=["a", "Blah"],
            made_rhs_call=True,
            call_pos=1,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=["a"],
            result_should_be=True,
            rhs_ref_to_class_should_be="a.Blah",
        )

    def test_2(self):
        """
        Most common case, e.g. self.popupmenu = wx.Menu() where all you know about is that you imported wx.
        a.Blah() where: import a - T a.Blah
        """
        self.do(
            rhs=["a", "Blah"],
            made_rhs_call=True,
            call_pos=1,
            quick_classes=[],
            quick_defs=[],
            imports=["a"],
            result_should_be=True,
            rhs_ref_to_class_should_be="a.Blah",
        )

    def test_3(self):
        """
        a.Blah() where: class Blah - F
        """
        self.do(
            rhs=["a", "Blah"],
            made_rhs_call=True,
            call_pos=1,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_4(self):
        """
        a.Blah() where: - F
        """
        self.do(
            rhs=["a", "Blah"],
            made_rhs_call=True,
            call_pos=1,
            quick_classes=[],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )


class TestCase_D_MultipleAttrBeforeClassic(TestCaseBase):
    # self.w = a.b.Blah()
    # self.w.append(a.b.Blah())

    def test_1(self):
        """
        a.b.Blah() where: class Blah, import a.b - T a.b.Blah
        """
        self.do(
            rhs=["a", "b", "Blah"],
            made_rhs_call=True,
            call_pos=2,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=["a.b"],
            result_should_be=True,
            rhs_ref_to_class_should_be="a.b.Blah",
        )

    def test_2(self):
        """
        a.b.Blah() where: import a.b - T a.b.Blah()
        """
        self.do(
            rhs=["a", "b", "Blah"],
            made_rhs_call=True,
            call_pos=2,
            quick_classes=[],
            quick_defs=[],
            imports=["a.b"],
            result_should_be=True,
            rhs_ref_to_class_should_be="a.b.Blah",
        )

    def test_3(self):
        """
        a.b.Blah() where: class Blah, import b - F
        """
        self.do(
            rhs=["a", "b", "Blah"],
            made_rhs_call=True,
            call_pos=2,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=["b"],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_4(self):
        """
        a.b.Blah() where: class Blah, import a - F
        """
        self.do(
            rhs=["a", "b", "Blah"],
            made_rhs_call=True,
            call_pos=2,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=["a"],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )


class TestCase_E_DoubleCall(TestCaseBase):
    # self.w = a().Blah()
    # self.w.append(a().Blah())

    def test_1(self):
        """
        a().Blah() where: class Blah - F
        """
        self.do(
            rhs=["a", "Blah"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_2(self):
        """
        a().Blah() where: class a - F
        """
        self.do(
            rhs=["a", "Blah"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=["a"],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )


class TestCase_F_CallThenTrailingInstance(TestCaseBase):
    # self.w = a().blah
    # self.w.append(a().blah)

    def test_1(self):
        """
        a().blah where: class Blah - F
        """
        self.do(
            rhs=["a", "blah"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )


class TestCase_G_AttrBeforeRhsInstance(TestCaseBase):
    # self.w = a.blah
    # self.w.append(a.blah)

    def test_1(self):
        """
        a.blah where: - F
        """
        self.do(
            rhs=["a", "blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=[],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_2(self):
        """
        a.blah where: class a - F
        """
        self.do(
            rhs=["a", "blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["a"],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_3(self):
        """
        a.blah where: class blah - F
        """
        self.do(
            rhs=["a", "blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["blah"],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_4(self):
        """
        a.blah where: class Blah - F
        """
        self.do(
            rhs=["a", "blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=[],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )

    def test_5(self):
        """
        a.blah where: class Blah, imports a - F
        """
        self.do(
            rhs=["a", "blah"],
            made_rhs_call=False,
            call_pos=0,
            quick_classes=["Blah"],
            quick_defs=[],
            imports=["a"],
            result_should_be=False,
            rhs_ref_to_class_should_be=None,
        )


class TestCase_AddHoc(TestCaseBase):
    def test_1(self):
        """
        self.flageditor = FlagEditor(gamestatusstate=self)
        a.blah where: class Blah, imports a - F
        """
        self.do(
            rhs=["FlagEditor"],
            made_rhs_call=True,
            call_pos=0,
            quick_classes=[],
            quick_defs=[],
            imports=[],
            result_should_be=True,
            rhs_ref_to_class_should_be="FlagEditor",
        )


def suite():
    suite1 = unittest.makeSuite(TestCase_A_Classic, "test")
    suite2 = unittest.makeSuite(TestCase_B_RhsIsInstance, "test")
    suite3 = unittest.makeSuite(TestCase_C_AttrBeforeClassic, "test")
    suite4 = unittest.makeSuite(TestCase_D_MultipleAttrBeforeClassic, "test")
    suite5 = unittest.makeSuite(TestCase_E_DoubleCall, "test")
    suite6 = unittest.makeSuite(TestCase_F_CallThenTrailingInstance, "test")
    suite7 = unittest.makeSuite(TestCase_G_AttrBeforeRhsInstance, "test")
    suite8 = unittest.makeSuite(TestCase_AddHoc, "test")
    alltests = unittest.TestSuite((suite1, suite2, suite3, suite4, suite5, suite6, suite7))
    # alltests = unittest.TestSuite((suite8, ))
    # alltests = unittest.TestSuite((suite3, suite4))
    return alltests


def main():
    runner = unittest.TextTestRunner(
        descriptions=0, verbosity=2
    )  # default is descriptions=1, verbosity=1
    runner.run(suite())


if __name__ == "__main__":
    main()
