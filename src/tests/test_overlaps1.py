import unittest

import sys

sys.path.append("../src")

from layout.overlap_removal import OverlapRemoval, LINE_NODE_OVERLAP_REMOVAL_ENABLED
from view.graph import Graph, GraphNode
import pprint

from layout.data_testgraphs import *


class OverlapTests(unittest.TestCase):
    def setUp(self):
        class FakeGui:
            def mega_refresh(self, recalibrate=False, auto_resize_canvas=True):
                pass

        self.g = Graph()
        self.overlap_remover = OverlapRemoval(self.g, margin=5, gui=FakeGui())

    def tearDown(self):
        # pprint.pprint(self.overlap_remover.GetStats())
        pass

    def test0_1OneNode(self):
        g = self.g
        g.AddNode(GraphNode("A", 0, 0, 250, 250))

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertEqual(0, self.overlap_remover.GetStats()["total_overlaps_found"])

    def test0_2TwoNode_notoverlapping(self):
        g = self.g
        g.AddNode(GraphNode("A", 0, 0, 250, 250))
        g.AddNode(GraphNode("B", 260, 0, 250, 250))

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertEqual(0, self.overlap_remover.GetStats()["total_overlaps_found"])

    def test0_3TwoNode_overlapping(self):
        g = self.g
        g.AddNode(GraphNode("A", 0, 0, 250, 250))
        g.AddNode(GraphNode("B", 200, 0, 250, 250))

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

    def test0_4OverlapRemoverCreation(self):
        g = self.g
        a = GraphNode("A", 0, 0, 250, 250)
        a1 = GraphNode("A1", 0, 0)
        a2 = GraphNode("A2", 0, 0)
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
        for i in range(0, len(nodes) - 1):
            if not nodes[i].right < nodes[i + 1].left:
                return False
        return True

    def _ensureXorderLefts(self, *args):
        nodes = [self.g.FindNodeById(id) for id in args]
        assert len(nodes) >= 2
        for i in range(0, len(nodes) - 1):
            if not nodes[i].left < nodes[i + 1].left:
                return False
        return True

    def _ensureYorder(self, *args):
        nodes = [self.g.FindNodeById(id) for id in args]
        assert len(nodes) >= 2
        for i in range(0, len(nodes) - 1):
            if not nodes[i].bottom < nodes[i + 1].top:
                return False
        return True

    def _ensureYorderBottoms(self, *args):
        nodes = [self.g.FindNodeById(id) for id in args]
        assert len(nodes) >= 2
        for i in range(0, len(nodes) - 1):
            if not nodes[i].bottom < nodes[i + 1].bottom:
                return False
        return True

    def _LoadScenario1(self):
        self.g.LoadGraphFromStrings(TEST_GRAPH1)

    def test1_1MoveLeftPushedBackHorizontally01(self):
        self._LoadScenario1()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (150, 9)

        # assert m1 has been pushed back to the right
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])
        self.assertTrue(node.left > self.g.FindNodeById("D25").right)
        self.assertTrue(node.top < self.g.FindNodeById("D25").bottom)

    def test1_2MoveLeftPushedBackDownRight02(self):
        self._LoadScenario1()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (106, 79)

        # assert m1 has been pushed back to the right but also down
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(node.left > self.g.FindNodeById("D13").right)
        self.assertTrue(node.top > self.g.FindNodeById("D25").bottom)

    def test1_3MoveInsertedVertically1(self):
        self._LoadScenario1()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (16, 74)

        # assert m1 has been squeezed in between the two existing
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()["total_overlaps_found"])

        # print self.g.GraphToString()
        self.assertTrue(node.top > self.g.FindNodeById("D25").bottom)
        self.assertTrue(node.bottom < self.g.FindNodeById("D13").top)
        self.assertTrue(self.g.FindNodeById("D13").top > self.g.FindNodeById("D25").bottom)
        self.assertTrue(node.left < self.g.FindNodeById("D25").right)
        self.assertTrue(node.left < self.g.FindNodeById("D13").right)

    def test1_4MovePushedVertically2(self):
        self._LoadScenario1()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (6, 154)

        # assert m1 has been pushed vertically underneath the other two nodes
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureYorder("D25", "D13", "m1"))

        self.assertTrue(node.left < self.g.FindNodeById("D25").right)
        self.assertTrue(node.left < self.g.FindNodeById("D13").right)

    def _LoadScenario2(self):
        self.g.LoadGraphFromStrings(TEST_GRAPH2)

    def test2_1InsertAndPushedRightHorizontally(self):
        self._LoadScenario2()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (121, 14)

        # assert m1 has been inserted and node to the right pushed right
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D25", "m1", "D97"))
        self.assertTrue(self._ensureYorderBottoms("m1", "D97"))  # m1 bottom above D97 bottom

    def test2_2PushedRightAndDownNicely(self):
        self._LoadScenario2()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (96, 114)

        # assert m1 has been pushed down and right nicely and snugly
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D13", "m1"))
        self.assertTrue(self._ensureXorderLefts("D13", "m1", "D97"))
        self.assertTrue(self._ensureXorderLefts("D25", "m1", "D97"))
        self.assertTrue(self._ensureYorderBottoms("D25", "D97", "m1"))
        self.assertTrue(self._ensureYorder("D25", "m1"))
        self.assertTrue(self._ensureYorderBottoms("D25", "D13", "m1"))
        self.assertTrue(self._ensureYorderBottoms("D25", "D97", "m1"))

    def _LoadScenario3(self):
        self.g.LoadGraphFromStrings(TEST_GRAPH3)

    def test3_1PushedBetweenLeftAndRight(self):
        self._LoadScenario3()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (266, 9)

        # assert m1 has been pushed between two nodes, horizontally.  Both left and right nodes moved left and right respectively.
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()["total_overlaps_found"])

        GatherSnugProposals_ON = True  # see method ProposeRemovalsAndApply() in overlap_removal.py

        if GatherSnugProposals_ON:
            # Newer snug behaviour
            self.assertTrue(self._ensureXorder("D25", "D97", "D98"))
            self.assertTrue(self._ensureYorder("D98", "m1"))
            self.assertTrue(self._ensureYorder("D97", "m1"))
            self.assertTrue(self._ensureYorder("D25", "m1"))
        else:
            # Older squeeze behaviour
            self.assertTrue(self._ensureXorder("D25", "D97", "m1", "D98"))
            self.assertTrue(self._ensureYorder("D25", "D13"))
            self.assertTrue(self._ensureYorderBottoms("D25", "D97", "D13"))

    def test3_2PushedBetweenLeftAndRightRefused(self):
        self._LoadScenario3()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (226, 14)

        # assert m1 has been not been inserted - refused and snuggled instead
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D25", "D97", "D98"))
        self.assertTrue(self._ensureXorder("D25", "D97", "m1"))
        self.assertTrue(self._ensureYorder("D98", "m1"))
        self.assertTrue(self._ensureYorderBottoms("D98", "D97", "m1"))

    def test3_2aPushedRefusedButLeftMovedAnyway(self):
        self._LoadScenario3()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (281, 64)

        d97 = self.g.FindNodeById("D97")
        oldD97pos = (d97.left, d97.top)

        # assert m1 has been refused insertion, but left (D97) moved leftwards cos there is room.  m1 snuggled below and to the right.
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D25", "D97", "D98"))
        self.assertTrue(self._ensureXorder("D13", "D97", "m1"))
        self.assertTrue(self._ensureYorder("D25", "D13"))
        self.assertTrue(self._ensureYorder("D98", "m1"))
        self.assertTrue(self._ensureYorderBottoms("D98", "D97", "m1"))
        self.assertNotEqual(oldD97pos, (d97.left, d97.top))  # ensure D97 HAS been pushed left

    def test3_3InsertedAndTwoPushedRight(self):
        self._LoadScenario3()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (146, 9)

        # assert m1 has been inserted - and two nodes pushed right
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(3, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D25", "m1", "D97", "D98"))

    def test3_4InsertedVerticallyNothingPushedRight(self):
        self._LoadScenario3()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (91, 64)

        d97 = self.g.FindNodeById("D97")
        oldD97pos = (d97.left, d97.top)

        # assert m1 has been inserted vertically - one node pushed down, NO nodes pushed right
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(5, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D25", "D97", "D98"))
        self.assertTrue(self._ensureXorder("m1", "D97", "D98"))
        self.assertTrue(self._ensureYorder("D25", "m1", "D13"))
        self.assertTrue(self._ensureYorder("D25", "m1", "D13"))
        self.assertEqual(oldD97pos, (d97.left, d97.top))  # ensure D97 hasn't been pushed

    def test3_5InsertedVerticallyTwoPushedDown(self):
        self._LoadScenario3()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (6, 4)

        d97 = self.g.FindNodeById("D97")
        oldD97pos = (d97.left, d97.top)

        # assert m1 has been inserted vertically - two pushed down
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(2, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureYorder("m1", "D25", "D13"))
        self.assertTrue(self._ensureXorder("m1", "D97", "D98"))
        self.assertTrue(self._ensureXorder("D25", "D97", "D98"))
        self.assertTrue(self._ensureXorder("D13", "D97", "D98"))
        self.assertEqual(oldD97pos, (d97.left, d97.top))  # ensure D97 hasn't been pushed

    def _LoadScenario3a(self):
        self.g.LoadGraphFromStrings(TEST_GRAPH3A)

    def test3A_1PushedLeft(self):
        self._LoadScenario3a()

        node = self.g.FindNodeById("m1")
        node.left, node.top = (246, 9)

        # move m1 to the right, should be pushed back to the left
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D25", "m1", "D97"))
        self.assertTrue(self._ensureXorder("D13", "m1", "D97"))
        self.assertTrue(self._ensureYorder("D25", "D13"))
        self.assertTrue(self._ensureYorder("m1", "D13"))
        self.assertTrue(self._ensureYorder("m1", "D98"))
        self.assertTrue(self._ensureYorder("D97", "D98"))

        self.assertFalse(self._ensureYorder("D25", "m1"))  # don't want this
        self.assertFalse(self._ensureYorder("D97", "m1"))  # don't want this

    def test3A_2PushedLeftD97DoesntMove(self):
        self._LoadScenario3a()

        d97 = self.g.FindNodeById("D97")
        oldD97pos = (d97.left, d97.top)

        node = self.g.FindNodeById("m1")
        node.left, node.top = (261, 104)

        # move m1 to the right, should be pushed back to the left.  D97 shouldn't move!
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)

        self.assertTrue(self._ensureXorder("D25", "m1", "D97"))
        self.assertTrue(self._ensureXorder("D25", "m1", "D98"))
        self.assertTrue(self._ensureXorderLefts("D25", "m1", "D98", "D97"))

        self.assertEqual(oldD97pos, (d97.left, d97.top))  # ensure D97 hasn't been pushed

    def test3A_3PushedLeftNotFlyingUpY(self):
        self._LoadScenario3a()

        node = self.g.FindNodeById("m1")
        node.left, node.top = (216, 164)

        # move m1 to the right, should be pushed back to the left.  Not flown up Y.
        # note that the top of m1 is > top of D98 to trigger this test.
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D25", "m1", "D97"))
        self.assertTrue(self._ensureXorder("D25", "m1", "D98"))
        self.assertTrue(self._ensureYorder("D25", "m1"))
        self.assertFalse(self._ensureYorder("m1", "D98"))  # don't want this

    def _LoadScenario4(self):
        self.g.LoadGraphFromStrings(TEST_GRAPH4)

    def test4_1InsertedTwoPushedRightTwoPushedDown(self):
        self._LoadScenario4()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (136, 99)

        d97 = self.g.FindNodeById("D97")
        d98 = self.g.FindNodeById("D98")
        d50 = self.g.FindNodeById("D50")
        d51 = self.g.FindNodeById("D51")
        oldD97pos = (d97.left, d97.top)
        oldD98pos = (d98.left, d98.top)
        oldD50pos = (d50.left, d50.top)
        oldD51pos = (d51.left, d51.top)

        # assert m1 has been inserted - two pushed right, two pushed down
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(5, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("D13", "m1", "D97", "D98"))
        self.assertTrue(self._ensureXorder("D25", "D97", "D98"))
        self.assertTrue(self._ensureYorder("D25", "D13", "D50", "D51"))
        self.assertTrue(self._ensureYorder("D25", "m1", "D50", "D51"))
        self.assertTrue(self._ensureYorder("D97", "D50", "D51"))
        self.assertTrue(self._ensureYorder("D98", "D50", "D51"))
        self.assertTrue(self._ensureXorder("D13", "D50"))
        self.assertTrue(self._ensureXorder("D13", "D51"))
        self.assertNotEqual(oldD97pos, (d97.left, d97.top))  # ensure D97 HAS been pushed
        self.assertNotEqual(oldD98pos, (d98.left, d98.top))  # ensure D98 HAS been pushed
        self.assertNotEqual(oldD50pos, (d50.left, d50.top))  # ensure D50 HAS been pushed
        self.assertNotEqual(oldD51pos, (d51.left, d51.top))  # ensure D51 HAS been pushed

    def test4_2InsertedTwoNotPushedRightThreePushedDown(self):
        self._LoadScenario4()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (101, 99)

        d97 = self.g.FindNodeById("D97")
        d98 = self.g.FindNodeById("D98")
        d50 = self.g.FindNodeById("D50")
        d51 = self.g.FindNodeById("D51")
        d13 = self.g.FindNodeById("D13")
        oldD97pos = (d97.left, d97.top)
        oldD98pos = (d98.left, d98.top)
        oldD50pos = (d50.left, d50.top)
        oldD51pos = (d51.left, d51.top)
        oldD13pos = (d13.left, d13.top)

        # assert m1 has been inserted - two NOT pushed right, two pushed down, and extra D13 pushed down
        # because m1 overlaps/attacks D13 (and there is room for D13 to move downwards I guess)
        #
        # An earlier version of this test allowed D97 and D98 to be pushed to the right.  I changed this.
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)

        self.assertFalse(
            self._ensureXorder("D13", "m1", "D97", "D98")
        )  # not true anymore, m1 not pushed to the right so much
        self.assertFalse(self._ensureYorder("D25", "D13", "D50", "D51"))  # not true anymore,

        self.assertTrue(self._ensureXorder("D25", "D97", "D98"))
        self.assertTrue(self._ensureXorder("D13", "D97", "D98"))
        self.assertTrue(self._ensureXorder("D13", "D50"))
        self.assertTrue(self._ensureXorder("D13", "D51"))

        self.assertTrue(self._ensureYorder("D25", "m1", "D13", "D51"))
        self.assertTrue(self._ensureYorder("D25", "m1", "D50", "D51"))
        self.assertTrue(self._ensureYorder("D97", "D50", "D51"))
        self.assertTrue(self._ensureYorder("D98", "D50", "D51"))
        self.assertTrue(self._ensureYorderBottoms("D25", "D97", "m1", "D13", "D50", "D51"))

        self.assertEqual(oldD97pos, (d97.left, d97.top))  # ensure D97 HAS NOT been pushed
        self.assertEqual(oldD98pos, (d98.left, d98.top))  # ensure D98 HAS NOT been pushed
        self.assertNotEqual(oldD50pos, (d50.left, d50.top))  # ensure D50 HAS been pushed
        self.assertNotEqual(oldD51pos, (d51.left, d51.top))  # ensure D51 HAS been pushed
        self.assertNotEqual(oldD13pos, (d13.left, d13.top))  # ensure D13 HAS been pushed

    def _LoadScenario6_linecrossing(self):
        self.g.LoadGraphFromStrings(TEST_GRAPH6)

    @unittest.skipIf(
        not LINE_NODE_OVERLAP_REMOVAL_ENABLED,
        "line node overlap removal - abandoned this difficult idea",
    )
    def test6_1LineCrossingNotNeeded(self):

        self._LoadScenario6_linecrossing()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (49, 48)

        # assert m1 has been repulsed and snuggeled
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("A", "B"))
        self.assertTrue(self._ensureXorder("A", "m1"))
        self.assertTrue(self._ensureYorder("A", "C"))
        self.assertTrue(self._ensureYorder("B", "m1", "C"))
        self.assertFalse(
            self._ensureYorder("A", "m1", "C")
        )  # don't want this otherwise the line from A to C would be crossed

    @unittest.skipIf(
        not LINE_NODE_OVERLAP_REMOVAL_ENABLED,
        "line node overlap removal - abandoned this difficult idea",
    )
    def test6_2LineCrossingAvoided(self):

        self._LoadScenario6_linecrossing()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        # node.left, node.top = (9, 103) # A is to the left of A
        node.left, node.top = (24, 98)  # m1 is to the left of A - a bit easier to solve

        # assert m1 has been repulsed and snuggled, and line not crossed - same results as ABOVE
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("A", "m1"))

        # ensure m1 not crossing any lines
        line_start_point = self.g.FindNodeById("A").centre_point
        line_end_point = self.g.FindNodeById("C").centre_point
        crossings = node.CalcLineIntersectionPoints(line_start_point, line_end_point)
        self.assertEqual(0, len(crossings))

    @unittest.skipIf(
        not LINE_NODE_OVERLAP_REMOVAL_ENABLED,
        "line node overlap removal - abandoned this difficult idea",
    )
    def test6_3LineCrossingAvoidedGoSnug(self):

        self._LoadScenario6_linecrossing()

        # move m1 to down and left, crossing the line
        node = self.g.FindNodeById("m1")
        node.left, node.top = (79, 163)

        # assert m1 has been repulsed up and to the right, snuggled, and line not crossed
        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("A", "B"))
        self.assertTrue(self._ensureXorder("A", "m1"))
        self.assertFalse(self._ensureXorder("C", "m1"))  # don't want this
        self.assertTrue(self._ensureYorder("m1", "C"))
        self.assertTrue(self._ensureYorder("A", "C"))

    def _LoadScenario7(self):
        self.g.LoadGraphFromStrings(TEST_GRAPH7)

    def test7_1DontJumpTooFarY(self):

        self._LoadScenario7()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (240, 15)

        # assert m1 has been pushed to the right.  don't see why edges should make any difference
        # initially found m1 was being pushed way too far down in the Y direction!

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("A", "m1"))
        self.assertTrue(self._ensureXorder("A", "c"))
        self.assertTrue(self._ensureYorder("m1", "c"))

        self.assertFalse(self._ensureYorder("A", "m1"))  # don't want this huge Y jump

    def test7_2DontJumpTooFarY(self):

        self._LoadScenario7()

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (235, 120)

        # assert m1 has been pushed to the right and down snugly
        # not pushed way too far down in the Y direction!

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)
        self.assertEqual(1, self.overlap_remover.GetStats()["total_overlaps_found"])

        self.assertTrue(self._ensureXorder("A", "m1"))
        self.assertTrue(self._ensureXorder("A", "c"))
        self.assertTrue(self._ensureYorder("c", "m1"))  # ensure m1 is snuggled below c

        self.assertFalse(self._ensureYorder("A", "m1"))  # don't want this huge Y jump

    def _LoadScenario8(self):
        self.g.LoadGraphFromStrings(TEST_GRAPH8)

    def test8_1JumpUpAndSnuggleB1PushedOk(self):

        self._LoadScenario8()

        b1 = self.g.FindNodeById("B1")
        a = self.g.FindNodeById("A")
        oldB1pos = (b1.left, b1.top)
        oldApos = (a.left, a.top)

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (64, 75)

        # assert m1 has been pushed up and to the right. Ok for B1 to be pushed a little left

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)

        self.assertTrue(self._ensureXorder("B1", "m1", "B2"))
        self.assertTrue(self._ensureYorder("B1", "A"))
        self.assertTrue(self._ensureYorder("B2", "A"))

        self.assertEqual(oldApos, (a.left, a.top))  # ensure A HAS NOT been pushed
        self.assertNotEqual(oldB1pos, (b1.left, b1.top))  # ok if B1 HAS been pushed

    def test8_2JumpUpAndSnuggle(self):

        self._LoadScenario8()

        b1 = self.g.FindNodeById("B1")
        a = self.g.FindNodeById("A")
        oldB1pos = (b1.left, b1.top)
        oldApos = (a.left, a.top)

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (34, 75)

        # assert m1 has been pushed up and to the right. We used to have it so
        # moving y up was not an option for m1 so A got pushed down instead.

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)

        self.assertTrue(self._ensureXorder("B1", "m1", "B2"))
        self.assertTrue(self._ensureYorder("B1", "A"))
        self.assertTrue(self._ensureYorder("B2", "A"))

        self.assertEqual(oldApos, (a.left, a.top))  # ensure A HAS NOT been pushed
        self.assertEqual(oldB1pos, (b1.left, b1.top))  # ensure B1 HAS NOT been pushed

    def test8_3JumpUpAndSnuggle(self):

        self._LoadScenario8()

        b2 = self.g.FindNodeById("B2")
        a = self.g.FindNodeById("A")
        oldB2pos = (b2.left, b2.top)
        oldApos = (a.left, a.top)

        # move m1 to the left
        node = self.g.FindNodeById("m1")
        node.left, node.top = (114, 75)

        # assert m1 has been pushed up and to the left. We used to have it so
        # moving y up was not an option for m1 so A got pushed down instead.

        were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
        self.assertTrue(were_all_overlaps_removed)

        self.assertTrue(self._ensureXorder("B1", "m1", "B2"))
        self.assertTrue(self._ensureYorder("B1", "A"))
        self.assertTrue(self._ensureYorder("B2", "A"))

        self.assertEqual(oldApos, (a.left, a.top))  # ensure A HAS NOT been pushed
        self.assertEqual(oldB2pos, (b2.left, b2.top))  # ensure B2 HAS NOT been pushed


# Suite only needed for my alltests.py test running master
def suite():
    suite1 = unittest.makeSuite(OverlapTests, "test")
    alltests = unittest.TestSuite((suite1,))
    return alltests


if __name__ == "__main__":
    unittest.main()
