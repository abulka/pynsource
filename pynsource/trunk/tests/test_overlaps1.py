import unittest

import sys
sys.path.append("../Research/layout force spring")

from overlap_removal import OverlapRemoval
from graph import Graph, GraphNode
import pprint
        
class OverlapTests(unittest.TestCase):

    def setUp(self):

        class FakeGui:
            def stateofthenation(self):
                pass

        self.g = Graph()
        self.overlap_remover = OverlapRemoval(self.g, margin=5, gui=FakeGui())

    def tearDown(self):
        pprint.pprint(self.overlap_remover.GetStats())

    def test0_1OneNode(self):
        g = self.g
        g.AddNode(GraphNode('A', 0, 0, 250, 250))

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertEqual(0, self.overlap_remover.GetStats()['total_overlaps_found'])

    def test0_2TwoNode_notoverlapping(self):
        g = self.g
        g.AddNode(GraphNode('A', 0, 0, 250, 250))
        g.AddNode(GraphNode('B', 260, 0, 250, 250))

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertEqual(0, self.overlap_remover.GetStats()['total_overlaps_found'])

    def test0_3TwoNode_overlapping(self):
        g = self.g
        g.AddNode(GraphNode('A', 0, 0, 250, 250))
        g.AddNode(GraphNode('B', 200, 0, 250, 250))

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertEqual(1, self.overlap_remover.GetStats()['total_overlaps_found'])

    def test0_4OverlapRemoverCreation(self):
        g = self.g
        a = GraphNode('A', 0, 0, 250, 250)
        a1 = GraphNode('A1', 0, 0)
        a2 = GraphNode('A2', 0, 0)
        g.AddEdge(a, a1)
        g.AddEdge(a, a2)

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)

    """
    Smarter tests.
    Load scenarios from persistence and use special box comparison utility methods
    """

    def _ensureXorder(self, *args):
        nodes = [self.g.FindNodeById(id) for id in args]
        assert len(nodes) >= 2
        for i in range(0,len(nodes)-1):
            if not nodes[i].right < nodes[i+1].left:
                return False
        return True

    def _ensureXorderLefts(self, *args):
        nodes = [self.g.FindNodeById(id) for id in args]
        assert len(nodes) >= 2
        for i in range(0,len(nodes)-1):
            if not nodes[i].left < nodes[i+1].left:
                return False
        return True

    def _ensureYorder(self, *args):
        nodes = [self.g.FindNodeById(id) for id in args]
        assert len(nodes) >= 2
        for i in range(0,len(nodes)-1):
            if not nodes[i].bottom < nodes[i+1].top:
                return False
        return True

    def _ensureYorderBottoms(self, *args):
        nodes = [self.g.FindNodeById(id) for id in args]
        assert len(nodes) >= 2
        for i in range(0,len(nodes)-1):
            if not nodes[i].bottom < nodes[i+1].bottom:
                return False
        return True
    


    def _LoadScenario1(self):
        initial = """
{'type':'node', 'id':'D25', 'x':6, 'y':7, 'width':159, 'height':106}
{'type':'node', 'id':'D13', 'x':6, 'y':119, 'width':119, 'height':73}
{'type':'node', 'id':'m1', 'x':170, 'y':9, 'width':139, 'height':92}
"""
        self.g.LoadGraphFromStrings(initial)

    def test1_1MoveLeftPushedBackHorizontally01(self):
        self._LoadScenario1()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (150, 9)

        # assert m1 has been pushed back to the right
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()['total_overlaps_found'])
        self.assertTrue(node.left > self.g.FindNodeById('D25').right)
        self.assertTrue(node.top < self.g.FindNodeById('D25').bottom)

    def test1_2MoveLeftPushedBackDownRight02(self):
        self._LoadScenario1()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (106, 79)
        
        # assert m1 has been pushed back to the right but also down
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()['total_overlaps_found'])
        
        self.assertTrue(node.left > self.g.FindNodeById('D13').right)
        self.assertTrue(node.top > self.g.FindNodeById('D25').bottom)
        
    def test1_3MoveInsertedVertically1(self):
        self._LoadScenario1()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (16,74)
        
        # assert m1 has been squeezed in between the two existing
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()['total_overlaps_found'])
        
        #print self.g.GraphToString()
        self.assertTrue(node.top > self.g.FindNodeById('D25').bottom)
        self.assertTrue(node.bottom < self.g.FindNodeById('D13').top)
        self.assertTrue(self.g.FindNodeById('D13').top > self.g.FindNodeById('D25').bottom)
        self.assertTrue(node.left < self.g.FindNodeById('D25').right)
        self.assertTrue(node.left < self.g.FindNodeById('D13').right)
        
    def test1_4MovePushedVertically2(self):
        self._LoadScenario1()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (6,154)
        
        # assert m1 has been pushed vertically underneath the other two nodes
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()['total_overlaps_found'])

        self.assertTrue(self._ensureYorder('D25', 'D13', 'm1'))
        
        self.assertTrue(node.left < self.g.FindNodeById('D25').right)
        self.assertTrue(node.left < self.g.FindNodeById('D13').right)
        
        
    def _LoadScenario2(self):
        initial = """
{'type':'node', 'id':'D25', 'x':7, 'y':6, 'width':159, 'height':106}
{'type':'node', 'id':'D13', 'x':6, 'y':119, 'width':119, 'height':73}
{'type':'node', 'id':'m1', 'x':146, 'y':179, 'width':139, 'height':92}
{'type':'node', 'id':'D97', 'x':213, 'y':6, 'width':85, 'height':159}
"""
        self.g.LoadGraphFromStrings(initial)        
        
    def test2_1InsertAndPushedRightHorizontally(self):
        self._LoadScenario2()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (121,14)
        
        # assert m1 has been inserted and node to the right pushed right
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()['total_overlaps_found'])
        
        self.assertTrue(self._ensureXorder('D25', 'm1', 'D97'))
        self.assertTrue(self._ensureYorderBottoms('m1', 'D97')) # m1 bottom above D97 bottom

    def test2_2PushedRightAndDownNicely(self):
        self._LoadScenario2()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (96, 114)
        
        # assert m1 has been pushed down and right nicely and snugly
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()['total_overlaps_found'])
        
        self.assertTrue(self._ensureXorder('D13', 'm1'))
        self.assertTrue(self._ensureXorderLefts('D13', 'm1', 'D97'))
        self.assertTrue(self._ensureXorderLefts('D25', 'm1', 'D97'))
        self.assertTrue(self._ensureYorderBottoms('D25', 'D97', 'm1'))
        self.assertTrue(self._ensureYorder('D25', 'm1'))
        self.assertTrue(self._ensureYorderBottoms('D25', 'D13', 'm1'))
        self.assertTrue(self._ensureYorderBottoms('D25', 'D97', 'm1'))


    def _LoadScenario3(self):
        initial = """
{'type':'node', 'id':'D25', 'x':7, 'y':6, 'width':159, 'height':106}
{'type':'node', 'id':'D13', 'x':6, 'y':119, 'width':119, 'height':73}
{'type':'node', 'id':'m1', 'x':246, 'y':179, 'width':139, 'height':92}
{'type':'node', 'id':'D97', 'x':213, 'y':6, 'width':85, 'height':159}
{'type':'node', 'id':'D98', 'x':340, 'y':7, 'width':101, 'height':107}
"""
        self.g.LoadGraphFromStrings(initial)  
        
    def test3_1PushedBetweenLeftAndRight(self):
        self._LoadScenario3()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (266, 9)
        
        # assert m1 has been pushed between two nodes, horizontally.  Both left and right nodes moved left and right respectively.
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()['total_overlaps_found'])
        
        self.assertTrue(self._ensureXorder('D25', 'D97', 'm1', 'D98'))
        self.assertTrue(self._ensureYorder('D25', 'D13'))
        self.assertTrue(self._ensureYorderBottoms('D25', 'D97', 'D13'))

    def test3_2PushedBetweenLeftAndRightRefused(self):
        self._LoadScenario3()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (226, 14)
        
        # assert m1 has been not been inserted - refused and snuggled instead
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()['total_overlaps_found'])
        
        self.assertTrue(self._ensureXorder('D25', 'D97', 'D98'))
        self.assertTrue(self._ensureXorder('D25', 'D97', 'm1'))
        self.assertTrue(self._ensureYorder('D98', 'm1'))
        self.assertTrue(self._ensureYorderBottoms('D98', 'D97', 'm1'))

    def test3_2aPushedRefusedButLeftMovedAnyway(self):
        self._LoadScenario3()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (281, 64)

        d97 = self.g.FindNodeById('D97')
        oldD97pos = (d97.left, d97.top)
        
        # assert m1 has been refused insertion, but left (D97) moved leftwards cos there is room.  m1 snuggled below and to the right.
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()['total_overlaps_found'])

        self.assertTrue(self._ensureXorder('D25', 'D97', 'D98'))
        self.assertTrue(self._ensureXorder('D13', 'D97', 'm1'))
        self.assertTrue(self._ensureYorder('D25', 'D13'))
        self.assertTrue(self._ensureYorder('D98', 'm1'))
        self.assertTrue(self._ensureYorderBottoms('D98', 'D97', 'm1'))
        self.assertNotEqual(oldD97pos, (d97.left, d97.top)) # ensure D97 HAS been pushed left
        
    def test3_3InsertedAndTwoPushedRight(self):
        self._LoadScenario3()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (146, 9)
        
        # assert m1 has been inserted - and two nodes pushed right
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(3, self.overlap_remover.GetStats()['total_overlaps_found'])
        
        self.assertTrue(self._ensureXorder('D25', 'm1', 'D97', 'D98'))
         
    def test3_4InsertedVerticallyNothingPushedRight(self):
        self._LoadScenario3()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (91, 64)
        
        d97 = self.g.FindNodeById('D97')
        oldD97pos = (d97.left, d97.top)

        # assert m1 has been inserted vertically - one node pushed down, NO nodes pushed right
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(5, self.overlap_remover.GetStats()['total_overlaps_found'])

        self.assertTrue(self._ensureXorder('D25', 'D97', 'D98'))
        self.assertTrue(self._ensureXorder('m1', 'D97', 'D98'))
        self.assertTrue(self._ensureYorder('D25', 'm1', 'D13'))
        self.assertTrue(self._ensureYorder('D25', 'm1', 'D13'))
        self.assertEqual(oldD97pos, (d97.left, d97.top)) # ensure D97 hasn't been pushed

    def test3_5InsertedVerticallyTwoPushedDown(self):
        self._LoadScenario3()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (6, 4)
        
        d97 = self.g.FindNodeById('D97')
        oldD97pos = (d97.left, d97.top)

        # assert m1 has been inserted vertically - two pushed down
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()['total_overlaps_found'])

        self.assertTrue(self._ensureYorder('m1', 'D25', 'D13'))
        self.assertTrue(self._ensureXorder('m1', 'D97', 'D98'))
        self.assertTrue(self._ensureXorder('D25', 'D97', 'D98'))
        self.assertTrue(self._ensureXorder('D13', 'D97', 'D98'))
        self.assertEqual(oldD97pos, (d97.left, d97.top)) # ensure D97 hasn't been pushed

    def _LoadScenario4(self):
        initial = """
{'type':'node', 'id':'D25', 'x':7, 'y':6, 'width':159, 'height':106}
{'type':'node', 'id':'D13', 'x':6, 'y':119, 'width':119, 'height':73}
{'type':'node', 'id':'m1', 'x':6, 'y':214, 'width':139, 'height':92}
{'type':'node', 'id':'D97', 'x':213, 'y':6, 'width':85, 'height':159}
{'type':'node', 'id':'D98', 'x':305, 'y':57, 'width':101, 'height':107}
{'type':'node', 'id':'D50', 'x':149, 'y':184, 'width':242, 'height':112}
{'type':'node', 'id':'D51', 'x':189, 'y':302, 'width':162, 'height':66}
"""
        self.g.LoadGraphFromStrings(initial)  

    def test4_1InsertedTwoPushedRightTwoPushedDown(self):
        self._LoadScenario4()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (136, 99)
        
        d97 = self.g.FindNodeById('D97')
        d98 = self.g.FindNodeById('D98')
        d50 = self.g.FindNodeById('D50')
        d51 = self.g.FindNodeById('D51')
        oldD97pos = (d97.left, d97.top)
        oldD98pos = (d98.left, d98.top)
        oldD50pos = (d50.left, d50.top)
        oldD51pos = (d51.left, d51.top)

        # assert m1 has been inserted - two pushed right, two pushed down
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(5, self.overlap_remover.GetStats()['total_overlaps_found'])

        self.assertTrue(self._ensureXorder('D13', 'm1', 'D97', 'D98'))
        self.assertTrue(self._ensureXorder('D25', 'D97', 'D98'))
        self.assertTrue(self._ensureYorder('D25', 'D13', 'D50', 'D51'))
        self.assertTrue(self._ensureYorder('D25', 'm1', 'D50', 'D51'))
        self.assertTrue(self._ensureYorder('D97', 'D50', 'D51'))
        self.assertTrue(self._ensureYorder('D98', 'D50', 'D51'))
        self.assertTrue(self._ensureXorder('D13', 'D50'))
        self.assertTrue(self._ensureXorder('D13', 'D51'))
        self.assertNotEqual(oldD97pos, (d97.left, d97.top)) # ensure D97 HAS been pushed
        self.assertNotEqual(oldD98pos, (d98.left, d98.top)) # ensure D98 HAS been pushed
        self.assertNotEqual(oldD50pos, (d50.left, d50.top)) # ensure D50 HAS been pushed
        self.assertNotEqual(oldD51pos, (d51.left, d51.top)) # ensure D51 HAS been pushed

    def test4_2InsertedTwoPushedRightThreePushedDown(self):
        self._LoadScenario4()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (101, 99)
        
        d97 = self.g.FindNodeById('D97')
        d98 = self.g.FindNodeById('D98')
        d50 = self.g.FindNodeById('D50')
        d51 = self.g.FindNodeById('D51')
        d13 = self.g.FindNodeById('D13')
        oldD97pos = (d97.left, d97.top)
        oldD98pos = (d98.left, d98.top)
        oldD50pos = (d50.left, d50.top)
        oldD51pos = (d51.left, d51.top)
        oldD13pos = (d13.left, d13.top)

        # assert m1 has been inserted - two pushed right, two pushed down, and extra D13 pushed down
        # because m1 overlaps/attacks D13 (and there is room for D13 to move downwards I guess)
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(6, self.overlap_remover.GetStats()['total_overlaps_found'])

        self.assertFalse(self._ensureXorder('D13', 'm1', 'D97', 'D98')) # not true anymore, m1 not pushed to the right so much 
        self.assertFalse(self._ensureYorder('D25', 'D13', 'D50', 'D51')) # not true anymore,
        
        self.assertTrue(self._ensureXorder('D25', 'D97', 'D98'))
        self.assertTrue(self._ensureXorder('D13', 'D97', 'D98'))
        self.assertTrue(self._ensureXorder('D13', 'D50'))
        self.assertTrue(self._ensureXorder('D13', 'D51'))
        
        self.assertTrue(self._ensureYorder('D25', 'm1', 'D13', 'D51'))
        self.assertTrue(self._ensureYorder('D25', 'm1', 'D50', 'D51'))
        self.assertTrue(self._ensureYorder('D97', 'D50', 'D51'))
        self.assertTrue(self._ensureYorder('D98', 'D50', 'D51'))
        self.assertTrue(self._ensureYorderBottoms('D25', 'D97', 'm1', 'D13', 'D50', 'D51'))

        self.assertNotEqual(oldD97pos, (d97.left, d97.top)) # ensure D97 HAS been pushed
        self.assertNotEqual(oldD98pos, (d98.left, d98.top)) # ensure D98 HAS been pushed
        self.assertNotEqual(oldD50pos, (d50.left, d50.top)) # ensure D50 HAS been pushed
        self.assertNotEqual(oldD51pos, (d51.left, d51.top)) # ensure D51 HAS been pushed
        self.assertNotEqual(oldD13pos, (d13.left, d13.top)) # ensure D13 HAS been pushed

    def _LoadScenario5_stress(self):
        initial = """
{'type':'node', 'id':'A', 'x':230, 'y':118, 'width':250, 'height':250}
{'type':'node', 'id':'A1', 'x':252, 'y':10, 'width':60, 'height':60}
{'type':'node', 'id':'A2', 'x':143, 'y':48, 'width':60, 'height':60}
{'type':'node', 'id':'B', 'x':87, 'y':245, 'width':60, 'height':60}
{'type':'node', 'id':'B1', 'x':10, 'y':199, 'width':60, 'height':60}
{'type':'node', 'id':'B2', 'x':190, 'y':253, 'width':60, 'height':60}
{'type':'node', 'id':'B21', 'x':262, 'y':161, 'width':60, 'height':60}
{'type':'node', 'id':'B22', 'x':139, 'y':351, 'width':100, 'height':200}
{'type':'node', 'id':'c', 'x':301, 'y':259, 'width':60, 'height':60}
{'type':'node', 'id':'c1', 'x':261, 'y':372, 'width':60, 'height':60}
{'type':'node', 'id':'c2', 'x':395, 'y':201, 'width':60, 'height':60}
{'type':'node', 'id':'c3', 'x':402, 'y':302, 'width':60, 'height':60}
{'type':'node', 'id':'c4', 'x':338, 'y':379, 'width':60, 'height':60}
{'type':'node', 'id':'c5', 'x':244, 'y':207, 'width':60, 'height':120}
{'type':'node', 'id':'BIG1', 'x':0, 'y':0, 'width':300, 'height':200}
{'type':'node', 'id':'BIG2', 'x':1, 'y':1, 'width':300, 'height':200}
{'type':'node', 'id':'BIG3', 'x':2, 'y':2, 'width':300, 'height':200}
{'type':'edge', 'id':'A_to_A1', 'source':'A', 'target':'A1'}
{'type':'edge', 'id':'A_to_A2', 'source':'A', 'target':'A2'}
{'type':'edge', 'id':'B_to_B1', 'source':'B', 'target':'B1'}
{'type':'edge', 'id':'B_to_B2', 'source':'B', 'target':'B2'}
{'type':'edge', 'id':'B2_to_B21', 'source':'B2', 'target':'B21'}
{'type':'edge', 'id':'B2_to_B22', 'source':'B2', 'target':'B22'}
{'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1'}
{'type':'edge', 'id':'c_to_c2', 'source':'c', 'target':'c2'}
{'type':'edge', 'id':'c_to_c3', 'source':'c', 'target':'c3'}
{'type':'edge', 'id':'c_to_c4', 'source':'c', 'target':'c4'}
{'type':'edge', 'id':'c_to_c5', 'source':'c', 'target':'c5'}
{'type':'edge', 'id':'A_to_c', 'source':'A', 'target':'c'}
{'type':'edge', 'id':'B2_to_c', 'source':'B2', 'target':'c'}
{'type':'edge', 'id':'B2_to_c5', 'source':'B2', 'target':'c5'}
{'type':'edge', 'id':'A_to_c5', 'source':'A', 'target':'c5'}
"""
        self.g.LoadGraphFromStrings(initial)
        
    def testStress1(self):
        
        for i in range(10):
            self._LoadScenario5_stress()
            print "Stress Iteration", i
            were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
            self.assertTrue(were_all_overlaps_removed)
            
            self.g.Clear()
        
    def _LoadScenario6_linecrossing(self):
        initial = """
{'type':'node', 'id':'A', 'x':13, 'y':12, 'width':84, 'height':126}
{'type':'node', 'id':'B', 'x':122, 'y':11, 'width':157, 'height':79}
{'type':'node', 'id':'C', 'x':8, 'y':292, 'width':194, 'height':91}
{'type':'node', 'id':'m1', 'x':102, 'y':95, 'width':123, 'height':144}
{'type':'edge', 'id':'A_to_B', 'source':'A', 'target':'B'}
{'type':'edge', 'id':'A_to_C', 'source':'A', 'target':'C'}
"""        
        self.g.LoadGraphFromStrings(initial)

    def test6_1LineCrossingNotNeeded(self):
        self._LoadScenario6_linecrossing()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        node.left, node.top = (49, 48)
        
        # assert m1 has been repulsed and snuggeled
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()['total_overlaps_found'])

        self.assertTrue(self._ensureXorder('A', 'B'))
        self.assertTrue(self._ensureXorder('A', 'm1'))
        self.assertTrue(self._ensureYorder('A', 'C'))
        self.assertTrue(self._ensureYorder('B', 'm1', 'C'))
        self.assertFalse(self._ensureYorder('A', 'm1', 'C')) # don't want this otherwise the line from A to C would be crossed
        
    def test6_2LineCrossingAvoided(self):
        self._LoadScenario6_linecrossing()
        
        # move m1 to the left
        node = self.g.FindNodeById('m1')
        #node.left, node.top = (9, 103) # A is to the left of A
        node.left, node.top = (24, 98)  # m1 is to the left of A - a bit easier to solve
        
        # assert m1 has been repulsed and snuggeled, and line not crossed - same results as ABOVE
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()['total_overlaps_found'])

        self.assertTrue(self._ensureXorder('A', 'B'))
        self.assertTrue(self._ensureXorder('A', 'm1'))
        self.assertTrue(self._ensureYorder('A', 'C'))
        self.assertTrue(self._ensureYorder('B', 'm1', 'C'))
        self.assertFalse(self._ensureYorder('A', 'm1', 'C')) # don't want this otherwise the line from A to C would be crossed
                
        
if __name__ == "__main__":
    unittest.main()
