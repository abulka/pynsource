import ast
from parsing.core_parser import PynsourcePythonParser
from parsing.core_parser_ast import convert_ast_to_old_parser
from common.logwriter import LogWriterNull

def old_parser(filename, options={}):
    p = PynsourcePythonParser()
    p.optionModuleAsClass = options.get('optionModuleAsClass', False)
    p.Parse(filename)
    return p, ''

def new_parser(filename, log=None, options={}):
    if not log:
        log = LogWriterNull()
        
    def ast_parser(filename):
        with open(filename,'r') as f:
            source = f.read()
        
        node = ast.parse(source)
        #print ast.dump(node)
        return node

    node = ast_parser(filename)
    model, debuginfo = convert_ast_to_old_parser(node, filename, log, options)
    return model, debuginfo
