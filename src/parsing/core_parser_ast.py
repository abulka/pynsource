import sys

ast = None  # we dynamically assign either native ast, typed_ast.ast27 or typed_ast.ast3 to this in mode()

# S
from ast import *  # only used for all the symbols like '_ast.And' etc which are stored into our

# lookup tables e.g. BOOLOP_SYMBOLS in a more general way e.g. 'And'
import ast as ast_native  # native ast of the Python that is running

if sys.version_info >= (3, 0):
    import typed_ast.ast27  # py2 (requires Python 3 to be running)
    import typed_ast.ast3  # py3 (requires Python 3 to be running)

import inspect
import logging
from common.logger import config_log
import traceback
from os import path
from textwrap import dedent

import astpretty  # pip install astpretty

from common.add_line_numbers import add_line_numbers
from parsing.alsm_set_module import get_source_code_sample
from common.architecture_support import whosdaddy, whosgranddaddy
from parsing.class_entry import ClassEntry, Attribute
from parsing.keywords import pythonbuiltinfunctions
from parsing.parse_rhs_analyser import RhsAnalyser
from parsing.quick_parse import QuickParse
from common.logwriter import LogWriter, LogWriterNull
from common.logger import LOG_FILENAME

log_proper = logging.getLogger(__name__)
config_log(log_proper)

try:
    from exceptions import SyntaxError
except ImportError:
    pass  # python 3 already imports all built in exceptions

STOP_ON_EXCEPTION = False  # this is only for deep debugging - want this OFF so that errors get reported to GUI
_DEBUGINFO = False
def DEBUGINFO(): return _DEBUGINFO
def set_DEBUGINFO(flag: bool): global _DEBUGINFO; _DEBUGINFO = flag  # allow setting from outside this module
DEBUGINFO_IMMEDIATE_PRINT = False
DEBUG_TO_LOG_PROPER = True
DEBUG_TO_LOG_PROPER_FLUSH_STATE = False  # usually too verbose for log file
DEBUG_TO_LOG_PROPER_PARSE_HISTORY = True  # very verbose and a little weird/hard to interpret

last_python_mode = 0

if getattr(sys, 'frozen', False):
    # running in a bundle
    _DEBUGINFO = False

def as_str(obj):
    """
    Converts type object into a simple string, without the _ast or _ast27 etc. prefix

    str(And)
    Out[9]: "<class '_ast.And'>"

    repr(And3)
    Out[3]: "<class '_ast27.And'>"

    :param obj: ast type object e.g. _ast.And
    :return: string e.g. 'And'
    """
    s = repr(obj)
    s = s.replace("typed_ast.", "")
    _from = s.index(".") + 1
    _to = s.index("'", _from)
    return s[_from:_to]


BOOLOP_SYMBOLS = {as_str(And): "and", as_str(Or): "or"}

BINOP_SYMBOLS = {
    as_str(Add): "+",
    as_str(Sub): "-",
    as_str(Mult): "*",
    as_str(Div): "/",
    as_str(FloorDiv): "//",
    as_str(Mod): "%",
    as_str(LShift): "<<",
    as_str(RShift): ">>",
    as_str(BitOr): "|",
    as_str(BitAnd): "&",
    as_str(BitXor): "^",
    as_str(Pow): "**",
    as_str(MatMult): "@",
}

CMPOP_SYMBOLS = {
    as_str(Eq): "==",
    as_str(Gt): ">",
    as_str(GtE): ">=",
    as_str(In): "in",
    as_str(Is): "is",
    as_str(IsNot): "is not",
    as_str(Lt): "<",
    as_str(LtE): "<=",
    as_str(NotEq): "!=",
    as_str(NotIn): "not in",
}

UNARYOP_SYMBOLS = {as_str(Invert): "~", as_str(Not): "not", as_str(UAdd): "+", as_str(USub): "-"}

ALL_SYMBOLS = {}
ALL_SYMBOLS.update(BOOLOP_SYMBOLS)
ALL_SYMBOLS.update(BINOP_SYMBOLS)
ALL_SYMBOLS.update(CMPOP_SYMBOLS)
ALL_SYMBOLS.update(UNARYOP_SYMBOLS)

TREAT_PROPERTY_DECORATOR_AS_PROP = True

BUILT_IN_TYPES = ('int', 'float', 'bool', 'str', 'bytes', 'List', 'Set', 'Dict', 'Tuple', 'Optional',
    'Callable', 'Iterator', 'Union', 'Any', 'Mapping', 'MutableMapping', 'Sequence', 'Iterable', 'Set',
    'Match', 'AnyStr', 'IO', 'Callable', 'TypeVar')  # I think I identified them all!

class OldParseModel(object):
    def __init__(self):
        self.classlist = {}
        self.modulemethods = []
        self.errors = ""
        self.filename = ""  # new, 2020, way of getting module name


def parse(filename, log=None, options={}):
    """
    This is the main entry point for parsing python and getting back a simplified parse model

    Args:
        filename: python file to parse
        log:
        options: pmodel, debuginfo

    Returns:

    """

    # OLD
    # node = _ast_parse(filename)
    # pmodel, debuginfo = _convert_ast_to_old_parser(node, filename, log, options)
    # return pmodel, debuginfo

    # NEW
    _mode = options.get("mode", 2)
    mode(_mode)
    pmodel = OldParseModel()

    log_proper.info(f"Parsing {filename}, syntax mode {_mode}")
    pmodel.filename = filename  # new, 2020

    if _mode == 2:
        generic_help = "If you are parsing Python 3 code, check the menu item 'File/Python 3."
    else:
        generic_help = "If you are parsing Python 2 code, uncheck the menu item 'File/Python 3."
        generic_help += f"\n\nBe aware that Pynsource is running under Python {sys.version} and thus cannot handle syntax > than that version."
    generic_help += "\n\nOr of course you may be dealing with a real syntax error :-)"

    try:
        node = _ast_parse(filename)
    except SyntaxError as e:
        mode(0)  # reset
        pmodel.errors = f"Syntax error in parsing\n'{filename}'\n\n{_format_syntax_error_nicely(e)}\n\nPynsource is in Python {_mode} syntax mode.\n{generic_help}"
        # log_proper.error(" ".join(pmodel.errors.split()))  # remove multiple spaces
        log_proper.error(pmodel.errors)  # changed my mind, log again with newlines intact ;-)
        return pmodel, ""
    except Exception as e:
        mode(0)  # reset
        pmodel.errors = f"General exception in parsing\n'{filename}'\nassuming Python {_mode} syntax - exception is: {e}.\n\n{generic_help}"
        return pmodel, ""
    else:
        msg = f"Ok parsing the file {filename} - no syntax errors encountered"
        log_proper.info(msg)
        log.out(msg)

    pmodel, debuginfo = _convert_ast_to_old_parser(node, filename, log, options)  # guaranteed to return ok, any exception in pmodel.errors (string)
    pmodel.filename = filename  # new, 2020
    warn_if_no_classes_found(pmodel)  # new, 2020
    mode(0)  # reset
    return pmodel, debuginfo  # 'debuginfo' is string of html

def warn_if_no_classes_found(pmodel):
    if len(pmodel.classlist) == 0:
        pmodel.errors += f"{path.basename(pmodel.filename)} had no classes."

def _format_syntax_error_nicely(e):
    try:
        return f"'{e.msg}' on line {e.lineno}:\n\n{e.text}"
    except:
        return repr(e)

def _ast_parse(filename):
    """
    Does the actual ast parsing, by calling python's built in ``ast.parse(source)``.

    We also enhance the tree by adding parent and root attributes to each node, so that we can always get to the root
    and parent. Currently 'root' is only used once, when visting the Module, in order to pretty print the tree,
    and to store the original source code in 'root.source_code'. The attribute 'parent' is not yet used.

    :param filename: python file to parse
    :return: ast root tree node
    """
    with open(filename, "r", encoding='utf-8') as f:
        source = f.read()

    node = ast.parse(source)
    root = node

    root.source_code = source

    # Pretty dump AST
    # print ast.dump(node)
    # print ast.dump(node, annotate_fields=False)
    # astpretty.pprint(node)

    # Enhance tree by adding parent and root attributes to each node
    root.parent = None
    root.root = root
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node
            child.root = root

    return root

def _remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    s = re.sub(clean, '\n', text)
    # now get rid of blank lines and insert newlines only on visit_* occurrances
    lines = s.splitlines()
    new_s = ""
    for line in lines:
        if line.strip() != "":
            if line.startswith("visit_"):
                new_s += "\n\t"
            new_s += line.strip() + " "
    return new_s

def _extract_source_code_line(filename, lineno):
    if lineno == 0:
        return f"UNKNOWN source code since line number is 0 ?"
    with open(filename, encoding='utf-8') as f:
        our_lines = f.readlines()
        if lineno < len(our_lines):
            return our_lines[lineno - 1].strip()
        else:
            return f"?line {lineno} exceeds num lines in file {len(our_lines)}, last source code line is {our_lines[-1].strip()}"

def _convert_ast_to_old_parser(node, filename, log, options={}):
    """
    Args:
        node: ast node after parsing by python's ast library
        filename:
        _log:
        options:

    Returns:

    """
    logh = log
    if not logh:
        logh = LogWriterNull()

    qp = QuickParse(filename, logh)
    v = Visitor(qp, logh, options)

    # Give visitor access to source code, for diagnostic purposes
    with open(filename, encoding='utf-8') as f:
        v.source_code_lines = f.readlines()

    try:
        v.visit(node)
    except Exception as err:
        # traceback.print_exception(type(ex), ex, ex.__traceback__)

        source_code_line = _extract_source_code_line(filename, v.latest_lineno)
        v.model.errors += f"error Pynsource couldn't handle traversing AST in file {filename} corresponding to approx. lineno {v.latest_lineno} coloffset {v.latest_col_offset} - source code:\n\n {source_code_line}"
        v.model.errors += f"\n\nPlease report this to https://github.com/abulka/pynsource/issues"
        v.model.errors += f"\n\nLog file location:\n{LOG_FILENAME}"
        v.model.errors += f"\n\nActual exception:\n\n{err}"

        if DEBUG_TO_LOG_PROPER:  # output goes to regular python logging
            log_proper.error(f"html version of debug info may exist at: '{logh.out_filename}'")
            log_proper.error(f"model.errors: '{v.model.errors}'")

            """IMPORTANT TO LEAVE THIS IN because it reports the actual exception in the proper log"""
            # very verbose and a little weird to interpret, so leave it out                
            # log_proper.error(f"Parsing Visit error: {err}, Debug info: {v.result_for_log_proper_cleaned}")

            # this is more normal and easier to figure out where the pynsource ast parser crashed
            log_proper.error(f"Full traceback: {traceback.format_exc()}")

            # DEBUG_TO_LOG_PROPER_PARSE_HISTORY adds some visit history info somehow, 
            # so may be useful on ocassion of an error.
            if DEBUG_TO_LOG_PROPER and DEBUG_TO_LOG_PROPER_PARSE_HISTORY:
                log_proper.debug(v.result_for_log_proper_cleaned)

        # debug output goes to special html formatted log file controlled by 'logh' object
        logh.out("Parsing Visit error: {0}".format(err), force_print=True)
        logh.out_wrap_in_html(traceback.format_exc(), style_class="stacktrace")
        if DEBUGINFO():
            debuginfo = "<br>".join(v.result)
            logh.out(debuginfo)
            logh.out(f"<br>model.errors: '{v.model.errors}'<br>")
            logh.out_html_footer()
            logh.finish()

        if STOP_ON_EXCEPTION:
            raise

    debuginfo = "<br>".join(v.result)
    return v.model, debuginfo


class T:
    pass  # fake base class, so can dynamically switch - https://stackoverflow.com/questions/9539052/how-to-dynamically-change-base-class-of-instances-at-runtime


# class Visitor(ast.NodeVisitor):
class Visitor(T):
    def __init__(self, quick_parse, logh, options={}):

        self.model = OldParseModel()
        self.source_code_lines = []  # new for 2020, helps with diagnostics only
        self.logh = logh
        self.stack_classes = []
        self.stack_module_functions = [False]
        self.quick_parse = quick_parse
        self.init_lhs_rhs()
        self.imports_encountered = []

        self.result = []                 # accumulated visitor debug info with html
        self.result_for_log_proper = []  # accumulated visitor debug info without html
        self.indent_with = " " * 4
        self.indentation = 0
        self.new_lines = 0

        self.latest_lineno = 0
        self.latest_col_offset = 0

        self.treat_property_decorator_as_prop = options.get(
            "TREAT_PROPERTY_DECORATOR_AS_PROP", TREAT_PROPERTY_DECORATOR_AS_PROP
        )

    def init_lhs_rhs(self):
        self.lhs = []
        self.rhs = []
        self.lhs_recording = True
        self.made_rhs_call = False
        self.made_assignment = False
        self.made_append_call = False
        self.made_import = False
        self.pos_rhs_call_pre_first_bracket = None
        self.stop_recording_rhs_inside_first_bracket = None

    def record_lhs_rhs(self, s):
        if self.lhs_recording:
            self.lhs.append(s)
            self.write("\nLHS %d %s\n" % (len(self.lhs), self.lhs), mynote=2)
        else:
            if (
                self.stop_recording_rhs_inside_first_bracket != None
                and self.stop_recording_rhs_inside_first_bracket > 1
            ):
                self.write(
                    "\nPrevented RHS %d %s due to stop_recording_rhs_inside_first_bracket\n"
                    % (len(self.rhs), self.rhs),
                    mynote=2,
                )
            else:
                self.rhs.append(s)
                self.write("\nRHS %d %s\n" % (len(self.rhs), self.rhs), mynote=2)

    def am_inside_module_function(self):
        return self.stack_module_functions[-1]

    def current_class(self):
        # Returns a ClassEntry or None
        if self.stack_classes:
            return self.stack_classes[-1]
        else:
            return None

    def pop_a_function_or_method(self):
        if self.current_class():
            self.current_class().stack_functions.pop()
            self.write("  (POP method) %s " % self.current_class().stack_functions, mynote=3)
        else:
            self.stack_module_functions.pop()
            self.write("  (POP module function) %s " % self.stack_module_functions, mynote=3)

    def push_a_function_or_method(self):
        if self.current_class():
            self.current_class().stack_functions.append(True)
            self.write("  (PUSH method) %s " % self.current_class().stack_functions, mynote=3)
        else:
            self.stack_module_functions.append(True)
            self.write("  (PUSH module function) %s " % self.stack_module_functions, mynote=3)

    def in_class_static_area(self):
        return self.current_class() and not self.current_class().stack_functions[-1]

    def in_method_in_class_area(self):
        return self.current_class() and self.current_class().stack_functions[-1]

    def build_class_entry(self, name):
        c = ClassEntry(name)
        self.model.classlist[name] = c
        self.stack_classes.append(c)
        c.name_long = "_".join([str(c) for c in self.stack_classes])
        self.write(
            "  (inside class %s) %s " % (c.name, [str(c) for c in self.stack_classes]), mynote=3
        )
        return c

    def add_composite_dependency(self, t):
        if t[1] not in BUILT_IN_TYPES and t not in self.current_class().classdependencytuples:
            self.current_class().classdependencytuples.append(t)

    def flush_state(self, msg=""):
        if DEBUG_TO_LOG_PROPER and DEBUG_TO_LOG_PROPER_FLUSH_STATE:
            self.result_for_log_proper.append(f"| state: lhs=%s rhs=%s made_assignment=%s made_append_call=%s made_rhs_call=%s pos_rhs_call_pre_first_bracket=%s in_class_static_area=%s in_method_in_class_area=%s msg=%s |" % (
                self.lhs,
                self.rhs,
                self.made_assignment,
                self.made_append_call,
                self.made_rhs_call,
                self.pos_rhs_call_pre_first_bracket,
                self.in_class_static_area(),
                self.in_method_in_class_area(),
                msg
            ))
        if DEBUGINFO():
            self.write(
                """
                    <table>
                        <tr>
                            <th>lhs</th>
                            <th>rhs</th>
                            <th>made_assignment</th>
                            <th>made_append_call</th>
                            <th>made_rhs_call</th>
                            <th>pos_rhs_call_pre_first_bracket</th>
                            <th>in_class_static_area</th>
                            <th>in_method_in_class_area</th>
                            <th></th>
                        </tr>
                        <tr>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                        </tr>
                    </table>
                """
                % (
                    self.lhs,
                    self.rhs,
                    self.made_assignment,
                    self.made_append_call,
                    self.made_rhs_call,
                    self.pos_rhs_call_pre_first_bracket,
                    self.in_class_static_area(),
                    self.in_method_in_class_area(),
                    msg,
                ),
                mynote=0,
            )

        if self.made_import:
            msg = "self.imports_encountered %s" % self.imports_encountered

            if DEBUG_TO_LOG_PROPER:
                self.result_for_log_proper.append(msg)
            if DEBUGINFO():
                self.write(msg, mynote=2)

    @property
    def result_for_log_proper_cleaned(self):
        s = " ".join(self.result_for_log_proper)
        s = _remove_html_tags(s)
        # s = s.replace("<br>", " ")
        # s = s.replace("<hr>", " ")
        # s = s.replace("\n", " ")
        # s = " ".join(s.split())  # remove multiple spaces
        return "Parse History: " + s

    def flush(self):
        """
            Flush is called after:
                * newlines,
                * ends of classes
                * end of functions
                * should be more?

            It is only interested in whether an assignment has been made or an append call has been made
            in order to create the relevant attribute and type (one or many).
            """

        if DEBUGINFO():
            # this is cripplingly slow when bundled in pyinstaller
            self.flush_state(whosgranddaddy())
        else:
            self.flush_state("")

        # At this point we have both lhs and rhs plus three flags and can
        # make a decision about what to create.

        def create_attr_static(t):
            self.current_class().AddAttribute(attrname=t, attrtype=["static"])
            return t

        def create_attr(t):
            if (t == "__class__") and len(self.lhs) >= 3:
                t = self.lhs[2]
                self.current_class().AddAttribute(attrname=t, attrtype=["static"])
            else:
                self.current_class().AddAttribute(attrname=t, attrtype=["normal"])
            return t

        def create_attr_many(t):
            self.current_class().AddAttribute(attrname=t, attrtype=["normal", "many"])
            return t

        def create_attr_please(t):
            if self.made_append_call:
                t = create_attr_many(t)
            else:
                t = create_attr(t)
            return t

        if self.made_assignment or self.made_append_call:

            if self.in_class_static_area():
                t = create_attr_static(self.lhs[0])
            elif self.in_method_in_class_area() and self.lhs[0] == "self" and len(self.lhs) > 1:
                t = create_attr_please(self.lhs[1])
            else:
                t = None  # in module area

            if self.lhs[0] == "self" and len(self.rhs) > 0:
                ra = RhsAnalyser(visitor=self)
                if ra.is_rhs_reference_to_a_class():
                    if t:
                        self.add_composite_dependency((t, ra.rhs_ref_to_class))
                    else:
                        msg = f"Would love to add a dependency to {ra.rhs_ref_to_class} but " \
                              f"lhs is ? - so adding ref from current class {self.current_class().name} " \
                              "which may not make sense.  This is usually a situation where you are " \
                              "assigning to the variable 'self' or something weird."
                        log_proper.warning(msg)
                        self.write(msg, mynote=1)
                        self.add_composite_dependency((self.current_class().name, ra.rhs_ref_to_class))

        self.init_lhs_rhs()
        # self.flush_state()
        self.write("<hr>", mynote=2)

    # MAIN VISIT METHODS

    def write(self, x, mynote=0):
        if DEBUG_TO_LOG_PROPER:
            self.result_for_log_proper.append(x)
        if not DEBUGINFO():
            return
        assert isinstance(x, str)
        if self.new_lines:
            if self.result:
                self.result.append("\n" * self.new_lines)
            self.result.append(self.indent_with * self.indentation)
            self.new_lines = 0
        x = "<span class=mynote%d>%s</span>" % (mynote, x)
        self.result.append(x)
        if DEBUGINFO_IMMEDIATE_PRINT:
            print(x)

    def _record_line_number(self, node):
        if node:
            msg = f"Line: {node.lineno} col_offset: {node.col_offset}"
            self.write(msg, mynote=2)  # 2 means red colour
            self.latest_lineno = node.lineno
            self.latest_col_offset = node.col_offset

            # 
            # Heavy debug point - comment out in production
            # 
            def get_source_code_line(lineno):
                return self.source_code_lines[lineno - 1].rstrip()
            def get_source_code_line_caret(col_offset):
                return f"{' ' * col_offset}^"
            log_proper.debug(get_source_code_line(node.lineno))
            log_proper.debug(get_source_code_line_caret(node.col_offset))

    def newline(self, node=None, extra=0):
        self._record_line_number(node)
        self.new_lines = max(self.new_lines, 1 + extra)

        # A
        self.flush()

    def body(self, statements):
        self.new_line = True
        self.indentation += 1
        for stmt in statements:
            self.visit(stmt)
        self.indentation -= 1

    # S
    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            self.newline()
            self.write("else:")
            self.body(node.orelse)

    # S
    def signature(self, node):
        want_comma = []

        def write_comma():
            if want_comma:
                self.write(", ")
            else:
                want_comma.append(True)

        padding = [None] * (len(node.args) - len(node.defaults))
        for arg, default in zip(node.args, padding + node.defaults):
            write_comma()
            self.visit(arg)
            if default is not None:
                self.write("=")
                self.visit(default)
        if node.vararg is not None:
            write_comma()
            self.write("*" + node.vararg)
        if node.kwarg is not None:
            write_comma()
            self.write("**" + node.kwarg)

    # S
    def decorators(self, node):
        for decorator in node.decorator_list:
            self.newline(decorator)
            self.write("@")
            self.visit(decorator)

    # Statements

    # A
    def visit_Module(self, node):
        self.write("\nvisit_Module ", mynote=1)

        # Dump source code to logh file
        self.logh.out_wrap_in_html(
            add_line_numbers(node.root.source_code),
            style_class="dump1",
            heading="Module Source Code...",
        )

        # Dump ast structure to logh file
        s = astpretty.pformat(node.root)  # .root is a property I added to each node of the ast tree
        if sys.version_info < (3, 0):
            s = s.encode("utf-8")  # unicode to str
        self.logh.out_wrap_in_html(
            s, style_class="dump_ast", heading="AST..."
        )  # better than self.write(s, mynote=1)

        self.generic_visit(node)  # need this to keep the visiting going...

        # After whole module is done...
        self.write("visit_Module complete", mynote=1)

    def visit_Assign(self, node):  # seems to be the top of the name / attr / chain
        self.write("\nvisit_Assign ", mynote=1)
        self.newline(node)

        for idx, target in enumerate(node.targets):
            if idx:
                self.write(", ")
            self.visit(target)

        self.write(" = ")

        # A
        self.lhs_recording = False  # are parsing the rhs now

        self.visit(node.value)  # node.value is an ast obj, can't print it

        # A
        self.made_assignment = True

    # S
    def visit_AugAssign(self, node):
        self.newline(node)
        self.visit(node.target)
        self.write(" " + BINOP_SYMBOLS[as_str(type(node.op))].replace("<", "&lt;") + "= ")
        self.visit(node.value)

    # S
    def visit_ImportFrom(self, node):
        self.newline(node)
        self.write("from %s%s import " % ("." * node.level, node.module))
        for idx, item in enumerate(node.names):
            if idx:
                self.write(", ")
            self.visit(item)

    # S
    def visit_Import(self, node):
        self.newline(node)

        # A
        self.made_import = True
        self.write("self.made_import = True", mynote=2)

        for item in node.names:
            self.write("import ")
            self.visit(item)

    def visit_Expr(self, node):
        # self.write("visit_Expr")
        self.detect_attribute_when_no_assignment(node)  # NEW July 2020
        self.newline(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.newline(extra=1)
        self.newline(node)
        self.write("\nvisit_FunctionDef\n", mynote=1)
        self.write("def %s(" % node.name)

        def has_property_decorator(node):
            """
            Determines if method 'node' has a property (get or set) decorator.
            
            node.decorator_list items can be one of two types of object:
                - Name          .id contains the decorator name e.g.
                                ['staticmethod', 'classmethod', 'abstractmethod', 'abc.abstractmethod', 'property']
                - Attribute     .attr contains the rhs of the decorator name e.g. for @myval.setter
                                ['setter']
                                .attr.value.id contains the lhs of the decorator e.g. 'myval'
                                Note that Attribute.value is an inner Name object.
            
            Typically a list of decorator id's might look like:
                ['staticmethod', 'classmethod', 'abstractmethod', 'abstractmethod', 'property', 'setter']

            For a @property getter the ast looks like:
                decorator_list=[Name(lineno=64, col_offset=5, id='property', ctx=Load())],

            For a @myval.setter the ast looks like:
                decorator_list=[
                    Attribute(
                        lineno=38,
                        col_offset=5,
                        value=Name(lineno=38, col_offset=5, id='myval', ctx=Load()),
                        attr='setter',
                        ctx=Load(),
                    ),

            :returns: bool
           """
            method_name = node.name
            for decorator in node.decorator_list:
                if hasattr(decorator, "id"):  # its a Name, look for getter
                    self.write(f" found decorator {decorator.id}", mynote=1)
                    if decorator.id == "property":
                        return True  # found the getter
                elif hasattr(decorator, "attr") and decorator.attr == 'setter':  # its an Attribute, setter, look for method_name
                    self.write(f" found decorator {decorator.attr}", mynote=1)
                    if hasattr(decorator, "value"):  # the inner Name
                        # ensure the Name object contains the same name as the method, just being cautious
                        name_obj = decorator.value
                        if hasattr(name_obj, "id") and name_obj.id == method_name:
                            return True  # found the setter
            return False


        # A
        if not self.current_class() and not self.am_inside_module_function():
            # assert node.name in self.quick_parse.quick_found_module_defs  # not always true cos quick parse isn't smart
            self.model.modulemethods.append(node.name)

        # look for decorator @property definition and treat method as property
        elif (
            self.treat_property_decorator_as_prop
            and self.current_class()
            and len(node.decorator_list)
            and has_property_decorator(node)
        ):
            self.current_class().AddAttribute(attrname=node.name, attrtype=["normal"])  # not sure why I had 'static' here in the past

        elif self.current_class():
            self.current_class().defs.append(node.name)

        self.scan_args_for_type_annotations(node)  # NEW July 2020

        # A
        self.push_a_function_or_method()

        self.write("):")
        self.body(node.body)

        # A
        self.flush()
        self.pop_a_function_or_method()

    # A - python 3.6
    def visit_AsyncFunctionDef(self, node):
        self.write("\nvisit_AsyncFunctionDef\n", mynote=1)
        self.visit_FunctionDef(node)  # just call the normal def

    def visit_ClassDef(self, node):
        self.newline(extra=2)
        # self.decorators(node)
        self.newline(node)

        self.write("\nvisit_ClassDef\n", mynote=1)
        self.write("class %s" % node.name)

        # A
        c = self.build_class_entry(node.name)

        for base in node.bases:
            self.visit(base)

            # A
            c.classesinheritsfrom.append(".".join(self.lhs))
            self.write(
                "classesinheritsfrom append %s cos lhs is %s" % (".".join(self.lhs), self.lhs)
            )
            self.lhs = []

        self.body(node.body)

        # A
        self.flush()
        self.stack_classes.pop()
        self.write(
            "  (pop a class) stack now: %s " % [str(c) for c in self.stack_classes], mynote=3
        )

    # S
    def visit_If(self, node):
        self.newline(node)
        self.write("if ")
        self.visit(node.test)
        self.write(":")
        self.body(node.body)
        while True:
            else_ = node.orelse
            if len(else_) == 1 and isinstance(else_[0], If):
                node = else_[0]
                self.newline()
                self.write("elif ")
                self.visit(node.test)
                self.write(":")
                self.body(node.body)
            else:
                if len(else_) > 0:
                    self.newline()
                    self.write("else:")
                    self.body(else_)
                break

    # S
    def visit_For(self, node):
        self.newline(node)
        self.write("for ")
        self.visit(node.target)
        self.write(" in ")
        self.visit(node.iter)
        self.write(":")
        self.body_or_else(node)

    # S
    def visit_While(self, node):
        self.newline(node)
        self.write("while ")
        self.visit(node.test)
        self.write(":")
        self.body_or_else(node)

    # S
    def visit_With(self, node):
        self.newline(node)
        self.write("with ")

        if hasattr(node, "items"):  # must be a python 3 ast
            for withitem in node.items:
                if withitem.optional_vars:
                    self.visit(withitem.context_expr)
                    self.write(" as ")
                    self.visit(withitem.optional_vars)
        else:
            self.visit(node.context_expr)
            if node.optional_vars:
                self.write(" as ")
                self.visit(node.optional_vars)

        self.write(":")
        self.body(node.body)

    # S
    def visit_Pass(self, node):
        self.newline(node)
        self.write("pass")
        # raise RuntimeError("fake exception in AST visitor for testing purposes - comment this out!")

    # S
    def visit_Print(self, node):
        # XXX: python 2.6 only
        self.newline(node)
        self.write("print ")
        want_comma = False
        if node.dest is not None:
            self.write(" >> ")
            self.visit(node.dest)
            want_comma = True
        for value in node.values:
            if want_comma:
                self.write(", ")
            self.visit(value)
            want_comma = True
        if not node.nl:
            self.write(",")

    # S
    def visit_Delete(self, node):
        self.newline(node)
        self.write("del ")
        for idx, target in enumerate(node.targets):
            if idx:
                self.write(", ")
            self.visit(target)

    # S
    def visit_TryExcept(self, node):
        self.newline(node)
        self.write("try:")
        self.body(node.body)
        for handler in node.handlers:
            self.visit(handler)

    # S
    def visit_TryFinally(self, node):
        self.newline(node)
        self.write("try:")
        self.body(node.body)
        self.newline(node)
        self.write("finally:")
        self.body(node.finalbody)

    if sys.version_info >= (3, 5):  # A

        def visit_Try(self, node):
            self.newline(node)
            self.write("try:")
            self.body(node.body)
            for handler in node.handlers:
                self.visit(handler)

    # S
    def visit_Global(self, node):
        self.newline(node)
        self.write("global " + ", ".join(node.names))

    # S
    def visit_Nonlocal(self, node):
        self.newline(node)
        self.write("nonlocal " + ", ".join(node.names))

    # S
    def visit_Return(self, node):
        self.newline(node)
        if node.value is not None:
            self.write("return ")
            self.visit(node.value)
        else:
            self.write("return")

    # S
    def visit_Break(self, node):
        self.newline(node)
        self.write("break")

    # S
    def visit_Continue(self, node):
        self.newline(node)
        self.write("continue")

    # S
    def visit_Raise(self, node):
        # XXX: Python 2.6 / 3.0 compatibility
        self.newline(node)
        self.write("raise")
        if hasattr(node, "exc") and node.exc is not None:
            self.write(" ")
            self.visit(node.exc)
            if node.cause is not None:
                self.write(" from ")
                self.visit(node.cause)
        elif hasattr(node, "type") and node.type is not None:
            self.visit(node.type)
            if node.inst is not None:
                self.write(", ")
                self.visit(node.inst)
            if node.tback is not None:
                self.write(", ")
                self.visit(node.tback)

    # Expressions

    # A
    def visit_AnnAssign(self, node):

        def scan_assignment_for_type_annotations(node):
            if hasattr(node, "annotation") and node.annotation != None:

                # All the cases are listed https://docs.python.org/3/library/ast.html#ast.AnnAssign 
                # we only handle a subset as minimally as possible, should enhance
                annotation_id = 'UnknownType'
                if hasattr(node.annotation, 'id'):
                    annotation_id = node.annotation.id
                else:
                    if hasattr(node.annotation, 'slice'):
                        if hasattr(node.annotation.slice, 'value'): # <= python 3.8 and under
                            if hasattr(node.annotation.slice.value, 'id'):
                                annotation_id = node.annotation.slice.value.id
                        else:
                            if hasattr(node.annotation.slice, 'id'): # >= python 3.9 
                                annotation_id = node.annotation.slice.id

                self.write(f" found type annotation '{annotation_id}' on assignment to {_to_full_var}", mynote=2)
                if self.current_class():
                    self.add_composite_dependency((_to, annotation_id))
                else:
                    pass  # should add to module dependencies (supported by GitUML only, at the moment)

        def nice_target_name(target) -> str:
            # target typically has .value.id and .attr
            try:
                if isinstance(target, ast.Attribute):
                    return f"{target.value.id}.{target.attr}"
                elif isinstance(target, ast.Name):
                    return f"{target.id}"
                else:
                    return "self.pynsource_parse_error_var"  # hack to avoid parse failures
            except AttributeError as e:
                return "self.pynsource_parse_error"  # hack to avoid parse failures
        _to_full_var = nice_target_name(node.target)
        _to = _to_full_var.split('.')[-1]

        self.write(f"\nvisit_AnnAssign {_to_full_var}\n", mynote=1)
        self.newline(node)

        scan_assignment_for_type_annotations(node)

        # The following logic directly copied from 'visit_Assign' - but adjusted since can't have
        # multiple lhs when using type annotations. Also have to guard against None (see explanation).
        self.visit(node.target)

        self.write(" = ")

        # A
        self.lhs_recording = False  # are parsing the rhs now

        """Have to protect against AnnAssign.value (the value being assigned) being None when 
        parsing "self.fred: Fred" whereas when parsing "self.fred: Fred = None" AnnAssign.value 
        is NameConstant(value=None) thus CAN be visited. Note that compared to the normal 
        Assign.value node parsing (see visit_Assign method) when parsing "self.fred = None" 
        Assign.value is a nice NameConstant(value=None) thus CAN be visited whereas when parsing 
        "self.fred" where you might think the dangerous situation of Assign.value being None will 
        arise, funnily enough it doesn't because the Python AST parser handles this syntax using 
        visit_Expr instead. 
        
        ------------------------------|------------------------------------------------------
        Expression                    | AnnAssign.value (type annotation assignment AST node)
        ------------------------------|------------------------------------------------------
            self.fred: Fred             None                        <- guard against
            self.fred: Fred = None      NameConstant(value=None)
            
                                      |------------------------------------------------------
                                      | Assign.value (traditional assignment AST node)
                                      |------------------------------------------------------
            self.fred                   n/a                     <- is parsed via visit_Expr instead
            self.fred = None            NameConstant(value=None)
            
        """
        if node.value:  # have to guard against None here but not in visit_Assign (see explanation above)
            self.visit(node.value)  # node.value is an ast obj, can't print it

        # A
        self.made_assignment = True
        self.flush()  # this fixes the old bug where x = 100 on a line by itself in a module didn't get a variable created unless there was a statement following it

    def visit_Attribute(self, node):
        self.visit(node.value)

        # A
        self.write("\nvisit_Attribute %s\n" % node.attr, mynote=1)
        self.record_lhs_rhs(node.attr)

        self.write("." + node.attr)

    def visit_Call(self, node):
        """
            class Call(func, args, keywords, starargs, kwargs)  -  See the WONDERFUL DOCO http://greentreesnakes.readthedocs.io/en/latest/nodes.html
            Thus in our visitor here, 'node' has those same parameters, but as properties e.g. node.func, node.args etc.

            Update: In Python 3.5 Instead of starargs, Starred nodes can now appear in args, and kwargs is replaced by
            keyword nodes in keywords for which arg is None.
            """
        self.visit(node.func)
        self.write("\nvisit_Call %s" % self.rhs, mynote=1)

        # A
        self.detect_append_or_rhs_call()
        if self.stop_recording_rhs_inside_first_bracket != None:
            self.stop_recording_rhs_inside_first_bracket += 1
            self.write(
                "stop_recording_rhs_inside_first_bracket INCREMENTED %s"
                % self.stop_recording_rhs_inside_first_bracket,
                mynote=1,
            )

        self.write("(")
        for arg in node.args:
            # write_comma()
            self.visit(arg)
        for keyword in node.keywords:
            # write_comma()
            self.write(
                (keyword.arg if keyword.arg else "None (no keyword arg)") + "="
            )  # TODO is this if/else fix related to python 3 node.kwargs handling? Only get None when parsing with python3 - see test 'test_star_star_params_pyth3'
            self.visit(keyword.value)

        if sys.version_info >= (3, 5):  # A
            # A
            pass  # TODO handle this properly viz. Starred nodes can now appear in args, and kwargs is replaced by keyword nodes in keywords for which arg is None.  See the WONDERFUL DOCO http://greentreesnakes.readthedocs.io/en/latest/nodes.html
        else:
            if node.starargs is not None:
                # write_comma()
                self.write("*")
                self.visit(node.starargs)
            if node.kwargs is not None:
                # write_comma()
                self.write("**")
                self.visit(node.kwargs)
        self.write(")")

        # A
        if self.stop_recording_rhs_inside_first_bracket != None:
            self.stop_recording_rhs_inside_first_bracket -= 1
            self.write(
                "stop_recording_rhs_inside_first_bracket decremented %s"
                % self.stop_recording_rhs_inside_first_bracket,
                mynote=1,
            )

    # A
    def detect_append_or_rhs_call(self):
        # Ensure self.made_append_call and self.made_rhs_call are different things.
        #
        # An append call does not necessarily imply a rhs call was made.
        # e.g. .append(blah) or .append(10) are NOT a calls on the rhs, in
        # fact there is no rhs clearly defined yet except till inside the
        # append(... despite it superficially looking like a function call
        #

        # Detect append call at module level - NEW
        if (
            len(self.lhs) == 2
            and not self.current_class()
            and self.lhs[1] in ("append", "add", "insert")
            and not self.rhs
        ):
            self.lhs_recording = False  # start recording tokens (names, attributes) on rhs
            self.made_append_call = True

            self.write("\n just_now_made_append_call (module level)", mynote=1)

        # Detect append call
        elif (
            len(self.lhs) == 3
            and self.in_method_in_class_area()
            and self.lhs[0] == "self"
            and self.lhs[2] in ("append", "add", "insert")
            and not self.rhs
        ):
            self.lhs_recording = False  # start recording tokens (names, attributes) on rhs
            self.made_append_call = True

            self.write("\n just_now_made_append_call", mynote=1)

        # Detect normal rhs call
        elif len(self.rhs) > 0:
            if not self.made_rhs_call:
                self.write("FIRST BRACKET %s len is %d" % (self.rhs, len(self.rhs)), mynote=1)
                self.pos_rhs_call_pre_first_bracket = (
                    len(self.rhs) - 1
                )  # remember which is the token before the first bracket

                self.stop_recording_rhs_inside_first_bracket = 1
                self.write("stop_recording_rhs_inside_first_bracket INITIAL SET to 1", mynote=1)

            self.made_rhs_call = True

    def visit_Name(self, node):
        self.write("\nvisit_Name %s\n" % node.id, mynote=1)
        self.write(node.id)

        # A
        self.record_lhs_rhs(node.id)

    # Cos Python 3.8 reports: PendingDeprecationWarning: visit_Str is deprecated; add visit_Constant
    if sys.version_info.minor >= 8:
        def visit_Constant(self, node):
            self.write(repr(node.s))
    else:
        def visit_Str(self, node):
            self.write(repr(node.s))

    # S
    def visit_Bytes(self, node):
        self.write(repr(node.s))

    def visit_Num(self, node):
        self.write(repr(node.n))

    # S
    def visit_Tuple(self, node):
        self.write("(")
        idx = -1
        for idx, item in enumerate(node.elts):
            if idx:
                self.write(", ")
            self.visit(item)
        self.write(idx and ")" or ",)")

    # S
    def sequence_visit(left, right):
        def visit(self, node):
            self.write(left)
            for idx, item in enumerate(node.elts):
                if idx:
                    self.write(", ")
                self.visit(item)
            self.write(right)

        return visit

    # S
    visit_List = sequence_visit("[", "]")
    visit_Set = sequence_visit("{", "}")
    del sequence_visit

    # S
    def visit_Dict(self, node):
        self.write("{")

        # Skip visiting inside the dictionary - no point getting confused by syntax like
        #     "varin = {**self.optStruct['ModelVars'], **data}"
        # all we want are big picture classes, functions, methods etc.
        # 
        # for idx, (key, value) in enumerate(zip(node.keys, node.values)):
        #     if idx:
        #         self.write(", ")
        #     self.visit(key)
        #     self.write(": ")
        #     self.visit(value)
        
        self.write("}")

    # S
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.write(" %s " % BINOP_SYMBOLS[as_str(type(node.op))].replace("<", "&lt;"))
        self.visit(node.right)

    # S
    def visit_BoolOp(self, node):
        self.write("(")
        for idx, value in enumerate(node.values):
            if idx:
                self.write(" %s " % BOOLOP_SYMBOLS[as_str(type(node.op))])
            self.visit(value)
        self.write(")")

    # S
    def visit_Compare(self, node):
        self.write("(")
        self.visit(node.left)
        for op, right in zip(node.ops, node.comparators):
            self.write(" %s " % CMPOP_SYMBOLS[as_str(type(op))].replace("<", "&lt;"))
            self.visit(right)
        self.write(")")

    # S
    def visit_UnaryOp(self, node):
        self.write("(")
        op = UNARYOP_SYMBOLS[as_str(type(node.op))]
        self.write(op)
        if op == "not":
            self.write(" ")
        self.visit(node.operand)
        self.write(")")

    # S
    def visit_Subscript(self, node):
        self.visit(node.value)
        self.write("[")
        self.visit(node.slice)
        self.write("]")

    # S
    def visit_Slice(self, node):
        if node.lower is not None:
            self.visit(node.lower)
        self.write(":")
        if node.upper is not None:
            self.visit(node.upper)
        if node.step is not None:
            self.write(":")
            if not (isinstance(node.step, Name) and node.step.id == "None"):
                self.visit(node.step)

    # S
    def visit_ExtSlice(self, node):
        for idx, item in enumerate(node.dims):  # ANDY added enumerate
            if idx:
                self.write(", ")
            self.visit(item)

    # S
    def visit_Yield(self, node):
        self.write("yield ")
        if node.value:  # may not be returning a value from yield
            self.visit(node.value)

    # S
    def visit_Lambda(self, node):
        self.write("lambda ")
        self.signature(node.args)
        self.write(": ")
        self.visit(node.body)

    # S
    def visit_Ellipsis(self, node):
        self.write("Ellipsis")

    # S
    def generator_visit(left, right):
        def visit(self, node):
            self.write(left)
            self.visit(node.elt)
            for comprehension in node.generators:
                self.visit(comprehension)
            self.write(right)

        return visit

    # S
    visit_ListComp = generator_visit("[", "]")
    visit_GeneratorExp = generator_visit("(", ")")
    visit_SetComp = generator_visit("{", "}")
    del generator_visit

    # S
    def visit_DictComp(self, node):
        self.write("{")
        self.visit(node.key)
        self.write(": ")
        self.visit(node.value)
        for comprehension in node.generators:
            self.visit(comprehension)
        self.write("}")

    # S
    def visit_IfExp(self, node):
        self.visit(node.body)
        self.write(" if ")
        self.visit(node.test)
        self.write(" else ")
        self.visit(node.orelse)

    # S
    def visit_Starred(self, node):
        self.write("*")
        self.visit(node.value)

    # S
    def visit_Repr(self, node):
        # XXX: python 2.6 only
        self.write(
            """)
            self.visit(node.value)
            self.write("""
        )

    # Helper Nodes

    # A
    def visit_alias(self, node):
        self.write(node.name)
        if node.asname is not None:
            self.write(" as " + node.asname)

        # A
        if self.made_import:
            if node.asname is not None:
                self.imports_encountered.append(node.asname)
            else:
                self.imports_encountered.append(node.name)

    # S
    def visit_comprehension(self, node):
        self.write(" for ")
        self.visit(node.target)
        self.write(" in ")
        self.visit(node.iter)
        if node.ifs:
            for if_ in node.ifs:
                self.write(" if ")
                self.visit(if_)

    # S
    def visit_ExceptHandler(self, node):
        self.newline(node)
        self.write("except")
        if node.type is not None:
            self.write(" ")
            self.visit(node.type)
            if node.name is not None:
                self.write(f" as {node.name}")  # no need to  self.visit(node.name)
                # This code breaks with python >= 3.8 which uses regular built in ast
                # s = repr(type(node)).replace("typed_ast.", "")
                # if "_ast27." in s or "_ast." in s:
                #     self.visit(node.name)  # Name object, in Python 2
                # else:
                #     self.write(
                #         node.name
                #     )  # Name is a str in Python 3, don't visit the 'as xxxx' tree if python3, cos haven't figured out the new tree yet, plus no reason to?
        self.write(":")
        self.body(node.body)

    # Util methods re assignment and type annotation - July 2020, Dec 2021

    def scan_args_for_type_annotations(self, node):
        """
        Called from visit_Func - parse the arguments to the function/method for type annotations
        Within the for loop:
            for arg in node.args.args:
                At this point, for the Python syntax:
                "func(param)"      arg.arg is "param" and arg.annotation is None
                "func(param: A)"   arg.arg is "param" and arg.annotation is decoded into the nice "A"
                "func(param: A.B)" arg.arg is "param" and arg.annotation is decoded into the nice "A.B" etc.
        """
        for arg in node.args.args:
            if hasattr(arg, "annotation") and arg.annotation != None:
                try:
                    _type = self.annotation_to_string(arg.annotation)
                except (AttributeError, AssertionError) as e:
                    log_proper.exception(f"Error parsing type annotation for parameter {arg.arg}")
                    _type = 'UnknownType'
                self.write(f" found type annotation '{_type}' on method parameter {arg.arg}", mynote=1)

                if self.current_class():
                    self.add_composite_dependency((arg.arg, _type))
                else:
                    pass  # should add to module dependencies (supported by GitUML only, at the moment)
    
    def annotation_to_string(self, annotation):
        # Generalised, recursive drilling down to construct and return annotation string
        # should handle any type of nested string annotation e.g. "A" or "A.B" or "A.B.C" etc.
        assert annotation is not None
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            result = self.annotation_to_string(annotation.value)  # recurse
            return f"{result}.{annotation.attr}"
        else:
            # Not a type with a juicy name - we have likely encountered a Python BUILT_IN_TYPE
            # a: Optional[str] or b: Sequence[int] etc.
            return annotation.value.id  # e.g. 'Optional' or 'Sequence' etc.

    def detect_attribute_when_no_assignment(self, node):
        """
        Called from an visit_Expr - normally we don't parse expressions at all, however this meant lone
        attribute declarations like `self.fred` were being missed.  This function picks up on this case.

        body=[
            Expr(          <- node
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
        if hasattr(node, "value") and isinstance(node.value, ast.Attribute) and hasattr(node.value, 'attr'):
            attr_name = node.value.attr
            if self.current_class():
                self.write(f" attribute '{attr_name}' without assignment - created!", mynote=2)
                # TODO AddAttribute() won't create duplicates, will add extra attrtypes, but unfortunately won't update an 
                # existing attrtype - which may mean that a "many" detected later via .append() won't replace a "normal" -  fix
                self.current_class().AddAttribute(attrname=attr_name, attrtype=["normal"])
            else:
                pass  # should create attribute in Module (currently GitUML only)

    # END Util methods


    # Note
    # S means this code is uneccesary for 99% of extraction of info I want.  I only put it in to stop some errors re huge accumulating rhs
    # A means Andy's extra bits of code


def mode(python=0):
    """
    Switch parser mode to deal with python 2 or 3 syntax.


    :param python: 0 means use native Python ast, 2 or 3 means use typed_ast (which only works in Python 3)
    :return: -
    """
    global ast, last_python_mode
    if python == 3:
        assert sys.version_info >= (3, 0)
        # print('mode 3')
        ast = typed_ast.ast3

        # Fix the fact that typed ast can't parse fstring variables and other 3.8 syntax
        # We revert to the built in ast which is ok.
        # NOTE: The official word on this is: https://github.com/python/typed_ast
        # typed_ast will not be updated to support parsing Python 3.8 and newer.
        # Instead, it is recommended to use the stdlib ast module there, which
        # has been augmented to support extracting type comments and has limited
        # support for parsing older versions of Python 3.
        if sys.version_info[1] >= 8:
            log_proper.debug(f"using native ast cos python 3.8 or above")
            ast = ast_native

    elif python == 2:
        assert sys.version_info >= (3, 0)
        # print('mode 2')
        ast = typed_ast.ast27
    else:
        # print('Warning - running in python native mode')
        ast = ast_native

    Visitor.__bases__ = (ast.NodeVisitor,)
    astpretty.ast = ast  # monkey patch the ast away from built in python to typed_ast
    last_python_mode = python


mode(0)
