import unittest
import os

import sys

sys.path.append("../src")
from ascii_uml.asciiworkspace import AsciiWorkspace

OUT_FILE = "ascii_out.txt"


class TestCaseAscii_02(unittest.TestCase):
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
| Statechart |
+------------+
"""
        )

        w.AddColumn(
            """
+-----------------------------+
|        UmlShapeCanvas       |
|-----------------------------|
| scrollStepX                 |  ---->  [ Laymanwoman ]
| scrollStepY                 |  ---->  [ OverlapRemoval ]
| evenfreddycansee            |  ---->  [ CoordinateMapper ]
| log                         |  ---->  [ GraphLayoutSpring ]
| frame                       |  ---->  [ UmlWorkspace ]
| save_gdi                    |
|-----------------------------|
| __init__                    |
+-----------------------------+
"""
        )

        w.Flush()
        fp = open(OUT_FILE, "w")
        fp.write(w.contents)
        fp.close()

    def tearDown(self):
        os.remove(OUT_FILE)

    def test_ascii_layout_02(self):
        fp = open(OUT_FILE, "r")
        lines = fp.readlines()
        fp.close()

        self.assertEqual(
            "                                                                                                                      \n",
            lines[0],
        )
        self.assertEqual(
            "| topHandler |  ---->  [ TopHandler ]                    | scrollStepX                 |  ---->  [ Laymanwoman ]      \n",
            lines[4],
        )


def suite():
    suite1 = unittest.makeSuite(TestCaseAscii_02, "test")
    alltests = unittest.TestSuite((suite1,))
    return alltests


def main():
    runner = unittest.TextTestRunner(
        descriptions=0, verbosity=2
    )  # default is descriptions=1, verbosity=1
    runner.run(suite())


if __name__ == "__main__":
    main()
