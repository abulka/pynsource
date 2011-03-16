# generate asciiart

from gen_base import ParseReportGenerator

class PySourceAsText(ParseReportGenerator):
    def __init__(self):
        ParseReportGenerator.__init__(self)

    def _DumpAttribute(self, attrobj):
        compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
        if compositescreated and self.embedcompositeswithattributelist:
            self.result +=  "%s %s <@>----> %s" % (attrobj.attrname, self.staticmessage, str(compositescreated))
        else:
            self.result +=  "%s %s" % (attrobj.attrname, self.staticmessage)
        self.result += self.manymessage
        self.result += '\n'

    def _DumpCompositeExtraFooter(self):
        if self.classentry.classdependencytuples and self.listcompositesatend:
            for dependencytuple in self.classentry.classdependencytuples:
                self.result +=  "%s <*>---> %s\n" % dependencytuple
            self.result +=  '-'*20   +'\n'

    def _DumpClassNameAndGeneralisations(self):
        self._Line()
        if self.classentry.ismodulenotrealclass:
            self.result +=  '%s  (file)\n' % (self.aclass,)
        else:
            self.result +=  '%s  --------|> %s\n' % (self.aclass, self.classentry.classesinheritsfrom)
        self._Line()

    def _DumpMethods(self):
        for adef in self.classentry.defs:
            self.result +=  adef +'\n'

    def _Line(self):
        self.result +=  '-'*20   +'\n'

    def _DumpClassFooter(self):
        self.result += '\n'
        self.result += '\n'

