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

def dump_old_structure(pmodel):
    for classname, classentry in pmodel.classlist.items():
        print "%s (is module=%s) inherits from %s class dependencies %s" % \
                                    (classname,
                                     classentry.ismodulenotrealclass,
                                     classentry.classesinheritsfrom,
                                     classentry.classdependencytuples)
        for attrobj in classentry.attrs:
            print "    %-20s (attrtype %s)" % (attrobj.attrname,
                                            attrobj.attrtype) # currently skip calc of self._GetCompositeCreatedClassesFor(attrobj.attrname), arguably it should be precalculated and part of the data structure
        for adef in classentry.defs:
            print "    %s()" % adef
    print "    modulemethods %s" % (pmodel.modulemethods)
    
def old_parser(filename):
    import sys
    sys.path.append("../../src")
    from generate_code.gen_asciiart import PySourceAsText
    
    p = PySourceAsText()
    p.Parse(filename)
    dump_old_structure(p)

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

            self.result = []
            self.indent_with = ' ' * 4
            self.indentation = 0
            self.new_lines = 0

        def write(self, x):
            assert(isinstance(x, str))
            if self.new_lines:
                if self.result:
                    self.result.append('\n' * self.new_lines)
                self.result.append(self.indent_with * self.indentation)
                self.new_lines = 0
            self.result.append(x)
        
        def visit_ClassDef(self, node):
            self.write("visit_ClassDef ")
            self.write(node.name)
            
            self.currclass = c = ClassEntry()
            self.model.classlist[node.name] = c
            for base in node.bases:
                c.classesinheritsfrom.append(base.id)

        def visit_FunctionDef(self, node):
            self.write("visit_FunctionDef ")
            self.write(node.id)
            
            self.currclass.defs.append(node.name)

        def visit_Assign(self, node):
            print "visit_Assign", node.id
            #self.newline(node)
            #for idx, target in enumerate(node.targets):
            #    if idx:
            #        self.write(', ')
            #    self.visit(target)
            #self.write(' = ')
            #self.visit(node.value)


        def visit_Attribute(self, node):
            print "visit_Attribute"
            #self.visit(node.value)
            #self.write('.' + node.attr)
    
        def visit_Call(self, node):
            print "visit_Call"
            #self.visit(node.func)
            #self.write('(')

        def visit_Name(self, node):
            self.write(node.id)

        def visit_Str(self, node):
            self.write(repr(node.s))

        def visit_Expr(self, node):
            print "visit_Expr", node
            #self.newline(node)
            #self.generic_visit(node)
        
#        classentry = self.classlist[self.currclass]
        #if self.nextvarnameisstatic:
        #    attrtype = ['static']

    v = Visitor()
    v.visit(node)
    print ''.join(v.result) # why doesn't print work and we have to do this
    return v.model

def parse_and_convert(filename):
    print "PARSING: %s *****\n" % filename
    old_parser(filename)
    print '-'*88
    node = ast_parser(filename)
    p = convert_ast_to_old_parser(node)
    dump_old_structure(p)
    print


parse_and_convert('../../tests/python-in/testmodule08_multiple_inheritance.py')
parse_and_convert('../../tests/python-in/testmodule02.py')
