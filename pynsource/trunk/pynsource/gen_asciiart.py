# generate asciiart

from core_parser import PynsourcePythonParser

class PySourceAsText(PynsourcePythonParser):
    def __init__(self):
        PynsourcePythonParser.__init__(self)
        self.listcompositesatend = 0
        self.embedcompositeswithattributelist = 1
        self.result = ''
        self.aclass = None
        self.classentry = None
        self.staticmessage = ""
        self.manymessage = ""
        self.verbose = 0

    def GetCompositeClassesForAttr(self, classname, classentry):
        resultlist = []
        for dependencytuple in classentry.classdependencytuples:
            if dependencytuple[0] == classname:
                resultlist.append(dependencytuple[1])
        return resultlist

    def _GetCompositeCreatedClassesFor(self, classname):
        return self.GetCompositeClassesForAttr(classname, self.classentry)

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

    def _DumpAttributes(self):
        for attrobj in self.classentry.attrs:
            self.staticmessage = ""
            self.manymessage = ""
            if 'static' in attrobj.attrtype:
                self.staticmessage = " static"
            if 'many' in attrobj.attrtype:
                self.manymessage = " 1..*"
            self._DumpAttribute(attrobj)

    def _DumpMethods(self):
        for adef in self.classentry.defs:
            self.result +=  adef +'\n'

    def _Line(self):
        self.result +=  '-'*20   +'\n'

    def _DumpClassHeader(self):
        self.result += '\n'

    def _DumpClassFooter(self):
        self.result += '\n'
        self.result += '\n'

    def _DumpModuleMethods(self):
        if self.modulemethods:
            self.result += '  ModuleMethods = %s\n' % `self.modulemethods`
##        self.result += '\n'

    def __str__(self):   # DESIGN PATTERN: Template method, subclasses override the _methods to vary
        self.result = ''
        self._DumpClassHeader()
        self._DumpModuleMethods()

        optionAlphabetic = 0
        classnames = self.classlist.keys()
        if optionAlphabetic:
            classnames.sort()
        else:
            def cmpfunc(a,b):
                if a.find('Module_') <> -1:
                    return -1
                else:
                    if a < b:
                        return -1
                    elif a == b:
                        return 0
                    else:
                        return 1
            classnames.sort(cmpfunc)
            
        for self.aclass in classnames:   # for self.aclass, self.classentry in self.classlist.items():
            self.classentry = self.classlist[self.aclass]

            self._DumpClassNameAndGeneralisations()
            self._DumpAttributes()
            self._Line()
            self._DumpMethods()
            self._Line()
            self._DumpCompositeExtraFooter()
            self._DumpClassFooter()
        return self.result
    