# RhsAnalyser tests

import sys

sys.path.append("../src")
from common.architecture_support import whosdaddy, whosgranddaddy
from view.graph import Graph, GraphNode
import view.graph_persistence

import unittest

"""
 TESTS
"""


class TestCase_A(unittest.TestCase):
    """
    Test upgrading from previous persistence format versions.
    """

    def test_1(self):
        """
        Upgrade 0.9 (no version number) to 1.0
        """
        g = Graph()

        filedata = """
{'type':'node', 'id':'c', 'x':230, 'y':174, 'width':60, 'height':120}
{'type':'node', 'id':'c1', 'x':130, 'y':174, 'width':60, 'height':120}
{'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1'}
    """
        # g.Clear()
        assert len(g.nodes) == 0
        # assert g.GraphToString().strip() == ""

        view.graph_persistence.PERSISTENCE_CURRENT_VERSION = 1.0
        # g.LoadGraphFromStrings(filedata)
        self.assertTrue(g.persistence.UpgradeToLatestFileFormatVersion(filedata))
        # print g.persistence.filedata_list

        assert (
            g.persistence.filedata_list[0] == "# PynSource Version 1.0"
        ), g.persistence.filedata_list[0]
        assert g.persistence.ori_file_version == 0.9

    def test_2(self):
        """
        Upgrade 0.9 (no version number) to 1.1
        """
        g = Graph()
        filedata = """
{'type':'node', 'id':'c', 'x':230, 'y':174, 'width':60, 'height':120}
{'type':'node', 'id':'c1', 'x':130, 'y':174, 'width':60, 'height':120}
{'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1'}
    """
        view.graph_persistence.PERSISTENCE_CURRENT_VERSION = 1.1
        self.assertTrue(g.persistence.UpgradeToLatestFileFormatVersion(filedata))
        # print g.persistence.filedata_list

        assert (
            g.persistence.filedata_list[0] == "# PynSource Version 1.1"
        ), g.persistence.filedata_list[0]
        assert "meta" in g.persistence.filedata_list[1], g.persistence.filedata_list[1]
        assert g.persistence.ori_file_version == 0.9

        # now check type node has been converted to type umlshape
        data = eval(g.persistence.filedata_list[2])
        self.assertEqual("umlshape", data.get("type"))

    def test_3(self):
        """
        Upgrade 1.0 to 1.1
        """
        g = Graph()
        filedata = """
# PynSource Version 1.0
{'type':'node', 'id':'UmlShapeCanvas', 'x':237, 'y':65, 'width':226, 'height':781, 'attrs':'scrollStepX|scrollStepY|evenfreddycansee|log|frame|save_gdi|working|font1|font2|umlworkspace|layout|coordmapper|layouter|overlap_remover', 'meths':'__init__|AllToLayoutCoords|AllToWorldCoords|onKeyPress|CmdInsertNewNode|CmdZapShape|Clear|ConvertParseModelToUmlModel|BuildEdgeModel|Go|CreateUmlShape|newRegion|CreateUmlEdge|OnWheelZoom|ChangeScale|stage1|stage2|stateofthenation|stateofthespring|RedrawEverything|ReLayout|LayoutAndPositionShapes|setSize|DecorateShape|createNodeShape|AdjustShapePosition|Redraw222|get_umlboxshapes|OnDestroy|OnLeftClick|DeselectAllShapes'}
{'type':'node', 'id':'Log', 'x':1089, 'y':222, 'width':82, 'height':67, 'attrs':'', 'meths':'WriteText'}
{'type':'node', 'id':'MainApp', 'x':788, 'y':217, 'width':234, 'height':717, 'attrs':'log|andyapptitle|frame|notebook|umlcanvas|yuml|asciiart|multiText|popupmenu|next_menu_id|printData|box|canvas|preview', 'meths':'OnInit|OnResizeFrame|OnRightButtonMenu|OnBuildGraphFromUmlWorkspace|OnSaveGraphToConsole|OnSaveGraph|OnLoadGraphFromText|OnLoadGraph|LoadGraph|OnTabPageChanged|InitMenus|Add|FileImport|FileImport2|FileImport3|FileNew|FilePrint|OnAbout|OnVisitWebsite|OnCheckForUpdates|OnHelp|OnDeleteNode|OnLayout|OnRefreshUmlWindow|MessageBox|OnButton|OnCloseFrame'}
{'type':'node', 'id':'MyEvtHandler', 'x':10, 'y':173, 'width':170, 'height':285, 'attrs':'log|frame|shapecanvas|popupmenu', 'meths':'__init__|UpdateStatusBar|OnLeftClick|_SelectNodeNow|OnEndDragLeft|OnSizingEndDragLeft|OnMovePost|OnPopupItemSelected|OnRightClick|RightClickDeleteNode'}
{'type':'edge', 'id':'UmlShapeCanvas_to_MainApp', 'source':'UmlShapeCanvas', 'target':'MainApp', 'uml_edge_type':'composition'}
{'type':'edge', 'id':'ImageViewer_to_MainApp', 'source':'ImageViewer', 'target':'MainApp', 'uml_edge_type':'composition'}
{'type':'edge', 'id':'UmlShapeCanvas_to_MainApp', 'source':'UmlShapeCanvas', 'target':'MainApp', 'uml_edge_type':'composition'}
    """
        view.graph_persistence.PERSISTENCE_CURRENT_VERSION = 1.1
        self.assertTrue(g.persistence.UpgradeToLatestFileFormatVersion(filedata))
        # print g.persistence.filedata_list

        assert (
            g.persistence.filedata_list[0] == "# PynSource Version 1.1"
        ), g.persistence.filedata_list[0]
        assert "meta" in g.persistence.filedata_list[1], g.persistence.filedata_list[1]
        assert g.persistence.ori_file_version == 1.0

        # now check type node has been converted to type umlshape
        data = eval(g.persistence.filedata_list[2])
        self.assertEqual("umlshape", data.get("type"))

    def test_4(self):
        """
        Upgrade 1.1 to 1.1
        """
        g = Graph()
        filedata = """
# PynSource Version 1.1
{'type':'meta', 'info1':'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'}
{'type':'umlshape', 'id':'UmlShapeCanvas', 'x':237, 'y':65, 'width':226, 'height':781, 'attrs':'scrollStepX|scrollStepY|evenfreddycansee|log|frame|save_gdi|working|font1|font2|umlworkspace|layout|coordmapper|layouter|overlap_remover', 'meths':'__init__|AllToLayoutCoords|AllToWorldCoords|onKeyPress|CmdInsertNewumlshape|CmdZapShape|Clear|ConvertParseModelToUmlModel|BuildEdgeModel|Go|CreateUmlShape|newRegion|CreateUmlEdge|OnWheelZoom|ChangeScale|stage1|stage2|stateofthenation|stateofthespring|RedrawEverything|ReLayout|LayoutAndPositionShapes|setSize|DecorateShape|createumlshapeShape|AdjustShapePosition|Redraw222|get_umlboxshapes|OnDestroy|OnLeftClick|DeselectAllShapes'}
{'type':'umlshape', 'id':'Log', 'x':1089, 'y':222, 'width':82, 'height':67, 'attrs':'', 'meths':'WriteText'}
{'type':'edge', 'id':'UmlShapeCanvas_to_MainApp', 'source':'UmlShapeCanvas', 'target':'MainApp', 'uml_edge_type':'composition'}
    """
        view.graph_persistence.PERSISTENCE_CURRENT_VERSION = 1.1
        self.assertTrue(g.persistence.UpgradeToLatestFileFormatVersion(filedata))
        # print g.persistence.filedata_list

        assert (
            g.persistence.filedata_list[0] == "# PynSource Version 1.1"
        ), g.persistence.filedata_list[0]
        assert "meta" in g.persistence.filedata_list[1], g.persistence.filedata_list[1]
        assert g.persistence.ori_file_version == 1.1

        # now check type node has been converted to type umlshape
        data = eval(g.persistence.filedata_list[2])
        self.assertEqual("umlshape", data.get("type"))

    def test_5(self):
        """
        Upgrade 1.1 to 1.0 - simulate loading a newer file format into an older version of the app
        Cannot read. (a bit strict, I know - but gui allows for forcing the read - see filemgmt.py)
        """
        g = Graph()
        filedata = """
# PynSource Version 1.1
{'type':'meta', 'info1':'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'}
{'type':'umlshape', 'id':'UmlShapeCanvas', 'x':237, 'y':65, 'width':226, 'height':781, 'attrs':'scrollStepX|scrollStepY|evenfreddycansee|log|frame|save_gdi|working|font1|font2|umlworkspace|layout|coordmapper|layouter|overlap_remover', 'meths':'__init__|AllToLayoutCoords|AllToWorldCoords|onKeyPress|CmdInsertNewumlshape|CmdZapShape|Clear|ConvertParseModelToUmlModel|BuildEdgeModel|Go|CreateUmlShape|newRegion|CreateUmlEdge|OnWheelZoom|ChangeScale|stage1|stage2|stateofthenation|stateofthespring|RedrawEverything|ReLayout|LayoutAndPositionShapes|setSize|DecorateShape|createumlshapeShape|AdjustShapePosition|Redraw222|get_umlboxshapes|OnDestroy|OnLeftClick|DeselectAllShapes'}
{'type':'umlshape', 'id':'Log', 'x':1089, 'y':222, 'width':82, 'height':67, 'attrs':'', 'meths':'WriteText'}
{'type':'edge', 'id':'UmlShapeCanvas_to_MainApp', 'source':'UmlShapeCanvas', 'target':'MainApp', 'uml_edge_type':'composition'}
    """
        view.graph_persistence.PERSISTENCE_CURRENT_VERSION = 1.0
        self.assertFalse(g.persistence.UpgradeToLatestFileFormatVersion(filedata))
        self.assertFalse(g.persistence.can_I_read(filedata)[0])

    def test_6(self):
        """
        Empty file
        """
        g = Graph()
        filedata = """
    """
        view.graph_persistence.PERSISTENCE_CURRENT_VERSION = 1.1
        self.assertFalse(g.persistence.can_I_read(filedata)[0])
        self.assertFalse(g.persistence.UpgradeToLatestFileFormatVersion(filedata))


def suite():
    suite1 = unittest.makeSuite(TestCase_A, "test")
    alltests = unittest.TestSuite((suite1,))
    return alltests


def main():
    runner = unittest.TextTestRunner(
        descriptions=0, verbosity=2
    )  # default is descriptions=1, verbosity=1
    runner.run(suite())


if __name__ == "__main__":
    main()
