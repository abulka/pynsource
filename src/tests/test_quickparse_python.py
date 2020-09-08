import unittest
from textwrap import dedent
from parsing.quick_parse import QuickParse
import tempfile

# python -m unittest parsing.python.tests.test_quickparse_python
# python -m unittest parsing.python.tests.test_quickparse_python.TestQuickParseProper.test_module_vars_regex101


class TestQuickParseProper(unittest.TestCase):
    def scan(self, source_code):
        # Re temporary files, win10 needs delete=False otherwise other routines cannot access.
        # Need to pass "wt" since we're writing text, not bytes - helps python3 compatibility.
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as temp:
            temp.write(source_code)
            temp.flush()
            qp = QuickParse(temp.name)
        return qp

    def test_simple_module(self):
        source_code = dedent(
            """
            x = 100
            def fred(): pass
            def mary(a,b): pass
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, ["fred", "mary"])
        self.assertEqual(qp.quick_found_module_attrs, ["x"])

    def test_indent_correct(self):
        source_code = dedent(
            """
            x = 100
                y = 200
            z = 100
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(qp.quick_found_module_attrs, ["x", "z"])

    def test_async_def(self):
        source_code = dedent(
            """
            def fred(): pass
            async def mary(a,b): pass
            
            # below should NOT match
            
            class A:
                def sam(self)
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, ["A"])
        self.assertEqual(qp.quick_found_module_defs, ["fred", "mary"])
        self.assertEqual(qp.quick_found_module_attrs, [])

    def test_inside_class(self):
        source_code = dedent(
            """
            class A:
                x = 300
                def fred(self): pass
                
                @staticmethod
                def load_from_json(frozen_json):
                    pass
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, ["A"])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(qp.quick_found_module_attrs, [])

    def test_module_vars_regex101(self):
        source_code = dedent(
            """
            aa = 100
            bb=100
            s=2
            a90=0
            a91 =0
            a92 = 0
            app = Mgr()
            app2 = mary()
            app3 = mary(x=2)
            z.x = 2 
            
            # below should NOT match
            
            # a = 100
                y = 200
            hello there
            fred(xx=100)
            def mary(xx=100)
            77=0
            88 = 0
            a93 == 0
            a94 0
            a95 0 =
            if __name__ == "__main__":
                app.run(host="0.0.0.0", port=8000)

        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(
            qp.quick_found_module_attrs,
            ["aa", "bb", "s", "a90", "a91", "a92", "app", "app2", "app3", "z"],
        )

    def test_ignore_named_args_simple(self):
        source_code = dedent(
            """
            y = 100
            mary(x=400)
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(qp.quick_found_module_attrs, ["y"])

    def test_ignore_named_args(self):
        source_code = dedent(
            """
            def fred(request, num_paths=1, waryear=int(DT[2]):
                r = []
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, ["fred"])
        self.assertEqual(qp.quick_found_module_attrs, [])

    def test_vars_with_dots(self):
        source_code = dedent(
            """
            x = 100
                y = 200
            z.x = 2        
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(qp.quick_found_module_attrs, ["x", "z"])

    def test_simple_class(self):
        source_code = dedent(
            """
            class Fred: pass
            class Mary(object):
                pass
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, ["Fred", "Mary"])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(qp.quick_found_module_attrs, [])

    def test_inner_class(self):
        source_code = dedent(
            """
            class Mary(object):
                class Inner:
                    pass
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, ["Mary", "Inner"])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(qp.quick_found_module_attrs, [])

    def test_commented_out_code(self):
        source_code = dedent(
            """
            # class Root(rpc.PulsarServerCommands):
            #     '''Add two rpc methods for testing to the :class:`.PulsarServerCommands`
            #     handler.
            #     '''
            #     def rpc_dodgy_method(self, request):
            #         '''This method will fails because the return object is not
            #         json serialisable.'''
            #         return Calculator
            # 
            #     rpc_check_request = RequestCheck()
            # 
            # 
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(qp.quick_found_module_attrs, [])

    @unittest.skip("too tricky to achieve without proper parsing")
    def test_inside_for_loop_tricky(self):
        """If allow leading spaces to variables to count, then variables
        inside classes and functions would get counted - that would be very bad"""
        source_code = dedent(
            """
            for line in lines:
                x = 100
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, [])
        self.assertEqual(qp.quick_found_module_attrs, ["x"])

    @unittest.skip("too tricky to achieve without proper parsing")
    def test_if_stmt_tricky(self):
        """If allow leading spaces to variables to count, then variables
        inside classes and functions would get counted - that would be very bad"""
        source_code = dedent(
            """
            y = 200

            if True:
                x = 100
                def fred(): pass

            if __name__ == "__main__":
                def mary(): pass
        """
        )
        qp = self.scan(source_code)

        self.assertEqual(qp.quick_found_classes, [])
        self.assertEqual(qp.quick_found_module_defs, ["fred", "mary"])
        self.assertEqual(qp.quick_found_module_attrs, ["y", "x"])
