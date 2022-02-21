import unittest
from parsing.api import new_parser
from common.logwriter import LogWriter
from parsing.core_parser_ast import set_DEBUGINFO, DEBUGINFO
from textwrap import dedent
from parsing.parse_source import parse_source
from parsing.dump_pmodel import dump_pmodel


class TestParseTypeAnnotations(unittest.TestCase):
    
    def test_type_annotations_in_method_args(self):
        """
        Detect type annotations in method arguments
        https://github.com/abulka/pynsource/issues/75
        """
        source_code = dedent(
            """
            # Ironically, declaring the Restaurant class will trigger Pynsource to treat
            # self.restaurant as a implicit reference to the Restaurant class - without needing type annotations
            # simply due to the convention that it is the same name with the first letter in uppercase.
            # But let's not rely on this here, so comment out this 'trick'
            # 
            # class Restaurant:
            #     pass

            class Customer:
                def __init__(self, restaurant: Restaurant):
                    self.restaurant = restaurant
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_type_annotations_in_method_args")
        self.assertEqual(pmodel.errors, "")
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        # print(classNames)
        # print(dump_pmodel(pmodel))  # very pretty table dump of the parse model
        self.assertIn("Customer", classNames)
        classentry = pmodel.classlist["Customer"]
        # print(classentry)
        self.assertEqual(len(classentry.defs), 1)
        self.assertIn("__init__", classentry.defs)

        # ensure the type annotation dependencies have been detected
        self.assertEqual(len(classentry.classdependencytuples), 1)
        self.assertEqual(classentry.classdependencytuples[0], ('restaurant', 'Restaurant'))

        # make sure the attributes are being created as well
        attrnames = [attr_tuple.attrname for attr_tuple in classentry.attrs]
        assert "restaurant" in attrnames

    def test_type_annotation_outside_class(self):
        # Outside of a class Pynsource can't make a class to class dependency but should parse ok.
        # (but GitUML can make a module dependency since it supports module dependencies and Pynsource currently does not)
        source_code = dedent(
            """

            def func(varin: dict):
                pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_type_annotation_outside_class")
        self.assertIn("had no classes", pmodel.errors)  # not really an error

    def test_type_annotation_in_attr_assignment(self):
        # Ensure attr assignment in class, with type annotation, works
        source_code = dedent(
            """
            class Customer:
                def __init__(self, restaurant):
                    self.restaurant: Restaurant = restaurant
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_type_annotation_in_attr_assignment")
        self.assertEqual(pmodel.errors, "")
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        # print(classNames)
        # print(dump_pmodel(pmodel))  # very pretty table dump of the parse model
        self.assertIn("Customer", classNames)
        classentry = pmodel.classlist["Customer"]
        # print(classentry)
        self.assertEqual(len(classentry.defs), 1)
        self.assertIn("__init__", classentry.defs)

        # ensure the type annotation dependencies have been detected
        self.assertEqual(len(classentry.classdependencytuples), 1)
        self.assertEqual(classentry.classdependencytuples[0], ('restaurant', 'Restaurant'))

        # make sure the attributes are being created as well
        attrnames = [attr_tuple.attrname for attr_tuple in classentry.attrs]
        assert "restaurant" in attrnames

    def test_type_annotation_attr_tricky_rhs(self):
        # Handle type annotation parsing where no rhs. expression given, and where rhs. is None
        source_code = dedent(
            """
            class Customer:
                def __init__(self, restaurant):
                    self.restaurant: Restaurant = restaurant
                    self.fred: Fred
                    self.xx: Mary = None
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_type_annotation_attr_tricky_rhs")
        self.assertEqual(pmodel.errors, "")
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        # print(classNames)
        # print(dump_pmodel(pmodel))  # very pretty table dump of the parse model
        self.assertIn("Customer", classNames)
        classentry = pmodel.classlist["Customer"]
        # print(classentry)
        self.assertEqual(len(classentry.defs), 1)
        self.assertIn("__init__", classentry.defs)

        # make sure the attributes are being created
        attrnames = [attr_tuple.attrname for attr_tuple in classentry.attrs]
        assert "restaurant" in attrnames
        assert "fred" in attrnames
        assert "xx" in attrnames
        
        # ensure the type annotation dependencies have been detected
        self.assertEqual(len(classentry.classdependencytuples), 3)
        self.assertIn(('restaurant', 'Restaurant'), classentry.classdependencytuples)
        self.assertIn(('fred', 'Fred'), classentry.classdependencytuples)
        self.assertIn(('xx', 'Mary'), classentry.classdependencytuples)

    def test_type_annotation_builtin_types_skipped(self):
        # Skip creating references to built in types like 'bool' etc
        source_code = dedent(
            """
            class Customer:
                def __init__(self):
                    self.a: bool
                    self.b: int
                    self.c: str
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_type_annotation_builtin_types_skipped")
        self.assertEqual(pmodel.errors, "")
        classentry = pmodel.classlist["Customer"]
        self.assertEqual(len(classentry.classdependencytuples), 0)

    def test_function_annotation_1(self):
        # Ensure can parse function annotation return types - see https://github.com/abulka/pynsource/issues/79
        """
        The reported error was caused by type having a '.' in the type e.g. Exception.ArithmeticError where we got
            annotation=Attribute(
               value=Name(lineno=6, col_offset=27, id='Exception', ctx=Load()),
               attr='ArithmeticError',
        rather than
            annotation=Name(lineno=7, col_offset=27, id='Exception', ctx=Load()),

        The solution is for the parser to check if the annotation is an ast.Attribute or ast.Name 
        (see line 1425 in src/parsing/core_parser_ast.py)
        """
        source_code = dedent(
            """
            def func1(x: Exception) -> None: pass
            def func1(x: Exception.ArithmeticError) -> float: pass
            """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_function_annotation_1")
        self.assertIn("had no classes.", pmodel.errors)

    def test_function_annotation_2(self):
        source_code = dedent(
            """
            class Customer:
                def meth1(self, param: Exception.ArithmeticError) -> None:
                    pass
                def meth2(self, param: Exception) -> SomeOtherClass:
                    pass
            """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_function_annotation_2")
        self.assertEqual(pmodel.errors, "")
        classentry = pmodel.classlist["Customer"]
        self.assertEqual(len(classentry.classdependencytuples), 2)  # Ideally should also find 'SomeOtherClass' dependency? thus 3 dependencies
        self.assertIn(('param', 'Exception'), classentry.classdependencytuples)
        self.assertIn(('param', 'Exception.ArithmeticError'), classentry.classdependencytuples)
        # self.assertIn(('??', 'SomeOtherClass'), classentry.classdependencytuples)  # TODO think about this


class TestNoAssignmentShouldStillCreateAttrs(unittest.TestCase):

    def _ensure_attrs_created(self, pmodel):
        # make sure the attributes are being created
        self.assertEqual(pmodel.errors, "")
        classentry = pmodel.classlist["Customer"]
        attrnames = [attr_tuple.attrname for attr_tuple in classentry.attrs]
        assert "restaurant" in attrnames
        assert "fred" in attrnames
        assert "xx" in attrnames

    def test_assignment_rhs_missing(self):
        """
            When rhs entirely missing, the AST contains an 'Expr' node not an 'Assign' node.

            AST:
            body=[
                Expr(
                    lineno=4,
                    col_offset=8,
                    value=Attribute(
                        lineno=4,
                        col_offset=8,
                        value=Name(lineno=4, col_offset=8, id='self', ctx=Load()),
                        attr='restaurant',
                        ctx=Load(),
                    ),
                ),        
        """
        source_code = dedent(
            """
            class Customer:
                def __init__(self, restaurant):
                    self.restaurant
                    self.fred
                    self.xx
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_assignment_rhs_missing")
        self._ensure_attrs_created(pmodel)

    def test_assignment_rhs_is_None(self):
        """
            Traditional 'Assign' node, attribute create via old rhs/lhs/flush logic.

            AST:
            body=[
                Assign(
                    lineno=4,
                    col_offset=8,
                    targets=[
                        Attribute(
                            lineno=4,
                            col_offset=8,
                            value=Name(lineno=4, col_offset=8, id='self', ctx=Load()),
                            attr='restaurant',
                            ctx=Store(),
                        ),
                    ],
                    value=NameConstant(lineno=4, col_offset=26, value=None),
                    type_comment=None,
                ),        
        """
        source_code = dedent(
            """
            class Customer:
                def __init__(self, restaurant):
                    self.restaurant = None
                    self.fred = None
                    self.xx = None
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_assignment_rhs_is_None")
        self._ensure_attrs_created(pmodel)

    def test_assignment_has_type_annotation(self):
        """
            'AnnAssign' node instead of traditional 'Assign' - copy the Assign logic but adjust
            since can't have multiple lhs when using type annotations.

            AST:
            body=[
                AnnAssign(
                    lineno=4,
                    col_offset=8,
                    target=Attribute(
                        lineno=4,
                        col_offset=8,
                        value=Name(lineno=4, col_offset=8, id='self', ctx=Load()),
                        attr='restaurant',
                        ctx=Store(),
                    ),
                    annotation=Name(lineno=4, col_offset=25, id='Restaurant', ctx=Load()),
                    value=Name(lineno=4, col_offset=38, id='restaurant', ctx=Load()),
                    simple=0,
                ),
        """
        source_code = dedent(
            """
            class Customer:
                def __init__(self, restaurant):
                    self.restaurant: Restaurant = restaurant
                    self.fred: Fred
                    self.xx: Mary = None
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_assignment_has_type_annotation")
        self._ensure_attrs_created(pmodel)


class TestTypeHintsOnFunctionArguments(unittest.TestCase):
    # Repro of python problem with type annotations on function arguments
    """
    Kyle noticed that generic type hints (in general) raise the same error if they are
    specified on arguments in a function/method.  However, those specified on a
    function/method return value work as expected.
    
    Example standalone Python file to parse:

        from typing import Optional, Sequence, Mapping

        def foo(a: Optional[str]):  # ERROR
            return f"Got {a}"
        print(foo("fred"))
        print(foo(None))

        def bar(b: Sequence[int]):  # ERROR
            return f"Got {b}"
        print(bar([1, 2, 3]))

        def qaz() -> Mapping[str, str]:  # OKAY
            return {'a': 'b', 'c': 'd'}
        print(qaz())

        # OUTPUT:
        # Got fred
        # Got None
        # Got [1, 2, 3]
        # {'a': 'b', 'c': 'd'}    
    """

    def testTypeHintsOptional(self):
        source_code = dedent(
        """
            def foo(a: Optional[str]):  # ERROR
                pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_FunctionArguments_testTypeHintsOptional")
        # self.assertEqual(pmodel.errors, "")  # too strict, cos I put no class warning in errors
        self.assertNotIn("error", pmodel.errors)
        self.assertIn("had no classes", pmodel.errors)

    def testTypeHintsSequence(self):
        source_code = dedent(
        """
            def bar(b: Sequence[int]):  # ERROR
                pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_FunctionArguments_testTypeHintsSequence")
        # self.assertEqual(pmodel.errors, "")  # too strict, cos I put no class warning in errors
        self.assertNotIn("error", pmodel.errors)
        self.assertIn("had no classes", pmodel.errors)

    def testTypeHintsMapping(self):
        source_code = dedent(
        """
            def qaz() -> Mapping[str, str]:  # OKAY
                return {'a': 'b', 'c': 'd'}
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_FunctionArguments_testTypeHintsMapping")
        # self.assertEqual(pmodel.errors, "")  # too strict, cos I put no class warning in errors
        self.assertNotIn("error", pmodel.errors)
        self.assertIn("had no classes", pmodel.errors)
