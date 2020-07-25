import unittest
from parsing.api import new_parser
from common.logwriter import LogWriter
from parsing.core_parser_ast import set_DEBUGINFO, DEBUGINFO
from textwrap import dedent
from parsing.parse_source import parse_source
from parsing.dump_pmodel import dump_pmodel


class TestParseTypeAnnotations(unittest.TestCase):
    def test_type_annotation(self):
        """
        Detect type annotations.
        """
        # https://github.com/abulka/pynsource/issues/75
        source_code = dedent(
            """
            # Ironically, declaring the Restaurant class will trigger Pynsource to treat
            # self.restaurant as a implicit reference to the Restaurant class - without needing type annotations
            # simply due to the convention that it is the same name with the first letter in uppercase.
            # But let's not rely on this here, so comment out this 'trick'
            # 
            # class Restaurant:
            #     pass

            def dict_to_plecs_opts(varin: dict):
                pass

            class Customer:
                def __init__(self, restaurant: Restaurant):
                    self.restaurant = restaurant
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_type_annotation")
        self.assertEqual(pmodel.errors, "")
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        # print(classNames)
        # print(dump_pmodel(pmodel))  # very pretty table dump of the parse model
        self.assertIn("Customer", classNames)
        classentry = pmodel.classlist["Customer"]
        # print(classentry)
        self.assertEqual(len(classentry.defs), 1)
        self.assertIn("__init__", classentry.defs)
        # print(classentry.classdependencytuples)
        self.assertEqual(len(classentry.classdependencytuples), 1)
        self.assertEqual(classentry.classdependencytuples[0], ('restaurant', 'Restaurant'))

    def test_type_annotation_outside_class(self):
        source_code = dedent(
            """
            # Outside of a class Pynsource can't make a class dependency but GitUML can make a module dependency

            def func(varin: dict):
                pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_type_annotation_outside_class")
        self.assertIn("had no classes", pmodel.errors)  # not really an error
