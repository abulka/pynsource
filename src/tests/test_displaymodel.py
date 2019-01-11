import unittest
import tempfile
from parsing.api import old_parser, new_parser
from parsing.dump_pmodel import dump_old_structure
from view.display_model import DisplayModel

def parse_source(source_code, options):
    with tempfile.NamedTemporaryFile(mode="wt") as temp:  # TODO use streams not temporary files
        temp.write(source_code)
        temp.flush()
        pmodel, debuginfo = new_parser(temp.name, options)
    return pmodel, debuginfo

class TestCaseDisplayModel(unittest.TestCase):
    def test_simple(self):
        source_code = """
class Fred(Mary, Sam):
    pass
        """
        pmodel, debuginfo = parse_source(source_code, options={})
        print(pmodel.classlist)
        print((dump_old_structure(pmodel)))

        self.assertEqual(list(pmodel.classlist.keys()), ["Fred"])
        self.assertEqual(pmodel.classlist["Fred"].defs, [])
        self.assertEqual(pmodel.classlist["Fred"].classesinheritsfrom, ["Mary", "Sam"])

        # Now convert to a display model

        dmodel = DisplayModel()
        dmodel.ConvertParseModelToUmlModel(pmodel)
        dmodel.Dump()
        print("display model", dmodel)

"""
Differences to alsm

OLD PARSE MODEL             GITUML 
USED BY PYNSOURCE           ALSM                        TYPE
-----------------           -----------                 -----------------------

pmodel.classlist            alsm.classes                : Dict[str, ClassEntry]

ClassEntry
    .name                   .name    
    .defs                   .methods                    : List[?]
    .attrs                  .attributes                 : List[?]
    .classesinheritsfrom    .classes_inherits_from      : List[str]
    .classdependencytuples  .class_dependency_tuples    : List[str]
    
    .ismodulenotrealclass   no equivalent cos an alsm 
                            represents a module
    
"""

#     def test_incoming_bugs(self):
#         source_code = """
# class Incoming1:
#     def HandlePowerOperator(self):
#         x = 10**2
#         print(x)
#
# a = Incoming1()
# a.HandlePowerOperator()
#         """
#         alsm = self.parse_to_alsm(source_code)
#         # TODO(alsm): Fix module attributes - 'a'
#         self.assertIsNone(alsm.error)
#         self.assertEqual(alsm.functions, [])
#         self.assertEqual(list(alsm.classes.keys()), ["Incoming1"])
#         self.assertEqual(alsm.classes["Incoming1"].methods, ["HandlePowerOperator"])
#         class_attributes = [
#             (x.attr_name, x.attr_type) for x in alsm.classes["Incoming1"].attributes
#         ]
#         self.assertEqual(class_attributes, [])
#         self.assertEqual(alsm.classes["Incoming1"].classes_inherits_from, [])
#
#
# import unittest
# from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE
#
#
# class TestCase08(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def test01(self):
#         """
#         """
#         FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule08_multiple_inheritance.py"
#
#         # self.p, debuginfo = old_parser(FILE)
#         self.p, debuginfo = new_parser(FILE)
#
#         # print self.p
#
#         # -------------------------------------------------------
#
#         gotevent1 = 0
#         gotevent2 = 0
#         gotevent3 = 0
#         gotevent4 = 0
#         gotevent5 = 0
#         gotevent6 = 0
#         gotevent7 = 0
#
#         for classname, classentry in list(self.p.classlist.items()):
#             if classname == "Fred":
#                 gotevent1 = 1
#                 assert classentry.classesinheritsfrom == [
#                     "Mary",
#                     "Sam",
#                 ], classentry.classesinheritsfrom
#
#             if classname == "MarySam":
#                 gotevent3 = False  # should not get this
#
#         assert gotevent1
#         assert not gotevent3
#
#     def test_parse_power_operator(self):
#         """
#         """
#         FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule11_incoming_bugs.py"
#
#         # self.p, debuginfo = old_parser(FILE)
#         self.p, debuginfo = new_parser(FILE)
#
#         # print self.p
#
#         # -------------------------------------------------------
#
#         gotevent1 = 0
#         gotevent2 = 0
#
#         for classname, classentry in list(self.p.classlist.items()):
#             if classname == "Incoming1":
#                 gotevent1 = 1
#
#         assert gotevent1
