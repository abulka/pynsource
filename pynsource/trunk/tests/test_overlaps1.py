import unittest

import sys
sys.path.append("../Research/layout force spring")

from overlap_removal import OverlapRemoval
from graph import Graph, GraphNode, Div

        
class MathLibraryTests(unittest.TestCase):

    def setUp(self):

        class FakeGui:
            def stateofthenation(self):
                pass

        self.g = Graph()
        self.overlap_remover = OverlapRemoval(self.g, gui=FakeGui())
        
    def testOneNode(self):
        g = self.g
        g.addNode(Div('A', 0, 0, 250, 250))

        were_all_overlaps_removed, numfixed = self.overlap_remover.remove_overlaps()
        self.assertEqual(0, numfixed)

    def testTwoNode_notoverlapping(self):
        g = self.g
        g.addNode(Div('A', 0, 0, 250, 250))
        g.addNode(Div('B', 260, 0, 250, 250))

        were_all_overlaps_removed, numfixed = self.overlap_remover.remove_overlaps()
        self.assertEqual(0, numfixed)

    def testTwoNode_overlapping(self):
        g = self.g
        g.addNode(Div('A', 0, 0, 250, 250))
        g.addNode(Div('B', 200, 0, 250, 250))

        were_all_overlaps_removed, numfixed = self.overlap_remover.remove_overlaps()
        self.assertEqual(1, numfixed)

    def testOverlapRemoverCreation(self):
        g = self.g
        a = Div('A', 0, 0, 250, 250)
        a1 = Div('A1', 0, 0)
        a2 = Div('A2', 0, 0)
        g.addEdge(a, a1)
        g.addEdge(a, a2)

        were_all_overlaps_removed, numfixed = self.overlap_remover.remove_overlaps()
        self.assertEqual(4, numfixed)


    def testMoveLeftPushedBackHorizontally01(self):
        initial = """
{'type':'node', 'id':'D25', 'x':6, 'y':7, 'width':159, 'height':106}
{'type':'node', 'id':'D13', 'x':6, 'y':119, 'width':119, 'height':73}
{'type':'node', 'id':'m1', 'x':170, 'y':9, 'width':139, 'height':92}
"""
        self.g.LoadGraphFromStrings(initial)
        
        # move m1 to the left
        node = self.g.findNode('m1')
        node.value.left, node.value.top = (150, 9)

        # assert m1 has been pushed back to the right
        # assert no overlaps
        were_all_overlaps_removed, numfixed = self.overlap_remover.remove_overlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, numfixed)
        self.assertTrue(node.value.left > self.g.findNode('D25').value.right)
        self.assertTrue(node.value.top < self.g.findNode('D25').value.bottom)

    def testMoveLeftPushedBackDownRight02(self):
        initial = """
{'type':'node', 'id':'D25', 'x':6, 'y':7, 'width':159, 'height':106}
{'type':'node', 'id':'D13', 'x':6, 'y':119, 'width':119, 'height':73}
{'type':'node', 'id':'m1', 'x':170, 'y':9, 'width':139, 'height':92}
"""
        self.g.LoadGraphFromStrings(initial)
        
        # move m1 to the left
        node = self.g.findNode('m1')
        node.value.left, node.value.top = (106, 79)
        
        # assert m1 has been pushed back to the right
        # assert no overlaps
        were_all_overlaps_removed, numfixed = self.overlap_remover.remove_overlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, numfixed)
        
        self.assertTrue(node.value.left > self.g.findNode('D13').value.right)
        self.assertTrue(node.value.top > self.g.findNode('D25').value.bottom)
        
if __name__ == "__main__":
    unittest.main()
