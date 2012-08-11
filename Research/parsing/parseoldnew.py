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

import sys
sys.path.append("../../src")
from architecture_support import whosdaddy, whosgranddaddy
import os

import traceback

DEBUG = 1
DEBUG_WRITE = 0

def dump_old_structure(pmodel):
    res = ""
    for classname, classentry in pmodel.classlist.items():
        res += "%s (is module=%s) inherits from %s class dependencies %s\n" % \
                                    (classname,
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


import sys
sys.path.append("../../src")
from core_parser import ClassEntry, Attribute
from keywords import pythonbuiltinfunctions

def convert_ast_to_old_parser(node, filename):
    
    class OldParseModel(object):
        def __init__(self):
            self.classlist = {}
            self.modulemethods = []
            
    class Visitor(ast.NodeVisitor):
        
        def __init__(self, quick_parse):
            self.model = OldParseModel()
            self.stack_classes = []
            self.stack_functions = [False]
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
        
        def am_inside_function(self):
            return self.stack_functions[-1]
        
        def current_class(self):
            if self.stack_classes:
                return self.stack_classes[-1]
            else:
                return None
            
        def write(self, x, mynote=0):
            assert(isinstance(x, str))
            if self.new_lines:
                if self.result:
                    self.result.append('\n' * self.new_lines)
                self.result.append(self.indent_with * self.indentation)
                self.new_lines = 0
            x = "<span class=mynote%d>%s</span>" % (mynote,x)
            self.result.append(x)
            if DEBUG_WRITE:
                print x

        def build_class_entry(self, name):
            c = ClassEntry(name)
            self.model.classlist[name] = c
            self.stack_classes.append(c)
            self.write("  (inside class %s) %s " % (name, [str(c) for c in self.stack_classes]), mynote=3)
            return c

        def add_classdependencytuple(self, t):
            if t not in self.current_class().classdependencytuples:
                self.current_class().classdependencytuples.append(t)
                
        def flush_state(self, msg=""):
            self.write("""
                <table>
                    <tr>
                        <th>lhs</th>
                        <th>rhs</th>
                        <th>made_assignment</th>
                        <th>made_rhs_call</th>
                        <th>made_append_call</th>
                        <th></th>
                    </tr>
                    <tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                    </tr>
                </table>
            """ % (self.lhs, self.rhs, self.made_assignment, self.made_rhs_call, self.made_append_call, msg), mynote=0)

        def flush(self):
            self.flush_state(whosgranddaddy())
            
            # At this point we have both lhs and rhs plus three flags and can
            # make a decision about what to create.
        
            def is_class_creation_call(rhs):
                # called in the context of rhs being Blah
                # ... = Blah()
                # ...append(Blah())  RHS CALL MADE but whether its from the append or the Blah we don't know
                #
                # or even the more relaxed interpretation of a varialble as a class instance if its got the exact same name, rhs being blah
                # ... = blah   NOT THIS, COS NO RHS CALL MADE
                # ...append(blah)
                #
                def relaxed_is_instance_a_known_class(t):
                    for c in self.quick_parse.quick_found_classes:
                        if t.lower() == c.lower():
                            return True, c  # return proper class name not the instance
                    return False, t
                
                res, rhs = relaxed_is_instance_a_known_class(rhs)
                if res:
                    return True, rhs
                
                if rhs not in pythonbuiltinfunctions and rhs not in self.model.modulemethods:
                    return True, rhs
                
                return False, rhs
            
            def in_class_static_area(): return self.current_class() and not self.am_inside_function()
            def in_function_in_class(): return self.current_class() and self.am_inside_function()
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
                
                if in_class_static_area():
                    t = create_attr_static(self.lhs[0])
                elif in_function_in_class() and self.lhs[0] == 'self':
                    t = create_attr_please(self.lhs[1])
                else:
                    pass # in module area
                        
                if self.lhs[0] == 'self' and self.made_rhs_call:
                    res, rhs = is_class_creation_call(self.rhs[0])
                    if res:
                        self.add_classdependencytuple((t, rhs))
                        
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
            if not self.current_class() and not self.am_inside_function():
                self.model.modulemethods.append(node.name)
            else:
                self.current_class().defs.append(node.name)

            # A
            self.stack_functions.append(True)
            self.write("  (inside function) %s " % self.stack_functions, mynote=3)
            
            self.write('):')
            self.body(node.body)
            
            # A
            self.flush()
            # A
            self.stack_functions.pop()
            self.write("  (outside function) %s " % self.stack_functions, mynote=3)
            
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
            self.write("\nvisit_Call ", mynote=1)

            # A
            if len(self.lhs) == 3 and self.current_class() and self.am_inside_function() and \
                            self.lhs[0] == 'self' and self.lhs[2] in ('append', 'add', 'insert'):
                self.lhs_recording = False # try to get the Blah into the rhs
                self.made_append_call = True
                
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
            if len(self.rhs) > 0:
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
            self.quick_found_classes = re.findall(r'^\s*class (.*)[:\(]', source, re.MULTILINE)  
            self.quick_found_module_defs = re.findall(r'^def (.*)\(.*\):', source, re.MULTILINE)
            self.quick_found_module_attrs = re.findall(r'^(\S.*?)[\.]*.*\s*=.*', source, re.MULTILINE)
            
            # WANT TO out(tohtml("classes found %s" % self.quick_found_classes))
            print 'classes found ', self.quick_found_classes
            print 'defs found', self.quick_found_module_defs
            print 'quick_found_module_attrs', self.quick_found_module_attrs
    
    qp = QuickParse(filename)

    v = Visitor(qp)
    
    try:
        v.visit(node)
    except Exception as err:
        print("Parsing Visit error: {0}".format(err))
        traceback.print_exc(file=sys.stdout)
        raise
    #finally:
    if DEBUG:
        debuginfo = '<br>'.join(v.result)
        return v.model, debuginfo
    else:
        return v.model, ""

def tohtml(s, style_class='dump1'):
    return "<div class=%s><pre> %s</div></pre>" % (style_class, s)
    
def header():
    return """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
  <title>My first styled page</title>
  <style type="text/css">
    body { background:DarkSeaGreen; font-family:monospace; }
    .dump1 { background:lightblue; margin:3px; padding:5px; font-size:1.2em;}
    .dumpdiff { background:black; color: white; padding:5px;}
    .mynote0 { font-family:monospace; font-size:1.5em; }
    .mynote1 { color:MediumBlue ; font-size:1.1em; }
    .mynote2 { color:FireBrick ; font-size:1.2em; }
    .mynote3 { background-color:AntiqueWhite; font-size:1.1em; }
    table, td, th
    {
    border:1px solid green;
    border-collapse:collapse;
    padding:5px;
    font-size:0.8em;
    font-family:"Times New Roman",Georgia,Serif;
    background-color:PaleGreen;
    }
  </style>
</head>

<body>
"""

def footer():
    return """</body>
</html>
"""

def out(s, f):
    #print s
    f.write("%s\n"%s)
    
def do_parse_and_convert(filename, outf):
    f = outf
    out(header(), f)
    out("PARSING: %s *****\n" % filename, f)
    p = old_parser(filename)
    d1 = dump_old_structure(p)
    out(tohtml(d1), f)
    out('-'*88, f)
    node = ast_parser(filename)
    p, debuginfo = convert_ast_to_old_parser(node, filename)
    out(debuginfo, f)
    d2 = dump_old_structure(p)
    out(tohtml(d2), f)
    
    comparedok = (d1 == d2)
    out("** old vs new method comparison = %s" % comparedok, f)

    import difflib
    diff = difflib.ndiff(d1.splitlines(1),d2.splitlines(1))
    diff_s = ''.join(diff)
    out(tohtml(diff_s, style_class='dumpdiff'), f)
    if not comparedok:
        print diff_s

    out('',f)
    out(footer(), f)
    return comparedok

def parse_and_convert(in_filename):
    out_filename = os.path.basename(in_filename)
    fileName, fileExtension = os.path.splitext(out_filename)
    out_filename = "logs/debug_%s.html" % fileName
    with open(out_filename, 'w') as f:
        return do_parse_and_convert(in_filename, f)

results = []
results.append(parse_and_convert('../../tests/python-in/testmodule08_multiple_inheritance.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule01.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule02.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule03.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule04.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule05.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule06.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule07.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule66.py'))

print results
if results == [False, True, True, True, True, False, True, True, True]:
    print "refactorings going OK"
else:
    print "oooops"
    