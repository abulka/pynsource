# Unit tests for pyNsource that
# check that one to many works in the case of a test submitted by Antonio

import unittest
from parsing.api import old_parser, new_parser
from tests.settings import PYTHON_CODE_EXAMPLES_TO_PARSE
from common.logwriter import LogWriter
from parsing.core_parser_ast import set_DEBUGINFO, DEBUGINFO
from textwrap import dedent
from parsing.parse_source import parse_source
from parsing.dump_pmodel import dump_pmodel


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
        # classNames = [classname for classname, classentry in pmodel.classlist.items()]
        # # print(classNames)
        # # print(dump_pmodel(pmodel))
        # assert "Test" in classNames
        # assert classNames == ["Test"]
        # classentry = pmodel.classlist["Test"]
        # # print(classentry)
        # assert len(classentry.defs) == 1
        # assert "hi" in classentry.defs

    def test_issue_81(self):
        # https://github.com/abulka/pynsource/issues/81
        source_code = dedent("""
            variable = 'a'
            print(f'{variable=}')
        """
        )
        pmodel, debuginfo = parse_source(source_code, 
                                         options={"mode": 3}, 
                                         html_debug_root_name="test_issue_81")
        self.assertEqual(pmodel.errors, "")












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
