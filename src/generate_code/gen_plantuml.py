from gen_base import ReportGenerator, CmdLineGenerator

class PySourceAsPlantUml(ReportGenerator):
    def __init__(self, ast=True):
        ReportGenerator.__init__(self, ast=ast)
        self.result = ''

    def calc_plant_uml(self, optimise=False):
        self.result = ''

        classnames = self.pmodel.classlist.keys()
        for self.aclass in classnames:
            self.classentry = self.pmodel.classlist[self.aclass]

            # Main class output
            self.result += "\nclass %s {\n" % self.aclass

            for attrobj in self.classentry.attrs:
                self.result += "    %s\n" % attrobj.attrname

            for adef in self.classentry.defs:
                self.result += "    %s()\n" % adef

            # end class
            self.result += "}\n\n"

            # class inheritance relationships
            if self.classentry.classesinheritsfrom:
                for parentclass in self.classentry.classesinheritsfrom:
                    self.result += "%s <|- %s\n" % (parentclass, self.aclass)

            # aggregation relationships showing class dependency and composition relationships
            for attrobj in self.classentry.attrs:
                compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
                for c in compositescreated:
                    if 'many' in attrobj.attrtype:
                        line = "*-->"
                        cardinality = "*"
                    else:
                        line = "..>"
                        cardinality = ""
                    if cardinality:
                        connector = '%s "%s"' % (line, cardinality)
                    else:
                        connector = line
                    self.result += "%s %s %s : %s\n" % (self.aclass, connector, c, attrobj.attrname)


    def GenReportDump(self):            # Override template method entirely and do it ourselves
        """
        This method gets called by the __str__ of the parent ReportGenerator
        We override here to do our own generation rather than the template method design pattern
        approach of ReportGenerator class
        """
        if not self.result:
            print "Warning, should call calc_plant_uml() after .Parse() and before str(p) - repairing..."
            self.calc_plant_uml()
        return "@startuml\n%s@enduml\n" % self.result

class CmdLinePythonToPlantUml(CmdLineGenerator):
    """
    The only thing we inherit from CmdLineGenerator is the constructor with gives us self.directories etc.
    Everything else gets triggered by the ExportTo()
    """
    def _GenerateAuxilliaryClasses(self):
        pass

    def ExportTo(self, outpath=None):     # Override and redefine Template method entirely
        """
        """
        globbed = self.directories

        self.p = PySourceAsPlantUml()
        self.p.optionModuleAsClass = self.optionModuleAsClass
        self.p.verbose = self.verbose

        for f in globbed:
            self.p.Parse(f)
        self.p.calc_plant_uml()
        print self.p

        # optionExportTo_outpng = outpath
        #
        # if optionExportTo_outpng <> "nopng" :
        #     if not '.png' in optionExportTo_outpng.lower():
        #         print "output filename %s must have .png in the name" % optionExportTo_outpng
        #         exit(0)
        #     print 'Generating yuml diagram %s...' % optionExportTo_outpng
        #     yuml_create_png(','.join(str(self.p).split()), optionExportTo_outpng)
        #     #os.system(optionExportTo_outpng)  # launch notepad or whatever on it
        #     print 'Done!'
