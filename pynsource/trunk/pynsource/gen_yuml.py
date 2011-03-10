# generate Yuml (both text and png)

from core_parser import HandleModuleLevelDefsAndAttrs

class Klass:
    def __init__(self, name, parent=None, connectsto=None, connectorstyle=None, attrs="", defs=""):
        self.name = name
        self.parent = parent
        self.connectsto = connectsto
        self.connectorstyle = connectorstyle
        self.attrs = attrs
        self.defs = defs

class YumlLine:
    def __init__(self, lhsclass, connector, rhsclass, rhsattrs, rhsdefs):
        if connector == "^":
            self.klass = Klass(rhsclass, parent=Klass(lhsclass), connectorstyle=connector, attrs=rhsattrs, defs=rhsdefs)
        elif connector == "":
            assert lhsclass == ""
            self.klass = Klass(rhsclass, attrs=rhsattrs, defs=rhsdefs)
        else:
            self.klass = Klass(lhsclass, connectsto=Klass(rhsclass, attrs=rhsattrs, defs=rhsdefs), connectorstyle=connector)
            
    def GetRhs(self):
        # if alone then rhs is N/A - interpret as self
        # if have parent then rhs is self
        # if have connector then rhs is connectsto
        if self.klass.connectsto:
            return self.klass.connectsto
        else:
            return self.klass

    def GetLhs(self):
        # if alone then lhs is N/A - interpret as self
        # if have parent then lhs is parent
        # if have connector then lhs is self
        if self.klass.parent:
            return self.klass.parent
        else:
            return self.klass

    def IsRichRhs(self):
        c = self.GetRhs()
        return (c.attrs <> "" or c.defs <> "")
    
    def IsRichLhs(self):
        c = self.GetLhs()
        return (c.attrs <> "" or c.defs <> "")
        
    def RhsAloneWithNoParent(self):
        if self.klass.parent == None and self.klass.connectsto == None:
            assert self.klass == self.GetRhs()
            return True
        else:
            return False
    
    def __str__(self):
        if self.RhsAloneWithNoParent():
            s = "[%s|%s|%s]" % (self.klass.name, self.klass.attrs, self.klass.defs)
        else:
            l = self.GetLhs()
            r = self.GetRhs()
            s = "[%s|%s|%s]%s[%s|%s|%s]" % (l.name, l.attrs, l.defs, self.klass.connectorstyle, r.name, r.attrs, r.defs)
        s = s.replace("||", "")
        s = s.replace("|]", "]")
        return  s

class YumlLine_:
    def __init__(self, lhsclass, connector, rhsclass, rhsattrs, rhsdefs):
        self.lhsclass = lhsclass
        self.lhsattrs = ""
        self.lhsdefs = ""
        self.connector = connector
        self.rhsclass = rhsclass
        self.rhsattrs = rhsattrs
        self.rhsdefs = rhsdefs
        
    def IsRichRhs(self):
        return self.rhsattrs <> "" or self.rhsdefs <> ""
    
    def IsRichLhs(self):
        # lhs is only rich when it is alone
        return self.RhsAloneWithNoParent()

    def RhsAloneWithNoParent(self):
        if self.connector == "":
            assert self.lhsclass == ""
        return self.connector == ""
    
    def __str__(self):
        if self.lhsclass == "" and self.connector == "":
            s = "[%s|%s|%s]" % (self.rhsclass, self.rhsattrs, self.rhsdefs)
        else:
            s = "[%s|%s|%s]%s[%s|%s|%s]" % (self.lhsclass, self.lhsattrs, self.lhsdefs, self.connector, self.rhsclass, self.rhsattrs, self.rhsdefs)
        s = s.replace("||", "")
        s = s.replace("|]", "]")
        return  s
    
    def GetRhs(self):
        class Junk:
            def __init__(self, name):
                self.name = name
        return Junk(self.rhsclass)
        
    def GetLhs(self):
        class Junk:
            def __init__(self, name):
                self.name = name
        return Junk(self.lhsclass)
                 
class PySourceAsYuml(HandleModuleLevelDefsAndAttrs):
    def __init__(self):
        HandleModuleLevelDefsAndAttrs.__init__(self)
        self.result = ''
        self.aclass = None
        self.classentry = None
        self.verbose = 0
        self.yumls = []
        self.yumls_optimised = []

    def GetCompositeClassesForAttr(self, classname, classentry):
        resultlist = []
        for dependencytuple in classentry.classdependencytuples:
            if dependencytuple[0] == classname:
                resultlist.append(dependencytuple[1])
        return resultlist

    def _GetCompositeCreatedClassesFor(self, classname):
        return self.GetCompositeClassesForAttr(classname, self.classentry)

    def FindIndexRichRhsYuml(self, classname):
        index = 0
        for yuml in self.yumls:
            if yuml.GetRhs().name == classname and yuml.IsRichRhs():
                return index
            index += 1            
        return None

    def AddYuml(self, lhsclass, connector, rhsclass, rhsattrs="", rhsdefs=""):
        yuml = YumlLine(lhsclass, connector, rhsclass, rhsattrs, rhsdefs)
        self.yumls.append(yuml)

    #def YumlSuckAttrsAndDefsIntoRhs(self, from_yuml=None, to_yuml=None):
    #    to_yuml.rhsattrs = from_yuml.rhsattrs
    #    to_yuml.rhsdefs = from_yuml.rhsdefs
    #    from_yuml.rhsattrs = from_yuml.rhsdefs = ""
    #
    #def YumlSuckAttrsAndDefsIntoLhs(self, from_yuml=None, to_yuml=None):
    #    to_yuml.lhsattrs = from_yuml.rhsattrs
    #    to_yuml.lhsdefs = from_yuml.rhsdefs
    #    from_yuml.rhsattrs = from_yuml.rhsdefs = ""
        
    def YumlSuckAttrsAndDefsIntoRhs(self, from_yuml=None, to_yuml=None):
        a = from_yuml.GetRhs().attrs
        d = from_yuml.GetRhs().defs
        from_yuml.GetRhs().attrs = from_yuml.GetRhs().defs = ""

        to_yuml.GetRhs().attrs = a
        to_yuml.GetRhs().defs = d

    def YumlSuckAttrsAndDefsIntoLhs(self, from_yuml=None, to_yuml=None):
        a = from_yuml.GetRhs().attrs
        d = from_yuml.GetRhs().defs
        from_yuml.GetRhs().attrs = from_yuml.GetRhs().defs = ""

        to_yuml.GetLhs().attrs = a
        to_yuml.GetLhs().defs = d

    def YumlOptimise(self, debug=False):
        if debug:
            print
        for yuml in self.yumls:
            if debug:
                print "OPTIMISE RhsAloneWithNoParent() = %d yuml.IsRichRhs() = %d for %s  YUML %s" % (yuml.RhsAloneWithNoParent(), yuml.IsRichRhs(), yuml.rhsclass, str(yuml))
            if not yuml.IsRichRhs() and not yuml.GetRhs().name in self.yumls_optimised:
                index = self.FindIndexRichRhsYuml(yuml.GetRhs().name) 
                if debug:
                    print "    scanning for RICH version of RHS class %s" % yuml.GetRhs().name
                if index == None:
                    if debug:
                        print "    no rich yuml found"
                else:
                    if debug:
                        print "    found at index %d, need to swap rhs at that index into lhs here.  YUML %s" % (index, str(yuml))
                    self.YumlSuckAttrsAndDefsIntoRhs(from_yuml=self.yumls[index], to_yuml=yuml)
                    self.yumls_optimised.append(yuml.GetRhs().name)
            if not yuml.IsRichLhs() and not yuml.GetLhs().name in self.yumls_optimised:
                index = self.FindIndexRichRhsYuml(yuml.GetLhs().name)
                if debug:
                    print "    scanning for RICH lhs version of LHS class %s" % yuml.GetLhs().name
                if index == None:
                    if debug:
                        print "    no rich yuml found"
                else:
                    if debug:
                        print "    found at index %d, need to swap rhs at that index into lhs here.  YUML %s" % (index, str(yuml))
                    self.YumlSuckAttrsAndDefsIntoLhs(from_yuml=self.yumls[index], to_yuml=yuml)
                    self.yumls_optimised.append(yuml.GetLhs().name)
            else:
                pass
            
        # Now delete lone lines with one lone class that is not rich,
        # and which is not mentioned anywhere else (if its been optimised then a rich version exists somewhere else, so checking yuml.rhsclass in self.yumls_optimised is the logic)
        if debug:
            print "CLEANUP OPTIMISATION"
        newyumls = []
        for yuml in self.yumls:
            if debug:
                print "if yuml.RhsAloneWithNoParent() %s and not yuml.IsRichRhs() %r and yuml.rhsclass in self.yumls_optimised %r" %(yuml.RhsAloneWithNoParent(), not yuml.IsRichRhs(), yuml.GetRhs().name in self.yumls_optimised)
            if yuml.RhsAloneWithNoParent() and not yuml.IsRichRhs() and yuml.GetRhs().name in self.yumls_optimised:
                pass
            else:
                newyumls.append(yuml)
        self.yumls = newyumls
        
    def CalcYumls(self, optimise=True):
        self.yumls = []
        self.yumls_optimised = []
        classnames = self.classlist.keys()
        for self.aclass in classnames:
            self.classentry = self.classlist[self.aclass]

            """
            
            #TODO handle modules (but first debug method scanning, which is not under unit test see unittests_parse06.py )
            
            if self.classentry.ismodulenotrealclass:
                continue
                self.result +=  '[%s  (file)]\n' % (self.aclass,)
                if self.modulemethods:
                    self.result += '  ModuleMethods = %s\n' % `self.modulemethods`
                    self.result += "-[note: module/file's methods]"
                continue
            """
            
            attrs = ""
            for attrobj in self.classentry.attrs:
                if attrs:
                    attrs += ";"
                attrs += attrobj.attrname

                # gen extra yUml lines showing class relationships
                # SHOULD not dump so many extra lines as yUml likes the info consolidated if at all possible
                compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
                for c in compositescreated:
                    if 'many' in attrobj.attrtype:
                        line = "++-"
                        cardinality = "*"
                    else:
                        line = "-.->"
                        cardinality = ""
                    connector = "%s%s%s" % (attrobj.attrname, line, cardinality)
                    
                    self.AddYuml(self.aclass, connector, c)
                    #self.result += "[%s]%s[%s]\n" % (self.aclass, connector, c)

            defs = ""
            for adef in self.classentry.defs:
                if defs:
                    defs += ";"
                defs += adef + "()"
                
            #theclass = "%s|%s|%s" % (self.aclass, attrs, defs)
            
            if self.classentry.classesinheritsfrom:
                parentclass = self.classentry.classesinheritsfrom[0]  #TODO don't throw away all the inherited classes - just grab 0 for now
                self.AddYuml(parentclass, "^", self.aclass, attrs, defs)
                #self.result +=  '[%s]^[%s]\n' % (parentclass, theclass)
            else:
                parentclass = ""
                self.AddYuml("", "", self.aclass, attrs, defs)
                #self.result +=  '[%s]\n' % (theclass,)
        if optimise:
            self.YumlOptimise(debug=False)
        
    def YumlDump(self):
        for yuml in self.yumls:
            self.result += str(yuml) + "\n"
            
    def __str__(self):
        if not self.yumls:
            print "Warning, should call CalcYumls() after .Parse() and before str(p) - repairing..."
            self.CalcYumls()
        self.result = ''
        self.YumlDump()
        return self.result
    
import urllib
import urllib2
import png    # codeproject version, not the "easy_install pypng" version.

def write_yuml_to_png(yuml, in_stream, out_stream):
    signature = png.read_signature(in_stream)
    out_stream.write(signature)
    
    for chunk in png.all_chunks(in_stream):
        if chunk.chunk_type == 'IEND':
            break
        chunk.write(out_stream)

    itxt_chunk = png.iTXtChunk.create('yuml', yuml)
    itxt_chunk.write(out_stream)

    # write the IEND chunk
    chunk.write(out_stream)

def yumlcreate(yuml, output_filename):
    #baseUrl = 'http://yuml.me/diagram/scruffy/class/'
    baseUrl = 'http://yuml.me/diagram/dir:lr;scruffy/class/'
    url = baseUrl + urllib.quote(yuml)
    
    original_png = urllib2.urlopen(url)
    output_file = file(output_filename, 'wb')

    write_yuml_to_png(yuml, original_png, output_file)

    output_file.close()

if __name__ == '__main__':
    y = YumlLine('a','->','b', "fielda", "doa;dob")
    print y
    print YumlLine('a','^','b', "fielda", "doa;dob")
    
    