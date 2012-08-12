"""
Compare old and new parsing

Old Parser results model structure:
-----------------------------------

model
    .classlist {classname, classentry ...} where classentry is
        .ismodulenotrealclass T/F
        .classdependencytuples [(fromclass, toclass), ...]
        .classesinheritsfrom [class, ...]  # todo should be renamed classinheritsfrom (singular)
        .attrs [attrobj, ...]
                .attrname
                .attrtype []  # todo should be renamed attrtypes plural
                .compositedependencies  # todo (calculated in real time, should precalc)
        .defs [method, ...]
    .modulemethods = [method, ...]]
"""

import ast
import traceback
import difflib
import os

import sys
sys.path.append("../../src")
from architecture_support import whosdaddy, whosgranddaddy
from core_parser import ClassEntry, Attribute
from keywords import pythonbuiltinfunctions

from logwriter import LogWriter

log = None

DEBUGINFO = 1
DEBUGINFO_IMMEDIATE_PRINT = 0
LOG_TO_CONSOLE = 0
STOP_ON_EXCEPTION = 0

def dump_old_structure(pmodel):
    res = ""
    
    # TODO build this into ClassEntry
    def calc_classname(classentry):
        if classentry.name_long:
            return classentry.name_long
        else:
            return classentry.name
        
    # repair old parse models #TODO build this into the old parser so that we don't have to do this
    for classname, classentry in  pmodel.classlist.items():
        classentry.name = classname
    
    for classname, classentry in  sorted(pmodel.classlist.items(), key=lambda kv: calc_classname(kv[1])):
        res += "%s (is module=%s) inherits from %s class dependencies %s\n" % \
                                    (calc_classname(classentry),
                                     classentry.ismodulenotrealclass,
                                     classentry.classesinheritsfrom,
                                     classentry.classdependencytuples)
        for attrobj in classentry.attrs:
            res += "    %-20s (attrtype %s)\n" % (attrobj.attrname,
                                            attrobj.attrtype) # currently skip calc of self._GetCompositeCreatedClassesFor(attrobj.attrname), arguably it should be precalculated and part of the data structure
        for adef in classentry.defs:
            res += "    %s()\n" % adef
    res += "    modulemethods %s\n" % (pmodel.modulemethods)
    return res
    
def old_parser(filename):
    import sys
    sys.path.append("../../src")
    from generate_code.gen_asciiart import PySourceAsText
    
    p = PySourceAsText()
    p.Parse(filename)
    return p

def ast_parser(filename):
    with open(filename,'r') as f:
        source = f.read()
    
    node = ast.parse(source)
    #print ast.dump(node)
    return node


def convert_ast_to_old_parser(node, filename):
    
    class OldParseModel(object):
        def __init__(self):
            self.classlist = {}
            self.modulemethods = []
            
    class Visitor(ast.NodeVisitor):
        
        def __init__(self, quick_parse):
            self.model = OldParseModel()
            self.stack_classes = []
            self.stack_module_functions = [False]
            self.quick_parse = quick_parse
            self.init_lhs_rhs()
            
            self.result = []
            self.indent_with = ' ' * 4
            self.indentation = 0
            self.new_lines = 0

        def init_lhs_rhs(self):
            self.lhs = []
            self.rhs = []
            self.lhs_recording = True
            self.made_rhs_call = False
            self.made_assignment = False
            self.made_append_call = False

        def record_lhs_rhs(self, s):
            if self.lhs_recording:
                self.lhs.append(s)
                self.write("\nLHS %d %s\n" % (len(self.lhs), self.lhs), mynote=2)
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

        def write(self, x, mynote=0):
            assert(isinstance(x, str))
            if self.new_lines:
                if self.result:
                    self.result.append('\n' * self.new_lines)
                self.result.append(self.indent_with * self.indentation)
                self.new_lines = 0
            x = "<span class=mynote%d>%s</span>" % (mynote,x)
            self.result.append(x)
            if DEBUGINFO_IMMEDIATE_PRINT:
                print x

        def build_class_entry(self, name):
            c = ClassEntry(name)
            self.model.classlist[name] = c
            self.stack_classes.append(c)
            c.name_long = "_".join([str(c) for c in self.stack_classes])
            self.write("  (inside class %s) %s " % (c.name, [str(c) for c in self.stack_classes]), mynote=3)
            return c

        def add_composite_dependency(self, t):
            if t not in self.current_class().classdependencytuples:
                self.current_class().classdependencytuples.append(t)
                
        def flush_state(self, msg=""):
            self.write("""
                <table>
                    <tr>
                        <th>lhs</th>
                        <th>rhs</th>
                        <th>made_assignment</th>
                        <th>made_append_call</th>
                        <th>made_rhs_call</th>
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
                    </tr>
                </table>
            """ % (self.lhs, self.rhs,
                    self.made_assignment,
                    self.made_append_call,
                    self.made_rhs_call,
                    self.in_class_static_area(),
                    self.in_method_in_class_area(),
                    msg), mynote=0)

        def flush(self):
            self.flush_state(whosgranddaddy())
            
            # At this point we have both lhs and rhs plus three flags and can
            # make a decision about what to create.
        
            def is_rhs_reference_to_a_class(rhs):
                
                assert len(self.rhs) > 0
                
                # Scenarios:
                #
                # ... = Blah()
                # ...append(Blah())  RHS CALL MADE but whether its from the append or the Blah we don't know
                #
                # ... = blah        may be reinterpreted as      = Blah()  if Blah class found - a relaxed rule I admit
                # ...append(blah)   may be reinterpreted as append(Blah()) if Blah class found - a relaxed rule I admit
                #
                # ... = 10          won't get here because no rhs
                # ...append(10)     won't get here because no rhs
                #
                def relaxed_is_instance_a_known_class(t):
                    self.write("checking to see if '%s' is relaxed_is_instance_a_known_class" % t, mynote=2)
                    for c in self.quick_parse.quick_found_classes:
                        if t.lower() == c.lower():
                            self.write("Yes t.lower() %s == c.lower() %s" % (t.lower(), c.lower()), mynote=2)
                            return True, c  # return proper class name not the instance
                    self.write("No", mynote=2)
                    return False, t
                
                res, rhs = relaxed_is_instance_a_known_class(rhs)
                if res:
                    return True, rhs
                
                # Make sure the rhs is a class NOT a function. Usually its a
                # class creation call or a relaxed ref to a class (see above)
                #
                # Also avoid case of self being on the rhs and being considered the first rhs token
                #
                #   self.curr.append(" "*self.curr_width)
                #
                if self.made_rhs_call and rhs not in pythonbuiltinfunctions and rhs not in self.model.modulemethods and rhs != 'self':
                    self.write("rhs %s IS is_rhs_reference_to_a_class" % rhs, mynote=2)
                    return True, rhs

                self.write("rhs %s is NOT is_rhs_reference_to_a_class" % rhs, mynote=2)
                return False, rhs
            
            def create_attr_static(t):
                self.current_class().AddAttribute(attrname=t, attrtype=['static'])
                return t
            def create_attr(t):
                if (t == '__class__') and len(self.lhs) >= 3:
                    t = self.lhs[2]
                    self.current_class().AddAttribute(attrname=t, attrtype=['static'])
                else:
                    self.current_class().AddAttribute(attrname=t, attrtype=['normal'])
                return t
            def create_attr_many(t):
                self.current_class().AddAttribute(attrname=t, attrtype=['normal', 'many'])
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
                elif self.in_method_in_class_area() and self.lhs[0] == 'self':
                    t = create_attr_please(self.lhs[1])
                else:
                    pass # in module area
                        
                if self.lhs[0] == 'self' and len(self.rhs) > 0:
                    res, rhs = is_rhs_reference_to_a_class(self.rhs[0])
                    if res:
                        self.add_composite_dependency((t, rhs))
                        
            self.init_lhs_rhs()
            self.flush_state()
            self.write("<hr>", mynote=2)

        
        
        # MAIN VISIT METHODS
        
        def newline(self, node=None, extra=0):
            self.new_lines = max(self.new_lines, 1 + extra)

            # A
            self.flush()

        def body(self, statements):
            self.new_line = True
            self.indentation += 1
            for stmt in statements:
                self.visit(stmt)
            self.indentation -= 1
        
        def visit_ClassDef(self, node):
            self.newline(extra=2)
            #self.decorators(node)
            self.newline(node)
            
            self.write("\nvisit_ClassDef\n", mynote=1)
            self.write('class %s' % node.name)
            
            # A
            c = self.build_class_entry(node.name)

            for base in node.bases:
                self.visit(base)

                # A
                c.classesinheritsfrom.append(".".join(self.lhs))
            
            self.body(node.body)

            # A
            self.flush()
            self.stack_classes.pop()
            self.write("  (pop a class) stack now: %s " % [str(c) for c in self.stack_classes], mynote=3)
            
        def visit_FunctionDef(self, node):
            self.newline(extra=1)
            self.newline(node)
            self.write("\nvisit_FunctionDef\n", mynote=1)
            self.write('def %s(' % node.name)
            
            # A
            if not self.current_class() and not self.am_inside_module_function():
                self.model.modulemethods.append(node.name)
                assert node.name in self.quick_parse.quick_found_module_defs
            elif self.current_class():
                self.current_class().defs.append(node.name)

            # A
            self.push_a_function_or_method()
            
            self.write('):')
            self.body(node.body)
            
            # A
            self.flush()
            self.pop_a_function_or_method()
            
        def visit_Assign(self, node):  # seems to be the top of the name / attr / chain
            self.write("\nvisit_Assign ", mynote=1)
            self.newline(node)
            
            for idx, target in enumerate(node.targets):
                if idx:
                    self.write(', ')
                self.visit(target)

            self.write(' = ')
            
            # A
            self.lhs_recording = False  # are parsing the rhs now
            
            self.visit(node.value)  # node.value is an ast obj, can't print it
            
            # A
            self.made_assignment = True

        def visit_Call(self, node):
            self.visit(node.func)
            self.write("\nvisit_Call %s" % self.rhs, mynote=1)

            # A
            just_now_made_append_call = False
            if len(self.lhs) == 3 and \
                    self.in_method_in_class_area() and \
                    self.lhs[0] == 'self' and \
                    self.lhs[2] in ('append', 'add', 'insert') and \
                    not self.rhs:
                self.lhs_recording = False # start recording tokens (names, attrs) on rhs
                self.made_append_call = just_now_made_append_call = True
                self.write("\n just_now_made_append_call", mynote=1)
                
            self.write('(')
            for arg in node.args:
                #write_comma()
                self.visit(arg)
            for keyword in node.keywords:
                #write_comma()
                self.write(keyword.arg + '=')
                self.visit(keyword.value)
            if node.starargs is not None:
                #write_comma()
                self.write('*')
                self.visit(node.starargs)
            if node.kwargs is not None:
                #write_comma()
                self.write('**')
                self.visit(node.kwargs)
            self.write(')')

            # A
            # Ensure self.made_append_call and self.made_rhs_call are different things.
            #
            # An append call does not necessarily imply a rhs call was made.
            # e.g. .append(blah) or .append(10) are NOT a calls on the rhs, in
            # fact there is no rhs clearly defined yet except till inside the
            # append(... despite it superficially looking like a function call
            #               
            if len(self.rhs) > 0 and not just_now_made_append_call:
                self.made_rhs_call = True
               
        def visit_Name(self, node):
            self.write("\nvisit_Name %s\n" % node.id, mynote=1)
            self.write(node.id)

            # A
            self.record_lhs_rhs(node.id)

        def visit_Attribute(self, node):
            self.visit(node.value)
            
            # A
            self.write("\nvisit_Attribute %s\n" % node.attr, mynote=1)
            self.record_lhs_rhs(node.attr)
            
            self.write('.' + node.attr)

        def visit_Str(self, node):
            self.write(repr(node.s))

        def visit_Num(self, node):
            self.write(repr(node.n))

        def visit_Expr(self, node):
            #self.write("visit_Expr")
            self.newline(node)
            self.generic_visit(node)
    
    class QuickParse(object):
        def __init__(self, filename):
            import re   
            # secret regular expression based preliminary scan for classes and module defs
            # Feed the file text into findall(); it returns a list of all the found strings
            with open(filename, 'r') as f:
                source = f.read()
            self.quick_found_classes = re.findall(r'^\s*class (.*?)[\(:]', source, re.MULTILINE)  
            self.quick_found_module_defs = re.findall(r'^def (.*)\(.*\):', source, re.MULTILINE)
            self.quick_found_module_attrs = re.findall(r'^(\S.*?)[\.]*.*\s*=.*', source, re.MULTILINE)
            
            log.out_wrap_in_html("quick_found_classes %s<br>quick_found_module_defs %s<br>quick_found_module_attrs %s<br>" % \
                                (self.quick_found_classes, self.quick_found_module_defs, self.quick_found_module_attrs),
                                style_class='quick_findings')

    
    qp = QuickParse(filename)

    v = Visitor(qp)
    
    try:
        v.visit(node)
    except Exception as err:
        log.out("Parsing Visit error: {0}".format(err), force_print=True)
        log.out_wrap_in_html(traceback.format_exc(), style_class='stacktrace')
        if STOP_ON_EXCEPTION:
            if DEBUGINFO:
                debuginfo = '<br>'.join(v.result)
                log.out(debuginfo)
                log.out_html_footer()
                log.finish()
            raise

    debuginfo = '<br>'.join(v.result)
    return v.model, debuginfo


#####

def parse_and_convert(in_filename, print_diffs=True):
    global log
    log = LogWriter(in_filename, print_to_console=LOG_TO_CONSOLE)
    
    def oldparse():
        model = old_parser(in_filename)
        d1 = dump_old_structure(model)
        log.out_wrap_in_html(d1, style_class='dump1')
        return d1
        
    def newparse():
        node = ast_parser(in_filename)
        model, debuginfo = convert_ast_to_old_parser(node, in_filename)
        d2 = dump_old_structure(model)
        log.out_wrap_in_html(d2, style_class='dump1')
        return d2, debuginfo

    def dodiff(d1, d2):
        diff = difflib.ndiff(d1.splitlines(1),d2.splitlines(1))
        diff_s = ''.join(diff)
        return diff_s
    
    try:
        log.out_html_header()
        log.out("PARSING: %s *****\n" % in_filename)
        
        d1 = oldparse()
        log.out_divider()
        d2, debuginfo = newparse()
        
        comparedok = (d1 == d2)
        log.out("** old vs new method comparison = %s" % comparedok)

        diff_s = dodiff(d1, d2)
        log.out_wrap_in_html(diff_s, style_class='dumpdiff')
        if not comparedok and print_diffs:
            print diff_s

        if DEBUGINFO:
            log.out(debuginfo)
    
        log.out_html_footer()
    finally:
        log.finish()
        
    return comparedok


############        

RUN_TEST_SUITE = 1

results = []
def reset_tests():
    global results
    results = []
def test(filename):
    results.append(parse_and_convert(filename))
def test_not(filename):
    results.append(not parse_and_convert(filename, print_diffs=False))
def report(msg):
    if all(results):
        print "%s OK" % msg
    else:
        print "oooops %s broken" % msg, results

if RUN_TEST_SUITE:
    reset_tests()    
    test('../../tests/python-in/testmodule01.py')
    test('../../tests/python-in/testmodule02.py')
    test('../../tests/python-in/testmodule03.py')
    test('../../tests/python-in/testmodule04.py')
    test('../../tests/python-in/testmodule05.py') # (inner classes)
    test('../../tests/python-in/testmodule06.py')
    test('../../tests/python-in/testmodule07.py')
    test('../../tests/python-in/testmodule66.py')
    report("official parsing tests")
    
    reset_tests()    
    test('../../src/printframework.py')
    test('../../src/asciiworkspace.py')
    report("subsidiary parsing tests")
    
    # Expect these to fail cos ast parsing is genuinely better
    reset_tests()    
    test_not('../../tests/python-in/testmodule08_multiple_inheritance.py') # ast is better (base classes with .)
    test_not('../../src/pynsource.py') # ast is better (less module methods found - more correct)
    report("ast parsing is genuinely better")

    # Extras
    print

#print parse_and_convert('../../src/pyNsourceGui.py') # different - to investigate
#print parse_and_convert('../../src/command_pattern.py') # ast is better, nested module functions ignored. class checked for when relaxed attr ref to instance

"""
TODO

handle properties
    currentItem = property(_get_current_item)
    currentRedoItem = property(_get_current_redo_item)
    maxItems = property(_get_max_items, _set_max_items)
currently appearing as static attrs - which is ok.  Should be normal attra.


"""
