import sys
import unittest
from parsing.api import old_parser, new_parser
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE
from common.logwriter import LogWriter
from parsing.core_parser_ast import set_DEBUGINFO, DEBUGINFO
from textwrap import dedent
from parsing.parse_source import parse_source
from parsing.dump_pmodel import dump_pmodel


# These tests taken from GitML


class TestExcept(unittest.TestCase):

    # Util

    def assertNoPmodelErrors(self, pmodel):
        # Pity the 'had no classes' message is contaminating the errors message. Oh well we won't get
        # the 'had no classes' message if there were errors, so checking for 'had no classes' is
        # essentially the same as checking for no errors
        # self.assertEqual(pmodel.errors, "")
        self.assertIn("had no classes", pmodel.errors)

    # Tests

    def test_exception_simple(self):
        """Parse simple """
        source_code = dedent(
            """
            def fred():
                try:
                    blah()
                except TypeError as e:
                    raise e
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_exception_simple")
        self.assertNoPmodelErrors(pmodel)

    def test_exception_complex(self):
        """Parse complex multiple exceptions """
        source_code = dedent(
            """
            def fred():
                try:
                    blah()
                except (TypeError, ValueError) as e:
                    blah2()
                    raise e
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_exception_complex")
        self.assertNoPmodelErrors(pmodel)

    # @unittest.skipIf(sys.version_info < (3, 0), 'python 3 specific test')
    def test_exception_from_none(self):
        """Parse python 3 specific"""
        source_code = dedent(
            """
            def fred():
                try:
                    blah()
                except ImportError:
                    raise BuildFailed('blah') from None
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_exception_from_none")
        self.assertNoPmodelErrors(pmodel)

    def test_exception_bug_2018(self):
        """Parse python 3 specific"""
        source_code = dedent(
            """
            def fred():
                try:
                    blah()
                except Exception as e:
                    raise e
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_exception_bug_2018")
        self.assertNoPmodelErrors(pmodel)
