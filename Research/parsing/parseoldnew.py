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

import sys
sys.path.append("../../src")
from architecture_support import whosdaddy, whosgranddaddy

DEBUG = 1

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
    import ast

    with open(filename,'r') as f:
        source = f.read()
    
    node = ast.parse(source)
    #print ast.dump(node)
    return node


def convert_ast_to_old_parser(node):
    import sys
    sys.path.append("../../src")
    from core_parser import ClassEntry, Attribute
    import ast
    
    class OldParseModel(object):
        def __init__(self):
            self.classlist = {}
            self.modulemethods = []            

    class Visitor(ast.NodeVisitor):
        
        def __init__(self):
            self.model = OldParseModel()
            self.currclass = None
            self.class_nesting = [False]
            self.am_inside_function = [False]

            self.init_lhs_rhs()
            
            self.result = []
            self.indent_with = ' ' * 4
            self.indentation = 0
            self.new_lines = 0

        def init_lhs_rhs(self):
            self.lhs = []
            self.rhs = []
            self.lhs_recording = True
            self.rhs_call_made = False
            self.just_finished = None

        def record_lhs_rhs(self, s):
            if self.lhs_recording:
                self.lhs.append(s)
                self.write("\nLHS %d %s\n" % (len(self.lhs), self.lhs), mynote=2)
            else:
                self.rhs.append(s)
                self.write("\nRHS %d %s\n" % (len(self.rhs), self.rhs), mynote=2)
        
        def current_class(self):
            return self.class_nesting[-1]
            
        def write(self, x, mynote=0):
            assert(isinstance(x, str))
            if self.new_lines:
                if self.result:
                    self.result.append('\n' * self.new_lines)
                self.result.append(self.indent_with * self.indentation)
                self.new_lines = 0
            if mynote == 1:
                x = "<span class=mynote1>%s</span>" % x
            elif mynote == 2:
                x = "<span class=mynote2>%s</span>" % x
            else:
                x = "<span class=codegen>%s</span>" % x
            self.result.append(x)

        # A
        def flush(self):
            self.write("lhs=%30s // rhs=%20s  just_finished = '%s'  rhs_call_made = %s (flush begin)" %(self.lhs, self.rhs, self.just_finished, self.rhs_call_made), mynote=2)
            # At this point we have both lhs and rhs and can make a decision
            # about which attributes to create
            if self.just_finished == 'visit_Assign':
                if self.current_class() and not self.am_inside_function[-1]:
                    t = self.lhs[0]
                    self.current_class().AddAttribute(attrname=t, attrtype=['static'])
                elif self.current_class() and self.am_inside_function[-1] and self.lhs[0] == 'self':
                    t = self.lhs[1]
                    if (t == '__class__') and len(self.lhs) >= 3:
                        t = self.lhs[2]
                        self.current_class().AddAttribute(attrname=t, attrtype=['static'])
                    else:
                        self.current_class().AddAttribute(attrname=t, attrtype=['normal'])
                        
                    if self.rhs_call_made and len(self.rhs) >= 0:
                        self.current_class().classdependencytuples.append((t, self.rhs[0]))
                        
                    if len(self.lhs) == 3 and self.lhs[2] == 'append':
                        self.write("**********", mynote=2)
                        t = self.lhs[1]
                        self.current_class().AddAttribute(attrname=t, attrtype=['normal', 'many'])
                        
            # Need to cater for just_finished = 'None'
            # lhs= ['self', 'e', 'append'] // rhs= [] just_finished = 'None' rhs_call_made = True (flush begin)
            """
visit_Name self
self
LHS 1 ['self']
visit_Attribute e
LHS 2 ['self', 'e']
.e
visit_Attribute append
LHS 3 ['self', 'e', 'append']
.append
visit_Call
(
10
)
            """
                        
            if self.rhs_call_made and \
                        len(self.lhs) == 3 and\
                        self.current_class() and \
                        self.am_inside_function[-1] and \
                        self.lhs[0] == 'self' and \
                        self.lhs[2] == 'append' and \
                        len(self.rhs) >= 1:
                self.write("!!!!!!!!!!!!", mynote=2)
                t = self.lhs[1]
                self.current_class().AddAttribute(attrname=t, attrtype=['normal', 'many'])
                self.current_class().classdependencytuples.append((t, self.rhs[0]))
                        
            self.init_lhs_rhs()
            #self.write("  attr chain cleared (via newline from %s) lhs=%s // rhs=%s\n" % (whosgranddaddy(), self.lhs, self.rhs), mynote=1)
            self.write("lhs=%30s // rhs=%20s  just_finished = '%s'  rhs_call_made = %s (flush end, cleared (via newline from %s))" %(self.lhs, self.rhs, self.just_finished, self.rhs_call_made, whosgranddaddy()), mynote=2)
            self.write("<hr>", mynote=2)
            
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
            self.currclass = c = ClassEntry()
            self.model.classlist[node.name] = c
            # A
            self.class_nesting.append(c)
            self.write("  (inside class) %s " % self.class_nesting, mynote=2)

            for base in node.bases:
                # A
                c.classesinheritsfrom.append(base.id)
                
                self.visit(base)
            
            self.body(node.body)

            # A
            self.flush()
            # A
            self.class_nesting.pop()
            self.write("  (outside class) %s " % self.class_nesting, mynote=2)
            
        def visit_FunctionDef(self, node):
            self.newline(extra=1)
            self.newline(node)
            self.write("\nvisit_FunctionDef\n", mynote=1)
            self.write('def %s(' % node.name)
            
            # A
            if not self.current_class() and not self.am_inside_function[-1]:
                self.model.modulemethods.append(node.name)
            else:
                self.current_class().defs.append(node.name)

            # A
            self.am_inside_function.append(True)
            self.write("  (inside function) %s " % self.am_inside_function, mynote=2)
            
            self.write('):')
            self.body(node.body)
            
            # A
            self.flush()
            # A
            self.am_inside_function.pop()
            self.write("  (outside function) %s " % self.am_inside_function, mynote=2)
            
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
            self.just_finished = 'visit_Assign'

        def visit_Call(self, node):
            self.visit(node.func)
            self.write("\nvisit_Call ", mynote=1)

            # A
            if len(self.lhs) == 3 and self.current_class() and self.am_inside_function[-1] and self.lhs[0] == 'self' and self.lhs[2] == 'append':
                self.lhs_recording = False # try to get the Blah into the rhs
                self.rhs_call_made = True
                
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

            # A for the benefit of visit_Assign so that it can get the Blah() class instance name we are creating
            if len(self.lhs) >= 2 and len(self.rhs) == 1:
               self.rhs_call_made = True
               

            
            #if len(self.lhs) >= 3 and\
            #            self.current_class() and \
            #            self.am_inside_function[-1] and \
            #            self.lhs[0] == 'self' and \
            #            self.lhs[2] == 'append':
            #    t = self.lhs[1]
            #    self.current_class().AddAttribute(attrname=t, attrtype=['normal', 'many'])
                
                # HOW do we get the Blah from self.f.append(Blah()) into classdependencytuples ???
                #
                # one blah is on the rhs of an assignment, the other Blah is inside a call from append
                # how hand both with the same or similar code?
                #
                #self.rhs_call_made = True
                #self.current_class().classdependencytuples.append((t, self.lhs[3]))
                

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
       

    v = Visitor()
    v.visit(node)
    if DEBUG:
        print "<b>", '<br>'.join(v.result), "</b>"
    return v.model

def tohtml(s, style_class='dump1'):
    print "<div class=%s><pre> %s</div></pre>" % (style_class, s)
    
def header():
    return """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
  <title>My first styled page</title>
  <style type="text/css">
  body { background:DarkSeaGreen; font-family:monospace; }
  .dump1 { background:lightblue;
            margin:3px; padding:5px; font-size:1.2em;}
  .dumpdiff { background:black; color: white; padding:5px;}
  .mynote1 { color:MediumBlue ; font-size:1.1em; }
  .mynote2 { color:FireBrick ; font-size:1.2em; }
  .codegen { font-family:monospace; font-size:1.5em; }
  </style>
</head>

<body>
"""

def footer():
    return """</body>
</html>
"""


def parse_and_convert(filename):
    print header()
    print "PARSING: %s *****\n" % filename
    p = old_parser(filename)
    d1 = dump_old_structure(p)
    print tohtml(d1)
    print '-'*88
    node = ast_parser(filename)
    p = convert_ast_to_old_parser(node)
    d2 = dump_old_structure(p)
    print tohtml(d2)
    
    import difflib
    #s = difflib.SequenceMatcher(a=d1, b=d2)
    #for block in s.get_matching_blocks():
    #    print "match at a[%d] and b[%d] of length %d" % block    
    #for line in difflib.context_diff(d1, d2, fromfile='before.py', tofile='after.py'):
    #    sys.stdout.write(line)
    diff = difflib.ndiff(d1.splitlines(1),d2.splitlines(1))
    print tohtml(''.join(diff), style_class='dumpdiff')

    comparedok = (d1 == d2)
    print "** old vs new method comparison = %s" % comparedok
    print
    print footer()
    return comparedok


results = []
#results.append(parse_and_convert('../../tests/python-in/testmodule08_multiple_inheritance.py'))
#results.append(parse_and_convert('../../tests/python-in/testmodule02.py'))
#results.append(parse_and_convert('../../tests/python-in/testmodule04.py'))
#results.append(parse_and_convert('../../tests/python-in/testmodule03.py'))
#results.append(parse_and_convert('../../tests/python-in/testmodule05.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule01.py'))
print results
if results == [False, True, True, True, False, False]:
    print "refactorings going OK"
else:
    print "oooops"
    