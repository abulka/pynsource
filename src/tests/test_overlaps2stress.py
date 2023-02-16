import unittest

import sys

sys.path.append("../src")
from layout.overlap_removal import OverlapRemoval
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
        pass

    def testStress1(self):

        for i in range(10):
            self.g.LoadGraphFromStrings(TEST_GRAPH5_STRESS)
            print(i, end=" ")
            were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
            self.assertTrue(were_all_overlaps_removed)

            self.g.Clear()

    def testStress2_InitialBoot(self):
        """
        This is the slowest stress test because it runs the spring layout several times.
        """

        from layout.layout_spring import GraphLayoutSpring
        from layout.coordinate_mapper import CoordinateMapper

        self.g.LoadGraphFromStrings(GRAPH_INITIALBOOT)  # load the scenario ourselves

        layouter = GraphLayoutSpring(self.g)
        coordmapper = CoordinateMapper(self.g, (800, 800))

        def AllToLayoutCoords():
            coordmapper.AllToLayoutCoords()

        def AllToWorldCoords():
            coordmapper.AllToWorldCoords()

        for i in range(8):
            print(i, end=" ")

            AllToLayoutCoords()
            layouter.layout(keep_current_positions=False)
            AllToWorldCoords()

            were_all_overlaps_removed = self.overlap_remover.RemoveOverlaps()
            self.assertTrue(were_all_overlaps_removed)


# Suite only needed for my alltests.py test running master
def suite():
    suite1 = unittest.makeSuite(OverlapTests, "test")
    alltests = unittest.TestSuite((suite1,))
    return alltests


if __name__ == "__main__":
    unittest.main()
