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
    def test_no_duplicate_edges(self):
        """
        1. Ensure no duplicate edges when add to displaymodel from same parsemodel twice
        """
        source_code = """
class Fred(Mary, Sam):
    pass
        """
        pmodel, debuginfo = parse_source(source_code, options={})
        # print(pmodel.classlist)
        # print((dump_old_structure(pmodel)))

        self.assertEqual(list(pmodel.classlist.keys()), ["Fred"])
        self.assertEqual(pmodel.classlist["Fred"].defs, [])
        self.assertEqual(pmodel.classlist["Fred"].classesinheritsfrom, ["Mary", "Sam"])

        # Now convert to a display model

        dmodel = DisplayModel()
        dmodel.build_displaymodel(pmodel)
        # dmodel.Dump()
        self.assertEqual(len(dmodel.graph.nodes), 3)
        self.assertEqual(len(dmodel.graph.edges), 2)
        # print("display model", dmodel)

        # again - should not cause extra edges to be created
        dmodel.build_displaymodel(pmodel)
        # dmodel.Dump()
        self.assertEqual(len(dmodel.graph.nodes), 3)
        self.assertEqual(len(dmodel.graph.edges), 2)  # <---- THIS IS FAILING

    def test_merge_attrs(self):
        """
        2. when add multiple paresemodels to the displaymodel classes in both pmodels
        can miss out on their full set of attrs/methods depending on the order of pmodels.
        (cos attrs/methods might not be merging)
        """
        source_code1 = """
class Fred(Mary):
    pass
        """
        pmodel1, debuginfo = parse_source(source_code1, options={})

        source_code2 = """
class Fred(Mary):
    def __init__(self):
        self.attr1 = None
    def method1(self):
        pass
        """
        pmodel2, debuginfo = parse_source(source_code2, options={})

        # now add both pmodels to the same display model - hopefully
        dmodel = DisplayModel()

        # first parse of class Fred - no attributes or methods, but inherits from Mary
        dmodel.build_displaymodel(pmodel1)
        # dmodel.Dump()

        # check the parsemodel
        # self.assertEqual(list(pmodel1.classlist.keys()), ["Fred", "Mary"])   # seems that parent doesn't get officially created
        self.assertEqual(pmodel1.classlist["Fred"].attrs, [])
        self.assertEqual(pmodel1.classlist["Fred"].defs, [])
        # check the displaymodel
        self.assertEqual(len(dmodel.graph.nodes), 2)
        self.assertEqual(len(dmodel.graph.edges), 1)
        node = dmodel.graph.FindNodeById("Fred")
        self.assertEqual(node.attrs, [])
        self.assertEqual(node.meths, [])

        # second parse of class Fred - one attributes one method, and still inherits from Mary
        dmodel.build_displaymodel(pmodel2)
        # dmodel.Dump()

        # check the parsemodel
        # self.assertEqual(list(pmodel1.classlist.keys()), ["Fred", "Mary"])   # seems that parent doesn't get officially created

        # the main point of this test
        self.assertEqual(pmodel2.classlist["Fred"].attrs[0].attrname, "attr1")
        self.assertEqual(pmodel2.classlist["Fred"].defs, ["__init__", "method1"])

        # check the displaymodel
        self.assertEqual(len(dmodel.graph.nodes), 2)
        self.assertEqual(len(dmodel.graph.edges), 1)  # relies on edge duplicate protection fix
        node = dmodel.graph.FindNodeById("Fred")
        # test the merging has occurred
        self.assertEqual(node.attrs, ["attr1"])
        self.assertCountEqual(node.meths, ["__init__", "method1"])  # relies on edge duplicate fix


"""
Differences between old parser model used in pynsource and GitUML alsm

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

+ other differences not documented yet.    
"""
