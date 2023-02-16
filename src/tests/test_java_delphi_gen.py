import unittest
from parsing.api import new_parser, old_parser

# python -m unittest tests.test_java_delphi_gen


class TestJavaDelphiGen(unittest.TestCase):
    def test_1(self):
        in_filename = "src/tests/testing-generate-java/python-in/utilcc.py"

        p, debuginfo = old_parser(in_filename)
        pmodel_old = p.pmodel

        pmodel_new, debuginfo = new_parser(in_filename)

        # print pmodel_old.modulemethods
        # print pmodel_new.modulemethods

        old = set(pmodel_old.modulemethods)
        new = set(pmodel_new.modulemethods)

        any_changes = old ^ new

        differences_expected = set(["safeconvert", "PopFoldersTillFind"])

        # no_changes = set()
        # self.assertSetEqual(any_changes, no_changes, any_changes)

        # Nested methods are not picked up by the new ast parser
        self.assertSetEqual(any_changes, differences_expected, any_changes)
