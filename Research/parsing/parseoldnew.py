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
from architecture_support import whosdaddy, whoscalling2

DEBUG = 0

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

        def record_lhs_rhs(self, s):
            if self.lhs_recording:
                self.lhs.append(s)
                self.write("\nLHS %d %s\n" % (len(self.lhs), self.lhs))
            else:
                self.rhs.append(s)
                self.write("\nRHS %d %s\n" % (len(self.rhs), self.rhs))
        
        def current_class(self):
            return self.class_nesting[-1]
            
        def write(self, x):
            assert(isinstance(x, str))
            if self.new_lines:
                if self.result:
                    self.result.append('\n' * self.new_lines)
                self.result.append(self.indent_with * self.indentation)
                self.new_lines = 0
            self.result.append(x)

        def newline(self, node=None, extra=0):
            self.new_lines = max(self.new_lines, 1 + extra)
            # A
            self.init_lhs_rhs()
            self.write("  attr chain cleared (via newline from %s)" % whosdaddy())

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
            
            self.write("\nvisit_ClassDef\n")
            self.write('class %s' % node.name)
            
            # A
            self.currclass = c = ClassEntry()
            self.model.classlist[node.name] = c
            # A
            self.class_nesting.append(c)
            self.write("  (inside class) %s " % self.class_nesting)

            for base in node.bases:
                # A
                c.classesinheritsfrom.append(base.id)
                
                self.visit(base)
            
            self.body(node.body)

            # A
            self.class_nesting.pop()
            self.write("  (outside class) %s " % self.class_nesting)
            
        def visit_FunctionDef(self, node):
            self.newline(extra=1)
            self.newline(node)
            self.write("\nvisit_FunctionDef\n")
            self.write('def %s(' % node.name)
            
            # A
            if not self.current_class() and not self.am_inside_function[-1]:
                self.model.modulemethods.append(node.name)
            else:
                self.current_class().defs.append(node.name)

            # A
            self.am_inside_function.append(True)
            self.write("  (inside function) %s " % self.am_inside_function)
            
            self.write('):')
            self.body(node.body)

            # A
            self.am_inside_function.pop()
            self.write("  (outside function) %s " % self.am_inside_function)

        def visit_Assign(self, node):  # seems to be the top of the name / attr / chain
            self.write("\nvisit_Assign ")
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
            # At this point we have both lhs and rhs and can make a decision
            # about which attributes to create
            if self.current_class() and not self.am_inside_function[-1]:
                t = self.lhs[0]
                self.current_class().AddAttribute(attrname=t, attrtype=['static'])
            elif self.current_class() and self.am_inside_function[-1] and self.lhs[0] == 'self':
                t = self.lhs[1]
                if (t == '__class__') and len(self.lhs) >= 3:
                    t = self.lhs[2]
                    self.current_class().AddAttribute(attrname=t, attrtype=['static'])
                elif (t != '__class__'):
                    self.current_class().AddAttribute(attrname=t, attrtype=['normal'])
                    
                if self.rhs_call_made and len(self.rhs) >= 0:
                    self.current_class().classdependencytuples.append((t, self.rhs[0]))

        def visit_Call(self, node):
            self.visit(node.func)
            self.write("\nvisit_Call ")
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
               
            # A
            if len(self.lhs) >= 3 and\
                        self.current_class() and \
                        self.am_inside_function[-1] and \
                        self.lhs[0] == 'self' and \
                        self.lhs[2] == 'append':
                t = self.lhs[1]
                self.current_class().AddAttribute(attrname=t, attrtype=['normal', 'many'])
                
                # HOW do we get the Blah from self.f.append(Blah()) into classdependencytuples ???
                #
                # one blah is on the rhs of an assignment, the other Blah is inside a call from append
                # how hand both with the same or similar code?
                #
                #self.lhs_recording = False # try to get the Blah into the rhs
                #self.rhs_call_made = True
                #self.current_class().classdependencytuples.append((t, self.lhs[3]))
                

        def visit_Name(self, node):
            self.write("\nvisit_Name %s\n" % node.id)
            self.write(node.id)

            # A
            self.record_lhs_rhs(node.id)

        def visit_Attribute(self, node):
            self.visit(node.value)
            
            # A
            self.write("\nvisit_Attribute %s\n" % node.attr)
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
        print ''.join(v.result)
    return v.model

def parse_and_convert(filename):
    print "PARSING: %s *****\n" % filename
    p = old_parser(filename)
    d1 = dump_old_structure(p)
    print d1
    print '-'*88
    node = ast_parser(filename)
    p = convert_ast_to_old_parser(node)
    d2 = dump_old_structure(p)
    print d2
    comparedok = (d1 == d2)
    print "** old vs new method comparison = %s" % comparedok
    print
    return comparedok


results = []
results.append(parse_and_convert('../../tests/python-in/testmodule08_multiple_inheritance.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule02.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule04.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule03.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule05.py'))
results.append(parse_and_convert('../../tests/python-in/testmodule01.py'))
print results
if results == [False, True, True, True, False, False]:
    print "refactorings going OK"
else:
    print "oooops"
    