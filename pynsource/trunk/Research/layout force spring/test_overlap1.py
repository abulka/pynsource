import unittest

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

        numfixed = self.overlap_remover.remove_overlaps()
        self.assertEqual(0, numfixed)

    def testTwoNode_notoverlapping(self):
        g = self.g
        g.addNode(Div('A', 0, 0, 250, 250))
        g.addNode(Div('B', 260, 0, 250, 250))

        numfixed = self.overlap_remover.remove_overlaps()
        self.assertEqual(0, numfixed)

    def testTwoNode_overlapping(self):
        g = self.g
        g.addNode(Div('A', 0, 0, 250, 250))
        g.addNode(Div('B', 200, 0, 250, 250))

        numfixed = self.overlap_remover.remove_overlaps()
        self.assertEqual(1, numfixed)

    def testOverlapRemoverCreation(self):
        g = self.g
        a = Div('A', 0, 0, 250, 250)
        a1 = Div('A1', 0, 0)
        a2 = Div('A2', 0, 0)
        g.addEdge(a, a1)
        g.addEdge(a, a2)

        numfixed = self.overlap_remover.remove_overlaps()
        self.assertEqual(4, numfixed)




if __name__ == "__main__":
    unittest.main()
