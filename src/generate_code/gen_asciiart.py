# generate asciiart

from .gen_base import ReportGenerator, CmdLineGenerator


class PySourceAsText(ReportGenerator):
    def __init__(self, ast=True):
        ReportGenerator.__init__(self, ast=ast)

    def _DumpAttribute(self, attrobj):
        compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
        if compositescreated and self.embedcompositeswithattributelist:
            self.result += "%s %s <@>----> %s" % (
                attrobj.attrname,
                self.staticmessage,
                str(compositescreated),
            )
        else:
            self.result += "%s %s" % (attrobj.attrname, self.staticmessage)
        self.result += self.manymessage
        self.result += "\n"

    def _DumpCompositeExtraFooter(self):
        if self.classentry.classdependencytuples and self.listcompositesatend:
            for dependencytuple in self.classentry.classdependencytuples:
                self.result += "%s <*>---> %s\n" % dependencytuple
            self.result += "-" * 20 + "\n"

    def _DumpClassNameAndGeneralisations(self):
        self._Line()
        if self.classentry.ismodulenotrealclass:
            self.result += "%s  (file)\n" % (self.aclass,)
        else:
            self.result += "%s  --------|> %s\n" % (
                self.aclass,
                self.classentry.classesinheritsfrom,
            )
        self._Line()

    def _DumpMethods(self):
        for adef in self.classentry.defs:
            self.result += adef + "\n"

    def _Line(self):
        self.result += "-" * 20 + "\n"

    def _DumpClassFooter(self):
        self.result += "\n"
        self.result += "\n"


class CmdLinePythonToAsciiArt(CmdLineGenerator):
    """
    The only thing we inherit from CmdLineGenerator is the constructor
    At least we offer similar interface to the world.
    """

    def _GenerateAuxilliaryClasses(self):
        pass

    def _CreateLanguageGenerator(self):
        return PySourceAsText()

    def _Process(self):
        self.p = self._CreateLanguageGenerator()
        self.p.optionModuleAsClass = self.optionModuleAsClass
        self.p.verbose = self.verbose

    def ExportTo(self, outpath=None):  # Override and redefine Template method entirely
        """
        In this asciiart case self.directories
        actually is a list of files
        """
        globbed = self.directories  # files
        self._Process()
        for f in globbed:
            self.p.Parse(f)
        print(self.p)  # triggers the complex output behaviour on the generator
