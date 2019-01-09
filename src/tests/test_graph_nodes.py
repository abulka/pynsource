import sys

sys.path.append("../src")
from view.graph import Graph, GraphNode
from layout.line_intersection import FindLineIntersection

import os
import unittest


class TestCase_A(unittest.TestCase):
    def test_1_Basics(self):
        g = Graph()

        n1 = GraphNode("A", 0, 0, 200, 200)
        n2 = GraphNode("B", 0, 0, 200, 200)
        g.AddEdge(n1, n2)

        # for node in g.nodes:
        #    print node, "layout info:", (node.layoutPosX, node.layoutPosY)

        # print g.GraphToString().strip()

        assert len(g.nodes) == 2
        assert len(list(g.nodeSet.keys())) == 2
        assert len(g.edges) == 1
        g.DeleteNodeById("B")
        assert len(g.nodes) == 1
        assert len(list(g.nodeSet.keys())) == 1
        assert len(g.edges) == 0

        # Old persistence format - very simple, I call this 0.9 format.
        filedata = """
{'type':'node', 'id':'c', 'x':230, 'y':174, 'width':60, 'height':120}
{'type':'node', 'id':'c1', 'x':130, 'y':174, 'width':60, 'height':120}
{'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1'}
    """
        g.Clear()
        assert len(g.nodes) == 0
        assert g.GraphToString().strip() == ""

        g.LoadGraphFromStrings(filedata)
        # for node in g.nodes:
        #    print node, "layout info:", (node.layoutPosX, node.layoutPosY)
        # assert g.GraphToString().strip() == filedata.strip(), g.GraphToString().strip() # no longer true since upgrades to persistence format will translate the incoming text

        # Line intersection tests

        res = FindLineIntersection((0, 0), (200, 200), (10, 10), (10, 50))
        assert res == [10, 10]

        res = FindLineIntersection((0, 30), (200, 30), (10, 10), (10, 50))
        assert res == [10, 30]

        node = GraphNode("A", 10, 10, 30, 40)
        assert len(node.lines) == 4
        assert (10, 10) in node.lines[0]
        assert (40, 10) in node.lines[0]
        assert (40, 10) in node.lines[1]
        assert (40, 50) in node.lines[1]
        assert (40, 50) in node.lines[2]
        assert (10, 50) in node.lines[2]
        assert (10, 50) in node.lines[3]
        assert (10, 10) in node.lines[3]

        res = node.CalcLineIntersectionPoints((0, 0), (200, 200))
        assert len(res) == 2
        assert (10, 10) in res
        assert (40, 40) in res

        res = node.CalcLineIntersectionPoints((20, 0), (20, 1000))
        assert len(res) == 2
        assert (20, 10) in res
        assert (20, 50) in res

    """
    TESTS re generalisation sort order
    """

    def test_2_generalisation_sort_order(self):
        # C --|> B --|> A
        g = Graph()
        c = GraphNode("C", 0, 0, 200, 200)
        b = GraphNode("B", 0, 0, 200, 200)  # parent of C
        a = GraphNode("A", 0, 0, 200, 200)  # parent of B
        # add out of order
        g.AddNode(b)
        g.AddNode(c)
        g.AddNode(a)
        g.AddEdge(c, b)["uml_edge_type"] = "generalisation"
        g.AddEdge(b, a)["uml_edge_type"] = "generalisation"
        nodelist_normal = [node.id for node in g.nodes]
        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        nodelist_sorted_expected = ["A", "B", "C"]
        # print "nodelist_normal", nodelist_normal
        # print "nodelist_sorted_expected", nodelist_sorted_expected
        # print "nodelist_sorted", nodelist_sorted
        assert nodelist_sorted_expected == nodelist_sorted

        # D --|> C --|> B --|> A
        d = GraphNode("D", 0, 0, 200, 200)
        g.AddNode(d)
        g.AddEdge(d, c)["uml_edge_type"] = "generalisation"
        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        nodelist_sorted_expected = ["A", "B", "C", "D"]
        assert nodelist_sorted_expected == nodelist_sorted

        # E node not connected to anything
        e = GraphNode("E", 0, 0, 200, 200)
        g.AddNode(e)
        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        nodelist_sorted_expected = ["A", "B", "C", "D", "E"]
        assert nodelist_sorted_expected == nodelist_sorted

        # D --|> C --|> B --|> A
        # E
        # C2 --|> B
        c2 = GraphNode("C2", 0, 0, 200, 200)
        g.AddNode(c2)
        g.AddEdge(c2, b)["uml_edge_type"] = "generalisation"
        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        nodelist_sorted_expected = ["A", "B", "C", "C2", "D", "E"]
        assert nodelist_sorted_expected == nodelist_sorted

    def test_3_generalisation_sort_order(self):
        # START AGAIN - more tests, ensure children nodes with children themselves, are prioritised

        # C2,C --|> B
        # B,B2 --|> A
        g = Graph()
        c = GraphNode("C", 0, 0, 200, 200)
        c2 = GraphNode("C2", 0, 0, 200, 200)
        b = GraphNode("B", 0, 0, 200, 200)
        b2 = GraphNode("B2", 0, 0, 200, 200)
        a = GraphNode("A", 0, 0, 200, 200)
        # add out of order
        g.AddNode(b2)
        g.AddNode(b)
        g.AddNode(c)
        g.AddNode(c2)
        g.AddNode(a)
        g.AddEdge(c, b)["uml_edge_type"] = "generalisation"
        g.AddEdge(c2, b)["uml_edge_type"] = "generalisation"
        g.AddEdge(b2, a)["uml_edge_type"] = "generalisation"
        g.AddEdge(b, a)["uml_edge_type"] = "generalisation"
        nodelist_normal = [node.id for node in g.nodes]
        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        nodelist_sorted_expected = ["A", "B", "B2", "C", "C2"]
        nodelist_sorted_expected2 = ["A", "B", "B2", "C2", "C"]
        # print "nodelist_normal", nodelist_normal
        # print "nodelist_sorted_expected", nodelist_sorted_expected
        # print "nodelist_sorted", nodelist_sorted
        assert (
            nodelist_sorted_expected == nodelist_sorted
            or nodelist_sorted_expected2 == nodelist_sorted
        )

    def test_4_generalisation_sort_order(self):
        # START AGAIN - more tests, ensure children nodes with children themselves, are prioritised
        # and furthermore, children with the most descendants are prioritised even more.

        # B,B1 --|> A
        # C --|> B
        g = Graph()
        c = GraphNode("C", 0, 0, 200, 200)
        b = GraphNode("B", 0, 0, 200, 200)
        b1 = GraphNode("B1", 0, 0, 200, 200)
        a = GraphNode("A", 0, 0, 200, 200)
        c2 = GraphNode("C2", 0, 0, 200, 200)
        d = GraphNode("D", 0, 0, 200, 200)
        # add out of order
        g.AddNode(b1)
        g.AddNode(b)
        g.AddNode(a)
        g.AddNode(c)
        g.AddNode(c2)
        g.AddNode(d)
        g.AddEdge(c2, b1)["uml_edge_type"] = "generalisation"
        g.AddEdge(d, c)["uml_edge_type"] = "generalisation"
        g.AddEdge(c, b)["uml_edge_type"] = "generalisation"
        g.AddEdge(b1, a)["uml_edge_type"] = "generalisation"
        g.AddEdge(b, a)["uml_edge_type"] = "generalisation"
        nodelist_normal = [node.id for node in g.nodes]
        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        nodelist_sorted_expected = ["A", "B", "B1", "C", "D", "C2"]
        # print "nodelist_normal", nodelist_normal
        # print "nodelist_sorted_expected", nodelist_sorted_expected
        # print "nodelist_sorted", nodelist_sorted
        assert nodelist_sorted_expected == nodelist_sorted

    def test_5_generalisation_sort_order(self):
        # START AGAIN - more tests, check stranger trees, though the algorithm
        # is proving pretty smart, prioritising children who have children to the left

        # B,B1,C,K --|> A
        # D --|> C
        g = Graph()
        a = GraphNode("A", 0, 0, 200, 200)
        b = GraphNode("B", 0, 0, 200, 200)
        b1 = GraphNode("B1", 0, 0, 200, 200)
        c = GraphNode("C", 0, 0, 200, 200)
        k = GraphNode("K", 0, 0, 200, 200)
        d = GraphNode("D", 0, 0, 200, 200)
        # add out of order
        g.AddNode(b1)
        g.AddNode(b)
        g.AddNode(a)
        g.AddNode(c)
        g.AddNode(k)
        g.AddNode(d)
        g.AddEdge(k, a)["uml_edge_type"] = "generalisation"
        g.AddEdge(d, c)["uml_edge_type"] = "generalisation"
        g.AddEdge(c, a)["uml_edge_type"] = "generalisation"
        g.AddEdge(b1, a)["uml_edge_type"] = "generalisation"
        g.AddEdge(b, a)["uml_edge_type"] = "generalisation"
        nodelist_normal = [node.id for node in g.nodes]
        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        # print "nodelist_normal", nodelist_normal
        # print "nodelist_sorted_expected", nodelist_sorted_expected
        # print "nodelist_sorted", nodelist_sorted
        assert nodelist_sorted[0] == "A"
        assert nodelist_sorted[1] == "C"
        assert nodelist_sorted[-1] == "D"

        nodelist_sorted_annotated = [
            (node.id, annotation) for node, annotation in g.nodes_sorted_by_generalisation
        ]
        assert nodelist_sorted_annotated[0] == ("A", "root")
        assert nodelist_sorted_annotated[1] == ("C", "fc")
        assert nodelist_sorted_annotated[-1] == ("D", "fc")
        assert ("K", "tab") in nodelist_sorted_annotated
        assert ("B", "tab") in nodelist_sorted_annotated
        assert ("B1", "tab") in nodelist_sorted_annotated

    def test_6_generalisation_sort_order(self):
        # START AGAIN - more tests, check stranger trees

        # B,D,F --|> A
        # G --|> C --|> B
        # E --|> D
        g = Graph()
        a = GraphNode("A", 0, 0, 200, 200)
        b = GraphNode("B", 0, 0, 200, 200)
        c = GraphNode("C", 0, 0, 200, 200)
        d = GraphNode("D", 0, 0, 200, 200)
        e = GraphNode("E", 0, 0, 200, 200)
        f = GraphNode("F", 0, 0, 200, 200)
        h = GraphNode("H", 0, 0, 200, 200)
        # add out of order
        g.AddNode(f)
        g.AddNode(b)
        g.AddNode(a)
        g.AddNode(h)
        g.AddNode(c)
        g.AddNode(e)
        g.AddNode(d)
        g.AddEdge(b, a)["uml_edge_type"] = "generalisation"
        g.AddEdge(d, a)["uml_edge_type"] = "generalisation"
        g.AddEdge(f, a)["uml_edge_type"] = "generalisation"
        g.AddEdge(h, c)["uml_edge_type"] = "generalisation"
        g.AddEdge(c, b)["uml_edge_type"] = "generalisation"
        g.AddEdge(e, d)["uml_edge_type"] = "generalisation"
        nodelist_normal = [node.id for node in g.nodes]

        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        nodelist_sorted_expected = ["A", "B", "D", "F", "C", "H", "E"]
        assert nodelist_sorted_expected == nodelist_sorted

        nodelist_sorted_annotated = [
            (node.id, annotation) for node, annotation in g.nodes_sorted_by_generalisation
        ]
        nodelist_sorted_expected_annotated = [
            ("A", "root"),
            ("B", "fc"),
            ("D", "tab"),
            ("F", "tab"),
            ("C", "fc"),
            ("H", "fc"),
            ("E", "root"),
        ]
        assert nodelist_sorted_expected_annotated == nodelist_sorted_annotated

        # print "nodelist_normal", nodelist_normal
        # print "nodelist_sorted_expected", nodelist_sorted_expected
        # print "nodelist_sorted", nodelist_sorted

    def test_7_generalisation_multiple_inhertitance(self):
        # START AGAIN - more tests, check multiple inheritance trees

        # See 'python-in/testmodule08_multiple_inheritance.py'
        # for another related unit test

        # F --|> M
        # F --|> S
        g = Graph()
        f = GraphNode("F", 0, 0, 200, 200)
        m = GraphNode("M", 0, 0, 200, 200)
        s = GraphNode("S", 0, 0, 200, 200)
        g.AddEdge(f, m)["uml_edge_type"] = "generalisation"
        g.AddEdge(f, s)["uml_edge_type"] = "generalisation"

        nodelist_normal = [node.id for node in g.nodes]
        # print "nodelist_normal", nodelist_normal

        nodelist_sorted = [node.id for node, annotation in g.nodes_sorted_by_generalisation]
        nodelist_sorted_expected = ["M", "F", "S"]
        assert nodelist_sorted_expected == nodelist_sorted, nodelist_sorted

        # print "nodelist_sorted_expected", nodelist_sorted_expected
        # print "nodelist_sorted", nodelist_sorted

        nodelist_sorted_annotated = [
            (node.id, annotation) for node, annotation in g.nodes_sorted_by_generalisation
        ]
        nodelist_sorted_expected_annotated = [("M", "root"), ("F", "root"), ("S", "root")]
        assert (
            nodelist_sorted_expected_annotated == nodelist_sorted_annotated
        ), nodelist_sorted_annotated

        # print "nodelist_sorted_expected_annotated", nodelist_sorted_expected_annotated
        # print "nodelist_sorted_annotated", nodelist_sorted_annotated
        # print

    def test_8_multiple_inhertitance_render(self):
        # F --|> M
        # F --|> S
        g = Graph()
        f = GraphNode("F", 0, 0, 200, 200)
        m = GraphNode("M", 0, 0, 200, 200)
        s = GraphNode("S", 0, 0, 200, 200)
        g.AddEdge(f, m)["uml_edge_type"] = "generalisation"
        g.AddEdge(f, s)["uml_edge_type"] = "generalisation"
        nodelist_normal = [node.id for node in g.nodes]

        """
        Custom ordering allows us to bypass the graph 'nodes_sorted_by_generalisation'
        algorithm which might either be crashing or have unwanted ordering results.
        Thus we can experiment with how different experimental orderings will render.
        """
        mycustom_ordering = [(m, "root"), (s, "root"), (f, "root")]

        from ascii_uml.layout_ascii import model_to_ascii_builder

        m = model_to_ascii_builder()
        s = m.main(g, nodes_annotated_and_sorted=mycustom_ordering)

        expected_s = r"""
+---+
| M |
+---+
                      
                      
                      
+---+       [ S ][ M ]
| S |        .        
+---+       /_\       
             |        
             |        
            +---+     
            | F |     
            +---+     
        """

        def remove_blank_lines(str):
            return os.linesep.join([s for s in str.splitlines() if s.strip()])

        # remove blank lines, since different margins and paddings in ascii uml layout
        # could cause difference
        expected_s = remove_blank_lines(expected_s)
        s = remove_blank_lines(s)

        # print
        # print "*"*88
        # print expected_s
        # print "*"*88
        # print s
        # print "*"*88

        if s.strip() != expected_s.strip():
            print(s.strip())
            print(expected_s.strip())
            # Write to file
            with open(os.path.abspath("tests/logs/test_8_out_actual_.txt"), "w") as f:
                f.write(s)
            with open(os.path.abspath("tests/logs/test_8_out_expected.txt"), "w") as f:
                f.write(expected_s)

            import difflib

            # delta = difflib.ndiff(s.strip(), expected_s.strip()) # this will always emit something, a visual of the original with changes.
            delta = difflib.unified_diff(
                s.strip(), expected_s.strip(), n=0, fromfile="actual", tofile="expected"
            )
            diff_s = "".join(delta)
            print(diff_s)

        assert s.strip() == expected_s.strip()


def suite():
    suite1 = unittest.makeSuite(TestCase_A, "test")
    # suite2 = unittest.makeSuite(test_2_subsidiary_parsing, 'test')
    # suite3 = unittest.makeSuite(test_3_ast_parsing_is_genuinely_better, 'test')
    # suite4 = unittest.makeSuite(TestCase_D_MultipleAttrBeforeClassic, 'test')
    # suite5 = unittest.makeSuite(TestCase_E_DoubleCall, 'test')
    # suite6 = unittest.makeSuite(TestCase_F_CallThenTrailingInstance, 'test')
    # suite7 = unittest.makeSuite(TestCase_G_AttrBeforeRhsInstance, 'test')
    # suite8 = unittest.makeSuite(TestCase_AddHoc, 'test')
    # alltests = unittest.TestSuite((suite1, suite2, suite3, suite4, suite5, suite6, suite7))
    alltests = unittest.TestSuite((suite1,))
    # alltests = unittest.TestSuite((suite1, suite2, suite3))
    return alltests


def main():
    runner = unittest.TextTestRunner(
        descriptions=0, verbosity=2
    )  # default is descriptions=1, verbosity=1
    runner.run(suite())


if __name__ == "__main__":
    main()
