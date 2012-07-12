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
| Statechart |
+------------+
""")

w.AddColumn("""
+-----------------------------+
|        UmlShapeCanvas       |
|-----------------------------|
| scrollStepX                 |  ---->  [ LayoutBasic ]
| scrollStepY                 |  ---->  [ OverlapRemoval ]
| classnametoshape            |  ---->  [ CoordinateMapper ]
| log                         |  ---->  [ GraphLayoutSpring ]
| frame                       |  ---->  [ UmlWorkspace ]
| save_gdi                    |
|-----------------------------|
| __init__                    |
+-----------------------------+
""")

w.Flush()
fp = open("ascii_out.txt", "w")
fp.write(w.contents)
fp.close()

print "done"
