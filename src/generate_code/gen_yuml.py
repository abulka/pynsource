# generate Yuml (both text and png)

from .gen_base import ReportGenerator, CmdLineGenerator


class Klass:
    def __init__(self, name, parent=None, connectsto=None, connectorstyle=None, attrs="", defs=""):
        self.name = name
        self.parent = parent  # Klass
        self.connectsto = connectsto  # Klass
        self.connectorstyle = connectorstyle
        self.attrs = attrs
        self.defs = defs

    def MoveAttrsDefsInto(self, klass):
        klass.attrs = self.attrs
        klass.defs = self.defs
        self.attrs = self.defs = ""

    def IsRich(self):
        return self.attrs != "" or self.defs != ""


class Yuml:
    # A line of yUML which is one class or two classes in a relationship
    def __init__(self, lhsclass, connector, rhsclass, rhsattrs, rhsdefs):
        if connector == "^":
            self.klass = Klass(
                rhsclass,
                parent=Klass(lhsclass),
                connectorstyle=connector,
                attrs=rhsattrs,
                defs=rhsdefs,
            )
        elif connector == "":
            assert lhsclass == ""
            self.klass = Klass(rhsclass, attrs=rhsattrs, defs=rhsdefs)
        else:
            self.klass = Klass(
                lhsclass,
                connectsto=Klass(rhsclass, attrs=rhsattrs, defs=rhsdefs),
                connectorstyle=connector,
            )

    def _getrhs(self):
        # if alone then rhs is N/A - interpret as self
        # if have parent then rhs is self
        # if have connector then rhs is connectsto
        if self.klass.connectsto:
            return self.klass.connectsto
        else:
            return self.klass

    def _getlhs(self):
        # if alone then lhs is N/A - interpret as self
        # if have parent then lhs is parent
        # if have connector then lhs is self
        if self.klass.parent:
            return self.klass.parent
        else:
            return self.klass

    rhs = property(_getrhs)
    lhs = property(_getlhs)

    def OneClassAlone(self):
        return self.klass.parent == None and self.klass.connectsto == None

    def __str__(self):
        if self.OneClassAlone():
            s = "[%s|%s|%s]" % (self.klass.name, self.klass.attrs, self.klass.defs)
        else:
            l = self.lhs
            r = self.rhs
            s = "[%s|%s|%s]%s[%s|%s|%s]" % (
                l.name,
                l.attrs,
                l.defs,
                self.klass.connectorstyle,
                r.name,
                r.attrs,
                r.defs,
            )
        s = s.replace("||", "")
        s = s.replace("|]", "]")
        return s


class PySourceAsYuml(ReportGenerator):
    def __init__(self, ast=True):
        ReportGenerator.__init__(self, ast=ast)
        self.yumls = []
        self.enriched_yuml_classes = []

    def AddYuml(self, lhsclass, connector, rhsclass, rhsattrs="", rhsdefs=""):
        yuml = Yuml(lhsclass, connector, rhsclass, rhsattrs, rhsdefs)
        self.yumls.append(yuml)

    def FindRichYumlClass(self, classname):
        index = 0
        for yuml in self.yumls:
            if yuml.rhs.name == classname and yuml.rhs.IsRich():
                return index
            # No need to check the lhs since the order the yumls are
            # generated guarantee rich klasses will occur on the right.
            # Simplifies the Enrich method too as it always moves attrs & defs out of rhs
            index += 1
        return None

    def HasBeenEnriched(self, klass):
        return klass.name in self.enriched_yuml_classes

    def MarkAsEnriched(self, klass):
        self.enriched_yuml_classes.append(klass.name)

    def Enrich(self, YY):
        if not YY.IsRich() and not self.HasBeenEnriched(YY):
            index = self.FindRichYumlClass(YY.name)
            if index != None:
                self.yumls[index].rhs.MoveAttrsDefsInto(YY)
                self.MarkAsEnriched(YY)

    def CompactYumls(self):
        # Now delete lone lines whose rich info has been extracted.
        newyumls = []
        for yuml in self.yumls:
            if not (
                yuml.OneClassAlone()
                and not yuml.klass.IsRich()
                and self.HasBeenEnriched(yuml.klass)
            ):
                newyumls.append(yuml)
        self.yumls = newyumls

    def OptimiseAndEnrichYumls(self):
        for yuml in self.yumls:
            self.Enrich(yuml.rhs)
            self.Enrich(yuml.lhs)
        self.CompactYumls()

    def CalcYumls(self, optimise=True):
        self.yumls = []
        self.enriched_yuml_classes = []

        classnames = list(self.classlist.keys())
        for self.aclass in classnames:
            self.classentry = self.classlist[self.aclass]

            """
            
            # TODO handle modules (but first debug method scanning, which is not under unit test see unittests_parse06.py )
            
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

                # Generate extra yUml lines showing class dependency and composition relationships - generalisation relationship not done here.
                compositescreated = self._GetCompositeCreatedClassesFor(attrobj.attrname)
                for c in compositescreated:
                    if "many" in attrobj.attrtype:
                        line = "++-"
                        cardinality = "*"
                    else:
                        line = "-.->"
                        cardinality = ""
                    connector = "%s%s%s" % (attrobj.attrname, line, cardinality)

                    self.AddYuml(self.aclass, connector, c)

            defs = ""
            for adef in self.classentry.defs:
                if defs:
                    defs += ";"
                defs += adef + "()"

            if self.classentry.classesinheritsfrom:
                parentclass = self.classentry.classesinheritsfrom[
                    0
                ]  # TODO don't throw away all the inherited classes - just grab 0 for now
                self.AddYuml(parentclass, "^", self.aclass, attrs, defs)
            else:
                parentclass = ""
                self.AddYuml("", "", self.aclass, attrs, defs)
        if optimise:
            self.OptimiseAndEnrichYumls()

    def YumlDump(self):
        for yuml in self.yumls:
            self.result += str(yuml) + "\n"

    def GenReportDump(self):  # Override template method entirely and do it ourselves
        if not self.yumls:
            print(
                "Warning, should call CalcYumls() after .Parse() and before str(p) - repairing..."
            )
            self.CalcYumls()
        self.result = ""
        self.YumlDump()
        return self.result


class CmdLinePythonToYuml(CmdLineGenerator):
    """
    The only thing we inherit from CmdLineGenerator is the constructor
    At least we offer similar interface to the world.
    """

    def _GenerateAuxilliaryClasses(self):
        pass

    def _CreateLanguageGenerator(self):
        return PySourceAsYuml()

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
        self.p.CalcYumls()
        print(self.p)  # triggers the complex output behaviour on the generator

        optionExportTo_outpng = outpath

        if optionExportTo_outpng != "nopng":
            if not ".png" in optionExportTo_outpng.lower():
                print("output filename %s must have .png in the name" % optionExportTo_outpng)
                exit(0)
            print("Generating yuml diagram %s..." % optionExportTo_outpng)
            yuml_create_png(",".join(str(self.p).split()), optionExportTo_outpng)

            # Windows specific solution
            # os.system(outpng)  # launch notepad or whatever on it

            # Cross platform solution - conda install pillow
            # This will open the image in your default image viewer.
            from PIL import Image

            img = Image.open(optionExportTo_outpng)
            img.show()

            print("Done!")


import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
from common import png  # codeproject version, not the "easy_install pypng" version.


def _yuml_write_to_png(yuml, in_stream, out_stream):
    signature = png.read_signature(in_stream)
    out_stream.write(signature)

    for chunk in png.all_chunks(in_stream):
        if chunk.chunk_type == "IEND":
            break
        chunk.write(out_stream)

    itxt_chunk = png.iTXtChunk.create("yuml", yuml)
    itxt_chunk.write(out_stream)

    # write the IEND chunk
    chunk.write(out_stream)


def yuml_create_png(yuml_txt, output_filename):
    # baseUrl = 'http://yuml.me/diagram/scruffy/class/'
    baseUrl = "http://yuml.me/diagram/dir:lr;scruffy/class/"
    url = baseUrl + urllib.parse.quote(yuml_txt)

    original_png = urllib.request.urlopen(url)
    output_file = file(output_filename, "wb")

    _yuml_write_to_png(yuml_txt, original_png, output_file)

    output_file.close()


if __name__ == "__main__":
    y = Yuml("a", "->", "b", "fielda", "doa;dob")
    print(y)
    print(Yuml("a", "^", "b", "fielda", "doa;dob"))
