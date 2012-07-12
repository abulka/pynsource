from asciiworkspace import AsciiWorkspace
w = AsciiWorkspace()

w.AddColumn("""
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
""")

w.AddColumn("""
+------------+
| TopHandler |
+------------+
""")

w.AddColumn("""
+-----+
| GUI |
+-----+
""")

w.AddColumn("""
+------------+
| Statechart |
+------------+
""")

w.AddColumn("""
           [ ogl ]           
              .              
             /_\             
              |              
              |              
+-----------------------------+
|        UmlShapeCanvas       |
|-----------------------------|
| scrollStepX                 |  ---->  [ LayoutBasic ]
| scrollStepY                 |  ---->  [ OverlapRemoval ]
| classnametoshape            |  ---->  [ CoordinateMapper ]
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
""")

w.AddColumn("""
+-----------+
|    Log    |
|-----------|
| WriteText |
+-----------+
""")

w.AddColumn("""
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
| umlwin                       |
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
""")

w.AddColumn("""
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
""")

w.AddColumn("""
+-----+
| ogl |
+-----+
""")

w.AddColumn("""
+----+
| wx |
+----+
""")

w.AddColumn("""
+--------------+
| UmlWorkspace |
+--------------+
""")

w.AddColumn("""
+-------------+
| LayoutBasic |
+-------------+
""")

w.AddColumn("""
+------------------+
| CoordinateMapper |
+------------------+
""")

w.AddColumn("""
+-------------------+
| GraphLayoutSpring |
+-------------------+
""")

w.AddColumn("""
+----------------+
| OverlapRemoval |
+----------------+
""")

w.AddColumn("""
+-------+
| Frame |
+-------+
""")

w.AddColumn("""
+-------------+
| ImageViewer |
+-------------+
""")

w.Flush()
fp = open("ascii_out.txt", "w")
fp.write(w.contents)
fp.close()

print "done!"
