# pynsource command line tool

import os
# from parsing.core_parser import *
from generate_code.gen_asciiart import CmdLinePythonToAsciiArt
from generate_code.gen_yuml import CmdLinePythonToYuml
from generate_code.gen_delphi import CmdLinePythonToDelphi
from generate_code.gen_java import CmdLinePythonToJava
import common.messages
from parsing.dump_pmodel import dump_old_structure
from generate_code.gen_asciiart import PySourceAsText
from generate_code.gen_yuml import PySourceAsYuml
from parsing.api import old_parser, new_parser

def test():
    #FILE = "tests/python-in/testmodule01.py"
    FILE = "tests/python-in/testmodule66.py"

    OLD = False
    if OLD:
        p = PySourceAsText()
        # p = PySourceAsYuml()
        #p.optionModuleAsClass = True
        p.Parse(FILE)
        pmodel = extract_pmodel_from_reporter(p)
    else:
        # pmodel, debuginfo = old_parser(FILE)
        pmodel, debuginfo = new_parser(FILE)

    print(dump_old_structure(pmodel))  # TODO this could be another generate code reporter plugin

    # print p
    #print 'Done.'

# TODO make this a method of PynsourcePythonParser 
def extract_pmodel_from_reporter(parser_reporter):
        """
        The OldParseModel doesn't really exist independently, it is just two attributes on the 'HandleClasses' class of
        the old parser AndyBasicParseEngine.  And the Reporters are just subclasses of the old parser, thus these
        attributes are available to them as self.classlist and self.modulemethods
        This routine extracts the two attributes as an official old parse model.

        Args:
            parser_reporter: a PynsourcePythonParser instance or any descendant like a ReportGenerator or one of its
                descendents e.g. PySourceAsText, PySourceAsYuml etc.

        Returns: pmodel
        """
        class OldParseModel(object):
            def __init__(self):
                self.classlist = {}
                self.modulemethods = []
        pmodel = OldParseModel()
        pmodel.classlist = parser_reporter.classlist
        pmodel.modulemethods = parser_reporter.modulemethods
        return pmodel

def ParseArgsAndRun():
    import sys, glob
    import getopt   # good doco http://www.doughellmann.com/PyMOTW/getopt/
                    # should possibly upgrade to using http://docs.python.org/library/argparse.html#module-argparse
    SIMPLE = 0
    globbed = []

    optionVerbose = 0
    optionModuleAsClass = 0
    optionExportToJava = 0
    optionExportToDelphi = 0
    optionExportToYuml = False
    optionExportTo_outdir = ''

    if SIMPLE:
        params = sys.argv[1]
        globbed = glob.glob(params)
    else:
        listofoptionvaluepairs, params = getopt.getopt(sys.argv[1:], "amvy:j:d:")
        #print listofoptionvaluepairs, params
        #print dict(listofoptionvaluepairs) # turn e.g. [('-v', ''), ('-y', 'fred.png')] into nicer? dict e.g. {'-v': '', '-y': 'fred.png'}
        
        def EnsurePathExists(outdir, outlanguagemsg):
            assert outdir, 'Need to specify output folder for %s output - got %s.'%(outlanguagemsg, outdir)
            if not os.path.exists(outdir):
                raise RuntimeError, ('Output directory %s for %s file output does not exist.'%(outdir,outlanguagemsg))

        for optionvaluepair in listofoptionvaluepairs:
            if '-a' == optionvaluepair[0]:
                pass  # default is asciart, so don't need to specify
            if '-m' == optionvaluepair[0]:
                optionModuleAsClass = 1
            if '-v' == optionvaluepair[0]:
                optionVerbose = 1
            if optionvaluepair[0] in ('-j', '-d'):
                if optionvaluepair[0] == '-j':
                    optionExportToJava = 1
                    language = 'Java'
                else:
                    optionExportToDelphi = 1
                    language = 'Delphi'
                optionExportTo_outdir = optionvaluepair[1]
                EnsurePathExists(optionExportTo_outdir, language)
            if optionvaluepair[0] in ('-y'):
                optionExportToYuml = True
                optionExportTo_outpng = optionvaluepair[1]
        for param in params:
            files = glob.glob(param)
            globbed += files

    if globbed:
        if optionExportToJava or optionExportToDelphi:
            if optionExportToJava:
                u = CmdLinePythonToJava(globbed, treatmoduleasclass=optionModuleAsClass, verbose=optionVerbose)
            else:
                u = CmdLinePythonToDelphi(globbed, treatmoduleasclass=optionModuleAsClass, verbose=optionVerbose)
            u.ExportTo(optionExportTo_outdir)
        elif optionExportToYuml:
            u = CmdLinePythonToYuml(globbed, treatmoduleasclass=optionModuleAsClass, verbose=optionVerbose)
            u.ExportTo(optionExportTo_outpng)
        else:
            u = CmdLinePythonToAsciiArt(globbed, treatmoduleasclass=optionModuleAsClass, verbose=optionVerbose)
            u.ExportTo(None)
    else:
        print common.messages.HELP_COMMAND_LINE_USAGE

if __name__ == '__main__':
    test()
    exit(0)
    # ParseArgsAndRun()
    