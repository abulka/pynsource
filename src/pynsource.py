# pynsource command line tool

import os
# from parsing.core_parser import *
from generate_code.gen_asciiart import CmdLinePythonToAsciiArt
from generate_code.gen_yuml import CmdLinePythonToYuml
from generate_code.gen_delphi import CmdLinePythonToDelphi
from generate_code.gen_java import CmdLinePythonToJava
import common.messages
from parsing.dump_pmodel import dump_old_structure
from parsing.core_parser import PynsourcePythonParser
from parsing.api import old_parser, new_parser

def test():
    #FILE = "tests/python-in/testmodule01.py"
    FILE = "tests/python-in/testmodule66.py"

    strategy = 'ast_via_api' # 'old' or 'old_via_api'
    if strategy == 'old':
        p = PynsourcePythonParser()
        #p.optionModuleAsClass = True
        p.Parse(FILE)
        pmodel = p.pmodel
    elif strategy == 'old_via_api':
        pmodel, debuginfo = old_parser(FILE)
    elif strategy == 'ast_via_api':
        pmodel, debuginfo = new_parser(FILE)

    print(dump_old_structure(pmodel))  # TODO this could be another generate code reporter plugin

    # print p
    #print 'Done.'

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
    option_run_experiment = False
    option_show_parse_model = False
    optionExportTo_outdir = ''

    if SIMPLE:
        params = sys.argv[1]
        globbed = glob.glob(params)
    else:
        listofoptionvaluepairs, params = getopt.getopt(sys.argv[1:], "amvy:j:d:xp:")
        #print listofoptionvaluepairs, params
        #print dict(listofoptionvaluepairs) # turn e.g. [('-v', ''), ('-y', 'fred.png')] into nicer? dict e.g. {'-v': '', '-y': 'fred.png'}
        
        def EnsurePathExists(outdir, outlanguagemsg):
            assert outdir, 'Need to specify output folder for %s output - got %s.'%(outlanguagemsg, outdir)
            if not os.path.exists(outdir):
                raise RuntimeError, ('Output directory %s for %s file output does not exist.'%(outdir,outlanguagemsg))

        for optionvaluepair in listofoptionvaluepairs:
            if '-x' == optionvaluepair[0]:
                option_run_experiment = True
            if '-p' == optionvaluepair[0]:
                # print "picked up -p parameter, globbed is", globbed, 'params', params
                option_show_parse_model = True

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
        elif option_show_parse_model:
            for f in globbed:
                pmodel, debuginfo = new_parser(f)
                print(dump_old_structure(pmodel))
        else:
            u = CmdLinePythonToAsciiArt(globbed, treatmoduleasclass=optionModuleAsClass, verbose=optionVerbose)
            u.ExportTo(None)
    else:
        if option_run_experiment:
            test()
        else:
            print common.messages.HELP_COMMAND_LINE_USAGE

if __name__ == '__main__':
    # test()
    # exit(0)
    ParseArgsAndRun()
    