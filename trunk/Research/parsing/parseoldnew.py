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

#FILE = 'python-in/testmodule08_multiple_inheritance.py'
FILE = '../../tests/python-in/testmodule08_multiple_inheritance.py'

def dump_old_structure(pmodel):
    for classname, classentry in pmodel.classlist.items():
        print "%s (is module=%s) inherits from %s class dependencies %s" % \
                                    (classname,
                                     classentry.ismodulenotrealclass,
                                     classentry.classesinheritsfrom,
                                     classentry.classdependencytuples)
        for attrobj in classentry.attrs:
            print "%s (type %s)" % (attrobj.attrname,
                                    attrobj.attrtype) # currently skip calc of self._GetCompositeCreatedClassesFor(attrobj.attrname), arguably it should be precalculated and part of the data structure
        for adef in classentry.defs:
            print adef
    print "modulemethods %s" % (pmodel.modulemethods)
    
def old_parser():
    import sys
    sys.path.append("../../src")
    from generate_code.gen_asciiart import PySourceAsText
    
    p = PySourceAsText()
    p.Parse(FILE)
    dump_old_structure(p)

def ast_parser():
    import ast

    with open(FILE,'r') as f:
        source = f.read()
    
    node = ast.parse(source)
    print ast.dump(node)
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
            
        def visit_ClassDef(self, node):
            c = ClassEntry()
            self.model.classlist[node.name] = c
            #for base in node.bases:
            #    c.classesinheritsfrom.append(base.name)

            #have_args = []
            #def paren_or_comma():
            #    if have_args:
            #        print ', ',
            #    else:
            #        have_args.append(True)
            #        print '(',
            #
            ##self.newline(extra=2)
            ##self.decorators(node)
            ##self.newline(node)
            #print 'class %s' % node.name,
            #for base in node.bases:
            #    paren_or_comma()
            #    self.visit(base)
    
    
# self.classlist[self.currclass].classesinheritsfrom.append(self.currsuperclass)
#             self.classlist[self.currclass].defs.append(self.currdef)
#        classentry = self.classlist[self.currclass]
        #if self.nextvarnameisstatic:
        #    attrtype = ['static']

    v = Visitor()
    v.visit(node)
    return v.model
    
old_parser()
print '-'*88
node = ast_parser()
print '-'*88
p = convert_ast_to_old_parser(node)
dump_old_structure(p)

