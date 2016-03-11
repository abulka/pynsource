import os
import requests
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
        if not self.result:  # Update: THIS MAY BE VALIDLY EMPTY if there are no classes in a file
            # print "Warning, should call calc_plant_uml() after .Parse() and before str(p) - repairing..."
            self.calc_plant_uml()
        return self.result

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
        plant_uml_text = str(self.p)

        print plant_uml_text

        # Optionally generate image via plant uml server
        outpng = outpath
        if outpng != "nopng" :
            if not '.png' in outpng.lower():
                print "output filename %s must have .png in the name" % outpng
                exit(1)
            print 'Generating plantuml diagram %s...' % outpng
            plant_uml_create_png(plant_uml_text, outpng)

            # Windows specific solution
            # os.system(outpng)  # launch notepad or whatever on it

            # Cross platform solution - conda install pillow
            # This will open the image in your default image viewer.
            from PIL import Image
            img = Image.open(outpng)
            img.show()

            print 'Done!'


def plant_uml_create_png_and_return_image_url(plant_uml_txt):
    plant_uml_server = "http://www.plantuml.com/plantuml/form"
    response = requests.post(plant_uml_server,
                             data={'text': plant_uml_txt})
    if response.status_code == 200:

        """
        Need to find the fragment:
            <p id="diagram">
                <img src="http://www.plantuml.com:80/plantuml/png/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000" alt="PlantUML diagram" onload="doneLoading()">
            </p>
        in the response.
        """
        import re
        regex = r'.*<p id="diagram".*\s*<.*img src=\"(.*?)\"'
        image_url = re.findall(regex, response.text, re.MULTILINE)
        if image_url:
            image_url = image_url[0]
        return image_url, response
    else:
        return None, response

def plant_uml_create_png(plant_uml_txt, output_filename):
    image_url, response = plant_uml_create_png_and_return_image_url(plant_uml_txt)
    print image_url

    if image_url:
        """
        Now fetch the image
        """
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(output_filename, 'wb') as fp:
                fp.write(response.content)
        else:
            print 'ok getting generating uml but error pulling down image'
    else:
        print 'error calling plantuml server', response.status_code
