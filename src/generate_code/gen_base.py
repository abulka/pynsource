# base class for output generators and for the cmdline wrappers for those generators

import os, glob
from parsing.api import old_parser, new_parser
from functools import cmp_to_key  # to still be able to use old style compare func in sort


class ReportGenerator(object):
    """
    New ReportGenerator doesn't inherit from the old parser classes,
    it uses a new or old parser instead.

    """

    def __init__(self, ast=True):
        self.ast_parsing = ast
        self.listcompositesatend = 0
        self.embedcompositeswithattributelist = 1
        self.result = ""
        self.aclass = None
        self.classentry = None
        self.staticmessage = ""
        self.manymessage = ""
        self.verbose = 0

        self.optionModuleAsClass = False

    def Parse(self, file):
        if self.ast_parsing:
            pmodel, debuginfo = new_parser(file)
        else:
            options = {"optionModuleAsClass": self.optionModuleAsClass}
            pmodel, debuginfo = old_parser(file, options)

        self.pmodel = pmodel  # remember the parse model

        # break apart pmodel so that its attributes are on the report generator itself (legacy yukiness)
        self.classlist = pmodel.classlist
        self.modulemethods = pmodel.modulemethods

    def GetCompositeClassesForAttr(self, classname, classentry):
        resultlist = []
        for dependencytuple in classentry.classdependencytuples:
            if dependencytuple[0] == classname:
                resultlist.append(dependencytuple[1])
        return resultlist

    def _GetCompositeCreatedClassesFor(self, classname):
        return self.GetCompositeClassesForAttr(classname, self.classentry)

    def _DumpAttributes(self):
        for attrobj in self.classentry.attrs:
            self.staticmessage = ""
            self.manymessage = ""
            if "static" in attrobj.attrtype:
                self.staticmessage = " static"
            if "many" in attrobj.attrtype:
                self.manymessage = " 1..*"
            self._DumpAttribute(attrobj)

    def _DumpClassHeader(self):
        self.result += "\n"

    def _DumpModuleMethods(self):
        if self.modulemethods:
            self.result += "  ModuleMethods = %s\n" % repr(self.modulemethods)

    def GenReportDump(
        self
    ):  # DESIGN PATTERN: Template method, subclasses override the _methods to vary
        self.result = ""
        self._DumpClassHeader()
        self._DumpModuleMethods()

        optionAlphabetic = 0
        classnames = list(self.classlist.keys())
        if optionAlphabetic:
            classnames.sort()
        else:

            def cmpfunc(a, b):
                if a.find("Module_") != -1:
                    return -1
                else:
                    if a < b:
                        return -1
                    elif a == b:
                        return 0
                    else:
                        return 1

            classnames.sort(key=cmp_to_key(cmpfunc))

        for (
            self.aclass
        ) in classnames:  # for self.aclass, self.classentry in self.classlist.items():
            self.classentry = self.classlist[self.aclass]

            self._DumpClassNameAndGeneralisations()
            self._DumpAttributes()
            self._Line()
            self._DumpMethods()
            self._Line()
            self._DumpCompositeExtraFooter()
            self._DumpClassFooter()
        return self.result

    def __str__(self):
        return self.GenReportDump()


class CmdLineGenerator:
    def __init__(self, directories, treatmoduleasclass=0, verbose=0):
        self.directories = directories
        self.optionModuleAsClass = treatmoduleasclass
        self.verbose = verbose

    def ExportTo(self, outpath):  # Template method
        self.outpath = outpath

        self._GenerateAuxilliaryClasses()  # overridden by subclasses

        for directory in self.directories:
            if "*" in directory or "." in directory:
                filepath = directory
            else:
                filepath = os.path.join(directory, "*.py")
            if self.verbose:
                print("Processing directory", filepath)
            globbed = glob.glob(filepath)
            for f in globbed:
                self._Process(f)

    def _Process(self, filepath):  # Template method
        if self.verbose:
            padding = " "
        else:
            padding = ""
        thefile = os.path.basename(filepath)
        if thefile[0] == "_":
            print("  ", "Skipped", thefile, "cos begins with underscore.")
            return
        print("%sProcessing %s..." % (padding, thefile))

        self.p = self._CreateLanguageGenerator()  # overridden by subclasses
        self.p.optionModuleAsClass = self.optionModuleAsClass
        self.p.verbose = self.verbose

        self.p.Parse(filepath)
        str(
            self.p
        )  # triggers the complex output on the generator.  Usually involves calling a complex template method being invoked, which calls overridden methods in particular generator classes.
