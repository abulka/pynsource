import unittest
import tempfile
from parsing.api import old_parser, new_parser
from parsing.dump_pmodel import dump_old_structure
from view.display_model import DisplayModel
from view.display_model import Graph, GraphNode, UmlNode
from unittest import mock
from textwrap import dedent
import os
from parsing.parse_source import parse_source


class TestCaseDisplayModel(unittest.TestCase):
    def test_no_duplicate_edges(self):
        """
        1. Ensure no duplicate edges when add to displaymodel from same parsemodel twice
        """
        source_code = dedent(
            """
            class Fred(Mary, Sam):
                pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={})
        # print(pmodel.classlist)
        # print((dump_old_structure(pmodel)))

        self.assertEqual(list(pmodel.classlist.keys()), ["Fred"])
        self.assertEqual(pmodel.classlist["Fred"].defs, [])
        self.assertEqual(pmodel.classlist["Fred"].classesinheritsfrom, ["Mary", "Sam"])

        # Now convert to a display model

        dmodel = DisplayModel()
        dmodel.build_graphmodel(pmodel)
        # dmodel.Dump()
        self.assertEqual(len(dmodel.graph.nodes), 3)
        self.assertEqual(len(dmodel.graph.edges), 2)
        # print("display model", dmodel)

        # again - should not cause extra edges to be created
        dmodel.build_graphmodel(pmodel)
        # dmodel.Dump()
        self.assertEqual(len(dmodel.graph.nodes), 3)
        self.assertEqual(len(dmodel.graph.edges), 2)

    def test_merge_attrs(self):
        """
        2. when add multiple paresemodels to the displaymodel classes in both pmodels
        can miss out on their full set of attrs/methods depending on the order of pmodels.
        (cos attrs/methods might not be merging)
        """
        source_code1 = dedent(
            """
            class Fred(Mary):
                pass
        """
        )
        pmodel1, debuginfo = parse_source(source_code1, options={})

        source_code2 = dedent(
            """
            class Fred(Mary):
                def __init__(self):
                    self.attr1 = None
                def method1(self):
                    pass
        """
        )
        pmodel2, debuginfo = parse_source(source_code2, options={})

        # now add both pmodels to the same display model - hopefully
        dmodel = DisplayModel()

        # first parse of class Fred - no attributes or methods, but inherits from Mary
        dmodel.build_graphmodel(pmodel1)
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
        dmodel.build_graphmodel(pmodel2)
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

    # @mock.patch('gui.umlcanvas')  # how to patch the right thing?
    @unittest.skipIf("TRAVIS" in os.environ, "no wxpython possible on travis")
    def test_display_model_simplification(self):
        """
        Ensure old display model is no more.
        It is now merely the graph, and graph nodes point to shapes
            - node shapes are attached to nodes as node.shape
            - edge shapes are attached to each edge mapping dictionary
        """
        source_code = dedent(
            """
            class Fred(Mary, Sam):
                pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={})
        dmodel = DisplayModel()
        dmodel.build_graphmodel(pmodel)

        # old extra data structures we don't need
        self.assertIsNone(getattr(dmodel, "classnametoshape", None))
        self.assertIsNone(getattr(dmodel, "associations_generalisation", None))
        self.assertIsNone(getattr(dmodel, "associations_composition", None))
        self.assertIsNone(getattr(dmodel, "associations", None))

        # instead we have graph nodes pointing to shapes
        fred: GraphNode = dmodel.graph.FindNodeById("Fred")
        mary: GraphNode = dmodel.graph.FindNodeById("Mary")
        sam: GraphNode = dmodel.graph.FindNodeById("Sam")
        self.node_check(fred)
        self.node_check(mary)
        self.node_check(sam)

        # and we have graph edges dicts pointing to shapes
        fred_mary = dmodel.graph.FindEdge(fred, mary, "generalisation")
        fred_sam = dmodel.graph.FindEdge(fred, sam, "generalisation")
        self.assertIsNotNone(fred_mary)
        self.assertIsNotNone(fred_sam)

        umlcanvas = self.create_mock_umlcanvas(dmodel)

        dmodel.build_view(purge_existing_shapes=True)  # doesn't matter t/f cos first build
        self.assertTrue(umlcanvas.CreateUmlShape.called)
        self.assertFalse(umlcanvas.createCommentShape.called)
        self.assertTrue(umlcanvas.CreateUmlEdgeShape.called)

        self.assertEqual(umlcanvas.CreateUmlShape.call_count, 3)
        self.assertEqual(umlcanvas.CreateUmlEdgeShape.call_count, 2)

        # Tests - cannot test these cos deep functionality not present in mocked umlcanvas.

        # self.node_check_shape(fred)
        # self.node_check_shape(mary)
        # self.node_check_shape(sam)

        # self.edge_check_line(fred_mary)
        # self.edge_check_line(fred_sam)

    def create_mock_umlcanvas(self, dmodel):
        # this indirectly assumes wx
        from gui.uml_shapes import DividedShape, CommentShape
        from gui.uml_lines import LineShapeUml

        umlcanvas = mock.MagicMock()
        umlcanvas.CreateUmlShape.return_value = mock.MagicMock(spec=DividedShape)
        umlcanvas.createCommentShape.return_value = mock.MagicMock(spec=CommentShape)
        umlcanvas.CreateUmlEdge.return_value = mock.MagicMock(spec=LineShapeUml)
        umlcanvas.app.run.CmdDeselectAllShapes.return_value = None
        umlcanvas.displaymodel = dmodel
        dmodel.umlcanvas = umlcanvas
        return umlcanvas

    def node_check(self, node):
        self.assertIsNotNone(node)
        self.assertIsInstance(node, UmlNode)

    # def node_check_shape(self, node):
    #     self.assertIsNotNone(node.shape)
    #     self.assertIsInstance(node.shape, DividedShape)
    #
    # def edge_check_line(self, edge: dict):
    #     self.assertHasAttr(edge, "line")
    #     self.assertIsInstance(edge["line"], LineShapeUml)

    def test_display_model_general1(self):
        source_code = dedent(
            """
            class Fred(Big):
                self.a = A()
                self.a2 = A()
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={})
        dmodel = DisplayModel()
        dmodel.build_graphmodel(pmodel)
        # dmodel.Dump()

        fred: GraphNode = dmodel.graph.FindNodeById("Fred")
        big: GraphNode = dmodel.graph.FindNodeById("Big")
        a: GraphNode = dmodel.graph.FindNodeById("A")
        self.assertIsNotNone(fred)
        self.assertIsNotNone(big)
        self.assertIsNotNone(a)
        self.assertIsNotNone(dmodel.graph.FindEdge(fred, big, "generalisation"))
        self.assertIsNotNone(dmodel.graph.FindEdge(a, fred, "composition"))


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
