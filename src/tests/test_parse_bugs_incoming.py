import sys
import unittest
from parsing.api import old_parser, new_parser
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE
from common.logwriter import LogWriter
from parsing.core_parser_ast import set_DEBUGINFO, DEBUGINFO
from textwrap import dedent
from parsing.parse_source import parse_source
from parsing.dump_pmodel import dump_pmodel

# Unit tests for incoming Pynsource parsing bugs


class TestIncomingBugs(unittest.TestCase):
    def setUp(self):
        pass

    def test_bug_pyplecs(self):
        """
        """
        # breakpoint()
        FILE = PYTHON_CODE_EXAMPLES_TO_PARSE + "testmodule_bug_pyplecs.py"

        # Can also run using
        # python3 pynsource-cli.py --mode 3 --graph tests/python-in/testmodule_bug_pyplecs.py

        # create a html log file to contain html info 
        log = LogWriter(FILE, print_to_console=False)
        log.out_html_header()

        # Normally debug info is false for performance reasons, so turn it on temporarily and restore it later
        old_debug_info_value = DEBUGINFO()
        set_DEBUGINFO(True)
        try:
            pmodel, debuginfo = new_parser(FILE, log, options={"mode": 3})
        finally:
            set_DEBUGINFO(old_debug_info_value)

        # this log finishing is all written out automatically in new_parser / parse / _convert_ast_to_old_parser
        # if there is an error- otherwise we have to do it ourselves.
        #
        if not pmodel.errors:
            # log.out("<hr><h1>Errors (shouldn't be any):</h1>")
            # log.out_wrap_in_html(pmodel.errors)
            log.out("<hr><h1>debuginfo:</h1>")
            log.out(debuginfo)
            log.out_html_footer()
            log.finish()

        self.assertEqual(pmodel.errors, "")
        # print(dump_pmodel(pmodel))
        # print("html log file is", log.out_filename)

        # -------------------------------------------------------

        # gotevent1 = 0
        # gotevent2 = 0
        # gotevent3 = 0
        # gotevent4 = 0
        # gotevent5 = 0
        # gotevent6 = 0
        # gotevent7 = 0

        # for classname, classentry in list(self.p.classlist.items()):
        #     if classname == "Fred":
        #         gotevent1 = 1
        #         assert classentry.classesinheritsfrom == [
        #             "Mary",
        #             "Sam",
        #         ], classentry.classesinheritsfrom

        #     if classname == "MarySam":
        #         gotevent3 = False  # should not get this

        # assert gotevent1
        # assert not gotevent3


    def test_yield(self):
        source_code = dedent(
            """
            class Test():
                def gen(self):
                    yield 20
                    yield
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3})
        self.assertEqual(pmodel.errors, "")
        print(pmodel)


    @unittest.skip("not necessary because sorting in display model is what's important, which is done")
    def test_sorted_attributes(self):
        # see also 'test_plantuml_sorted' in src/tests/test_parse_plantuml.py
        source_code = dedent("""
            class ParseMeTest:
                def __init__(self):
                    self.z = 1
                    self.a = 1
                def aa(self): pass
                def zz(self): pass
                def bb(self): pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3})
        self.assertEqual(pmodel.errors, "")

        t = dump_pmodel(pmodel)
        print(t)

    def test_staticmethod(self):
        # https://github.com/abulka/pynsource/issues/74
        source_code = dedent(
            """
            class Test():
                @staticmethod
                def hi():
                    pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_staticmethod")
        self.assertEqual(pmodel.errors, "")
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        # print(classNames)
        # print(dump_pmodel(pmodel))
        assert "Test" in classNames
        assert classNames == ["Test"]
        classentry = pmodel.classlist["Test"]
        # print(classentry)
        assert len(classentry.defs) == 1
        assert "hi" in classentry.defs


    def test_decorators(self):
        """
        Ensure we create class attributes from methods marked with property decorators, 
        and create methods for all other decorator types.
        """
        source_code = dedent(
            """
            # staticmethod and classmthod

            class Test():
                @staticmethod
                def hi():
                    pass
                
                @classmethod
                def there(cls):
                    pass

            # static method, can call directly on class (no instance needed)
            Test.hi()

            # create instance
            t = Test()
            t.hi()

            t.myval = 100
            t.myval



            # Abstract methods - technique 1

            from abc import ABC, abstractmethod 
              
            class AbstractAnimal(ABC): 
                @abstractmethod
                def move(self): 
                    pass

            try:
                animal = AbstractAnimal()  # illegal
            except TypeError:
                print("Yep, can't instantiate an abstract class.")

            animal = Animal()
            print(animal)
            animal.move()



            # Abstract methods - technique 2

            import abc
            
            class Crop(metaclass=abc.ABCMeta):
                '''Abstract class declaring that its subclasses must implement that the sow() & harvest() methods.'''
                @abc.abstractmethod
                def sow(self): pass
                 
                def irrigate(self): pass
                 
                @abc.abstractmethod
                def harvest(self): pass
                


            # Properties
            
            class PropsClass():
                @staticmethod
                def hi():
                    print("hi from static method")
            
                @property
                def myval(self):
                    print(f"getting val")
                    return 999
            
                @myval.setter
                def myval(self, val):
                    print(f"setting val to {val}")
            
                                     
        """
        )
        pmodel, debuginfo = parse_source(source_code, options={"mode": 3}, html_debug_root_name="test_decorators")
        self.assertEqual(pmodel.errors, "")
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        # print(classNames)
        # print(dump_pmodel(pmodel))
        assert "Test" in classNames
        assert "AbstractAnimal" in classNames
        assert "Crop" in classNames
        assert "PropsClass" in classNames

        classentry = pmodel.classlist["Test"]
        assert len(classentry.defs) == 2
        assert "hi" in classentry.defs  # staticmethod
        assert "there" in classentry.defs  # classmethod

        classentry = pmodel.classlist["AbstractAnimal"]
        assert len(classentry.defs) == 1
        assert "move" in classentry.defs

        classentry = pmodel.classlist["Crop"]
        assert len(classentry.defs) == 3
        assert "sow" in classentry.defs
        assert "irrigate" in classentry.defs
        assert "harvest" in classentry.defs

        classentry = pmodel.classlist["PropsClass"]
        assert len(classentry.defs) == 1
        assert "hi" in classentry.defs
        attrnames = [attr_tuple.attrname for attr_tuple in classentry.attrs]
        assert "myval" in attrnames


    def test_issue_80(self):
        # https://github.com/abulka/pynsource/issues/80
        source_code = dedent("""
            class Foo(object):
            
                @classmethod
                def create(cls,VAR1):
                    self = Foo()  # <-- this is needed to cause the error
                    self.var1 = VAR1  # <-  error here
                    return self
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_80")
        self.assertEqual(pmodel.errors, "")
        # print(dump_pmodel(pmodel))

    @unittest.skipIf(sys.version_info.minor < 8, 'Need to upgrade Pynsource to run in Python 3.8 to handle this syntax')
    def test_issue_81(self):
        # https://github.com/abulka/pynsource/issues/81
        """"""  # avoid test message grabbing first line of the docstring below
        """
        This ability to specify an = sign after a variable in an fstring is a Python 3.8
        feature. See "f-strings support = for self-documenting expressions and debugging" in
        https://docs.python.org/3/whatsnew/3.8.html
        Pynsource will have to be running under Python 3.8 to handle this syntax.
        Pynsource release binaries currently run under Python 3.7.
        Running the latest master of Pynsource from source under Python 3.8 will allow you to parse this 3.8 syntax.
        I hope to update the Pynsource release binaries to Python 3.8 in the next release.
        """
        source_code = dedent("""
            variable = 'a'
            print(f'{variable=}')
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_81")
        self.assertNotIn("error", pmodel.errors)
        self.assertIn("had no classes", pmodel.errors)
        print(sys.version_info.minor)


    @unittest.skipIf(sys.version_info.minor < 8, 'Need to upgrade Pynsource to run in Python 3.8 to handle this syntax')
    def test_issue_typehint_optional(self):
        """"""  # avoid test message grabbing first line of the docstring below
        source_code = dedent("""
            x: Optional[str]
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_typehint_optional")
        self.assertNotIn("error", pmodel.errors)
        self.assertIn("had no classes", pmodel.errors)

    # June 2021 tests

    def test_issue_class_type_annotation_85(self):
        """Seems ok under pythons 3.7, 2.8 and 3.9. 
        Release 1.77 failed under linux and windows and some builds on Mac, 
        but this problem has seems to have gone away by rebuilding the executables - mysterious.
        """
        source_code = dedent("""
            class SimpleHttpTask(Task):
                url = None
                method = "GET"
                client: requests.Session = requests.Session()
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_class_type_annotation_85")
        self.assertNotIn("error", pmodel.errors)
        # print(dump_pmodel(pmodel))

    def test_issue_subscript_issue_93(self):
        """Tricky variable annotation, used to fail in Python 3.9 but passed in 3.7 and 3.8. 
        Changed visit_AnnAssign() to fix this, passes now under all Python versions.
        """
        source_code = dedent("""
            class Issue93:
                def method1(self):
                    self.pages: List[SnapFileView2D] = list()
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_subscript_issue_93")
        self.assertNotIn("error", pmodel.errors)
        # print(dump_pmodel(pmodel))
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        assert "Issue93" in classNames
        classentry = pmodel.classlist["Issue93"]
        assert len(classentry.defs) == 1
        assert "method1" in classentry.defs
        assert len(classentry.attrs) == 1
        attrnames = [attr_tuple.attrname for attr_tuple in classentry.attrs]
        assert "pages" in attrnames
        self.assertEqual(len(classentry.classdependencytuples), 1)
        self.assertEqual(classentry.classdependencytuples[0], ('pages', 'SnapFileView2D'))


    @unittest.skipIf(sys.version_info.minor < 8, 'Need to upgrade Pynsource to run in Python 3.8 to handle this syntax')
    def test_issue_walrus_issue_94(self):
        """Only Python 3.8 and higher can handle this new walrus syntax"""
        source_code = dedent("""
            class Issue94:
                def method1(self):
                    chairs: dict[int, str]
                    number: int
                    if (pair := chairs.get(number, None)) is None:
                        pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_walrus_issue_94")
        self.assertNotIn("error", pmodel.errors)
        # print(dump_pmodel(pmodel))
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        assert "Issue94" in classNames

    def test_issue_matrix_issue_102(self):
        """It looks like the "new" matrix multiplication operator (see PEP-465) is not handled correctly."""
        source_code = dedent("""
            a = 1
            world_co = np.array(ob.matrix_world @ vertex.co)
            b = 1
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_matrix_issue_102")
        self.assertNotIn("error", pmodel.errors)
        print(dump_pmodel(pmodel))

    def test_issue_typing_103(self):
        """It looks like parameter types that drill down more than two levels are causing the error.
        So gym.spaces.Space fails but gym.spaces is OK."""
        source_code = dedent("""
            class A:
                def __init__(self, p: gym.spaces.Space):
                    pass
        """
        )
        source_code = dedent("""
            class A:
                def __init__(self, p: A.B.C):
                    pass
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_typing_103")
        self.assertNotIn("error", pmodel.errors)
        # print(dump_pmodel(pmodel))
        classNames = [classname for classname, classentry in pmodel.classlist.items()]
        assert "A" in classNames
        classentry = pmodel.classlist["A"]
        assert len(classentry.defs) == 1
        assert "__init__" in classentry.defs
        self.assertEqual(len(classentry.classdependencytuples), 1)
        self.assertEqual(classentry.classdependencytuples[0], ('p', 'A.B.C'))

    @unittest.skipIf(sys.version_info.minor < 10, 'Need to upgrade Pynsource to run in Python 3.10 to handle this syntax')
    def test_issue_match_case_116(self):
        """Python 3.10 introduces base statements."""
        source_code = dedent("""
            def get_day_name(day_num: int) -> str:
                match day_num:
                    case 0:
                        return "Sunday"
                    case 1:
                        return "Monday"
                    case _:
                        return "Invalid day number"
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_match_case_116")
        self.assertNotIn("error", pmodel.errors)
        print(dump_pmodel(pmodel))











"""
To set up a launch config in vscode

    {
        "name": "test PYTHON parsing edge cases - test_yield",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceRoot}/src",
        "module": "unittest",
        "args": [
            "tests.test_parse_bugs_incoming.TestIncomingBugs.test_yeild",
        ],
    },  

To set up a launch config in pycharm

    Unittests, Target: Module name:
        tests.test_parse_bugs_incoming.TestIncomingBugs.test_staticmethod
    Working directory:
        /Users/andy/Devel/pynsource/src

"""
