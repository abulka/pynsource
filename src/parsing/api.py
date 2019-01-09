from parsing.core_parser_old import PynsourcePythonParser
from parsing.core_parser_ast import parse
from common.logwriter import LogWriterNull


def old_parser(filename, options={}):
    p = PynsourcePythonParser()
    p.optionModuleAsClass = options.get("optionModuleAsClass", False)
    p.Parse(filename)
    return p, ""


def new_parser(filename, log=None, options={}):
    if not log:
        log = LogWriterNull()
    pmodel, debuginfo = parse(filename, log, options)
    return pmodel, debuginfo
