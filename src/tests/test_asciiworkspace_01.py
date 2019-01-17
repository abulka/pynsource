import unittest
import os

import sys

sys.path.append("../src")
from ascii_uml.asciiworkspace import AsciiWorkspace

OUT_FILE = "ascii_out.txt"


class TestCaseAscii_01(unittest.TestCase):
    def setUp(self):
        w = AsciiWorkspace()

        w.AddColumn(
            """
+------------+
|   Editor   |
|------------|
| topHandler |  ---->  [ TopHandler ]
| GUI        |  ---->  [ Statechart ]
| statechart |  ---->  [ GUI ]
|------------|
| __init__   |
| start      |
+------------+
"""
        )

        w.AddColumn(
            """
+------------+
| TopHandler |
+------------+
"""
        )

        w.AddColumn(
            """
+-----+
| GUI |
+-----+
"""
        )

        w.AddColumn(
            """
+------------+
| Statechart |
+------------+
"""
        )

        w.AddColumn(
            """
           [ ogl ]           
              .              
             /_\             
              |              
              |              
+-----------------------------+
|        UmlShapeCanvas       |
|-----------------------------|
| scrollStepX                 |  ---->  [ Laymanwoman ]
| scrollStepY                 |  ---->  [ OverlapRemoval ]
| evenfreddycansee            |  ---->  [ CoordinateMapper ]
| log                         |  ---->  [ GraphLayoutSpring ]
| frame                       |  ---->  [ UmlWorkspace ]
| save_gdi                    |
| working                     |
| font1                       |
| font2                       |
| umlworkspace                |
| layout                      |
| coordmapper                 |
| layouter                    |
| overlap_remover             |
|-----------------------------|
| __init__                    |
| AllToLayoutCoords           |
| AllToWorldCoords            |
| onKeyPress                  |
| CmdInsertNewNode            |
| CmdZapShape                 |
| Clear                       |
| ConvertParseModelToUmlModel |
| BuildEdgeModel              |
| Go                          |
| CreateUmlShape              |
| newRegion                   |
| CreateUmlEdge               |
| OnWheelZoom                 |
| ChangeScale                 |
| stage1                      |
| stage2                      |
| stateofthenation            |
| stateofthespring            |
| RedrawEverything            |
| ReLayout                    |
| LayoutAndPositionShapes     |
| setSize                     |
| DecorateShape               |
| createNodeShape             |
| AdjustShapePosition         |
| Redraw222                   |
| get_umlboxshapes            |
| OnDestroy                   |
| OnLeftClick                 |
| DeselectAllShapes           |
+-----------------------------+
"""
        )

        w.AddColumn(
            """
+-----------+
|    Log    |
|-----------|
| WriteText |
+-----------+
"""
        )

        w.AddColumn(
            """
            [ wx ]            
              .               
             /_\              
              |               
              |               
+------------------------------+
|           MainApp            |
|------------------------------|
| log                          |  ---->  [ ImageViewer ]
| andyapptitle                 |  ---->  [ Log ]
| frame                        |  ---->  [ UmlShapeCanvas ]
| notebook                     |  ---->  [ Frame ]
| umlcanvas                       |
| yuml                         |
| asciiart                     |
| multiText                    |
| popupmenu                    |
| next_menu_id                 |
| printData                    |
| box                          |
| canvas                       |
| preview                      |
|------------------------------|
| OnInit                       |
| OnResizeFrame                |
| OnRightButtonMenu            |
| OnBuildGraphFromUmlWorkspace |
| OnSaveGraphToConsole         |
| OnSaveGraph                  |
| OnLoadGraphFromText          |
| OnLoadGraph                  |
| LoadGraph                    |
| OnTabPageChanged             |
| InitMenus                    |
| Add                          |
| FileImport                   |
| FileImport2                  |
| FileImport3                  |
| FileNew                      |
| FilePrint                    |
| OnAbout                      |
| OnVisitWebsite               |
| OnCheckForUpdates            |
| OnHelp                       |
| OnDeleteNode                 |
| OnLayout                     |
| OnRefreshUmlWindow           |
| MessageBox                   |
| OnButton                     |
| OnCloseFrame                 |
+------------------------------+
"""
        )

        w.AddColumn(
            """
       [ ogl ]        
          .           
         /_\          
          |           
          |           
+----------------------+
|     MyEvtHandler     |
|----------------------|
| log                  |
| frame                |
| shapecanvas          |
| popupmenu            |
|----------------------|
| __init__             |
| UpdateStatusBar      |
| OnLeftClick          |
| _SelectNodeNow       |
| OnEndDragLeft        |
| OnSizingEndDragLeft  |
| OnMovePost           |
| OnPopupItemSelected  |
| OnRightClick         |
| RightClickDeleteNode |
+----------------------+
"""
        )

        w.AddColumn(
            """
+-----+
| ogl |
+-----+
"""
        )

        w.AddColumn(
            """
+----+
| wx |
+----+
"""
        )

        w.AddColumn(
            """
+--------------+
| UmlWorkspace |
+--------------+
"""
        )

        w.AddColumn(
            """
+-------------+
| Laymanwoman |
+-------------+
"""
        )

        w.AddColumn(
            """
+------------------+
| CoordinateMapper |
+------------------+
"""
        )

        w.AddColumn(
            """
+-------------------+
| GraphLayoutSpring |
+-------------------+
"""
        )

        w.AddColumn(
            """
+----------------+
| OverlapRemoval |
+----------------+
"""
        )

        w.AddColumn(
            """
+-------+
| Frame |
+-------+
"""
        )

        w.AddColumn(
            """
+-------------+
| ImageViewer |
+-------------+
"""
        )

        w.Flush()
        fp = open(OUT_FILE, "w")
        fp.write(w.contents)
        fp.close()

    def tearDown(self):
        os.remove(OUT_FILE)

    def test_ascii_layout_01(self):
        fp = open(OUT_FILE, "r")
        lines = fp.readlines()
        fp.close()

        self.assertEqual(
            "                                                                                                                                                                                                                                                                                                                                                                                                                    \n",
            lines[0],
        )
        self.assertEqual(
            "+------------+                          +------------+   +-----+   +------------+              [ ogl ]                                              +-----------+               [ wx ]                                                   [ ogl ]             +-----+   +----+   +--------------+   +-------------+   +------------------+   +-------------------+   +----------------+   +-------+   +-------------+\n",
            lines[1],
        )
        self.assertEqual(
            "| statechart |  ---->  [ GUI ]                                                      +-----------------------------+                                                 +------------------------------+                              +----------------------+                                                                                                                                                          \n",
            lines[6],
        )


def suite():
    suite1 = unittest.makeSuite(TestCaseAscii_01, "test")
    alltests = unittest.TestSuite((suite1,))
    return alltests


def main():
    runner = unittest.TextTestRunner(
        descriptions=0, verbosity=2
    )  # default is descriptions=1, verbosity=1
    runner.run(suite())


if __name__ == "__main__":
    main()
