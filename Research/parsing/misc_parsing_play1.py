"""
Python parsing tools
http://nedbatchelder.com/text/python-parsers.html
http://wiki.python.org/moin/LanguageParsing
"""

# OLD FASHIOINED PARSER 

import parser
import pprint
source = """
class A:
    def hello(self):
        print 90 + "something"
class Fred(Mary, Sam):
    pass
"""

o = parser.suite(source)
pprint.pprint(parser.st2tuple(o))



print "-"*88



# AST

"""
http://stackoverflow.com/questions/4947783/python-ast-module
http://eli.thegreenplace.net/2009/11/28/python-internals-working-with-python-asts/  ** GOOD

http://www.breti.org/tech/files/a7b5fcecb0596b9bf127212e847584f9-66.html  ** to read
"""

import ast

class Py2Neko(ast.NodeVisitor):
    def generic_visit(self, node):
        print type(node).__name__
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Name(self, node):
        print 'Name :', node.id

    def visit_Num(self, node):
        print 'Num :', node.__dict__['n']

    def visit_Str(self, node):
        print "Str :", node.s

    def visit_Print(self, node):
        print "Print :"
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Assign(self, node):
        print "Assign :"
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Expr(self, node):
        print "Expr :"
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Str(self, node):
        print 'Found string "%s"' % node.s
        
    def visit_ClassDef(self, node):
        have_args = []
        def paren_or_comma():
            if have_args:
                print ', ',
            else:
                have_args.append(True)
                print '(',

        #self.newline(extra=2)
        #self.decorators(node)
        #self.newline(node)
        print 'class %s' % node.name,
        for base in node.bases:
            paren_or_comma()
            self.visit(base)
            
if __name__ == '__main__':
    #node = ast.parse("a = 1 + 2")
    #print ast.dump(node)
    #v = Py2Neko()
    #v.visit(node)
    
    # Andy
    node = ast.parse(source)
    print ast.dump(node)
    v = Py2Neko()
    v.visit(node)

    print
    print "from ast to source code"    
    import codegen   # http://stackoverflow.com/questions/768634/python-parse-a-py-file-read-the-ast-modify-it-then-write-back-the-modified
    print codegen.to_source(node)
    
    
    
"""
lib2to3.

It is a complete pure-Python implementation of a Python parser. It
reads a Python grammar file and parses Python source files according to this
grammar. It offers a great infrastructure for performing AST manipulations and
writing back nicely formatted Python code -- after all it's purpose is to
transform between two Python-like languages with slightly different grammars.

"""
