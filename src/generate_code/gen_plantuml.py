import os
import re
import requests
from .gen_base import ReportGenerator, CmdLineGenerator
# from pydbg import dbg
import logging
from common.logger import config_log
import functools
from common.url_to_data import url_to_data
from common.plantuml import deflate_and_encode
import asyncio
from async_lru import alru_cache
import aiohttp
from generate_code.plantuml_html_scan import extract_image_url

log = logging.getLogger(__name__)
config_log(log)

class PySourceAsPlantUml(ReportGenerator):
    def __init__(self, ast=True):
        ReportGenerator.__init__(self, ast=ast)
        self.result = ""

    def calc_plant_uml(self, optimise=False):
        """Optimise not used for anything, so use for sorting attributes and members"""
        self.result = ""

        classnames = list(self.pmodel.classlist.keys())
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
                    if "many" in attrobj.attrtype:
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

    def GenReportDump(self):  # Override template method entirely and do it ourselves
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

    def ExportTo(self, outpath=None):  # Override and redefine Template method entirely
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

        print(plant_uml_text)

        # Optionally generate image via plant uml server
        outpng = outpath
        if outpng != "nopng":
            if not ".png" in outpng.lower():
                print("output filename %s must have .png in the name" % outpng)
                exit(1)
            print("Generating plantuml diagram %s..." % outpng)
            plant_uml_create_png(plant_uml_text, outpng)

            # Windows specific solution
            # os.system(outpng)  # launch notepad or whatever on it

            # Cross platform solution - conda install pillow
            # This will open the image in your default image viewer.
            from PIL import Image

            img = Image.open(outpng)
            img.show()

            print("Done!")


@alru_cache(maxsize=32)
async def plant_uml_create_png_and_return_image_url_async(plant_uml_txt: str, plantuml_server_local_url: str) -> str:
    """Async version of getting image url from plantuml.  This does not get the actual image,
    that is a separate call - unlike in a browser where that second call is done automatically.

    Uses `url_to_data`, and only returns extracted url, no response object is returned by this
    routine, cos it was never used by anyone recently.

    I'm caching the result, though truthfully the call to `url_to_data` is already cached,
    so it probably doesn't make much difference.
    """
    PLANTUML_URL_ON_INTERNET = "http://www.plantuml.com/plantuml/uml"
    # PLANTUML_URL_LOCAL = "http://localhost:8080/plantuml/uml"

    plant_uml_server = plantuml_server_local_url if plantuml_server_local_url else PLANTUML_URL_ON_INTERNET
    log.info("plant_uml_server calculated to be %s" % (plant_uml_server,))

    try:
        # url = os.path.join(plant_uml_server, deflate_and_encode(plant_uml_txt))  # fails on windows cos \ char is not proper url
        url = plant_uml_server + "/" + deflate_and_encode(plant_uml_txt)
        data, status_code = await url_to_data(url)
        log.info(f"Response for url {url} from plant_uml_server status_code is {status_code}")
        response_text = data.decode('utf-8')

    except (ConnectionError,
            requests.exceptions.RequestException,
            aiohttp.client_exceptions.ClientConnectorError) as e:
        # log.exception("Trying to render using plantuml server %s str(e)" % plant_uml_server)
        log.error(
            f"Error trying to fetch initial html from plantuml server {plant_uml_server} {str(e)}")
        return None
    except asyncio.TimeoutError as e:  # there is no string repr of this exception
        log.error("TimeoutError getting plantuml html")
        raise

    if status_code == 200:
        log.info("plant_uml_server responded with 200 ok, next we try to extract diagram url from this HTML...")

        # Uncomment for debugging
        # log.info("plant_uml_server responded with 200 ok, see plantuml_server_response.html for full page response")
        # with open("plantuml_server_response.html", "w") as f:
        #     f.write(response_text)
        
        image_url = extract_image_url(response_text)
        if image_url:
            # this is likely referencing localhost due to calc_plantuml_server_url() giving us a localhost
            image_url = image_url[0]

            if image_url.startswith("//"):
                from urllib.parse import urlparse
                o = urlparse(plant_uml_server)
                image_url = f"{o.scheme}:{image_url}"  # add the scheme back in e.g. http
        else:
            image_url = None
            log.error(f"could not extract image from plant_uml_server - plantuml server html format has probably changed - please report this to https://github.com/abulka/pynsource/issues")

        log.info("extracted actual diagram image_url of %s" % image_url)

        return image_url
    else:
        log.error(f"plant_uml_server responded with {status_code} ok")
        return None

@functools.lru_cache(maxsize=32)
def plant_uml_create_png_and_return_image_url(plant_uml_txt):
    """
    Convert the plantuml text into a uml image url, using the plantuml server on the internet.

    :param plant_uml_txt: plant uml text syntax
    :return: a tuple: [image_url | None], response
    """
    # import hashlib
    # dbg(hashlib.md5(plant_uml_txt.encode('utf-8')).hexdigest())

    # plant_uml_server = calc_plantuml_server_url()
    PLANTUML_URL_ON_INTERNET = "http://www.plantuml.com/plantuml/uml"
    plant_uml_server = PLANTUML_URL_ON_INTERNET
    log.info("plant_uml_server calculated to be %s" % (plant_uml_server,))

    try:
        # response = requests.post(plant_uml_server, data={'text': plant_uml_txt})

        url = os.path.join(plant_uml_server, deflate_and_encode(plant_uml_txt))
        response = requests.get(url)

    except (ConnectionError, requests.exceptions.RequestException) as e:
        # log.exception("Trying to render using plantuml server %s str(e)" % plant_uml_server)
        log.error(f"Error trying to fetch initial html from plantuml server {plant_uml_server} {str(e)}")
        return None, None

    if response.status_code == 200:
        # print("plant_uml_server responded with 200 ok")
        log.info("plant_uml_server responded with 200 ok")

        """
        Need to find the fragment:
            <p id="diagram">
                <img src="http://www.plantuml.com:80/plantuml/png/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000" alt="PlantUML diagram" onload="doneLoading()">
            </p>
        in the response.
        """
        regex = r'.*<p id="diagram".*\s*<.*img src=\"(.*?)\"'
        image_url = re.findall(regex, response.text, re.MULTILINE)
        if image_url:
            image_url = image_url[
                0
            ]  # this is likely referencing localhost due to calc_plantuml_server_url() giving us a localhost
            # if PLANT_UML_LOCAL:
            #     image_url = normalise_plantuml_url(
            #         image_url
            #     )  # substitute the real host we are on.  doesn't really matter, cos always will dynamically repair in all list and update views - but need this repair for ztree1 non persistent debug view, so that can ipad in to e.g. http://192.168.0.3:8000/ztree1 whilst images being returned are refering to localhost which the ipad cannot reach (cos its a different machine)
        else:
            image_url = None
        return image_url, response
    else:
        log.error("plant_uml_server responded with %d ok" % (response.status_code,))
        return None, response

def plant_uml_create_png(plant_uml_txt, output_filename):
    image_url, response = plant_uml_create_png_and_return_image_url(plant_uml_txt)
    print(image_url)

    if image_url:
        """
        Now fetch the image
        """
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(output_filename, "wb") as fp:
                fp.write(response.content)
        else:
            print("ok getting generating uml but error pulling down image")
    else:
        print("error calling plantuml server", response.status_code)

# New

def displaymodel_to_plantuml(displaymodel):
    # TODO Should use AlsmMgr.calc_plant_uml()

    edge_lookup = {
        "generalisation" : "--|>",
        "composition" : "<--",
        "association" : "..",
    }  # TODO need to persist and represent cardinality, which is in the pmodel after all !!
    result = ""
    for node in displaymodel.graph.nodes:
        if hasattr(node, "comment"):
            result += f"note as {node.id}\n"
            result += node.comment + "\n"
            result += "end note\n\n"
        else:
            if ".py" in node.id:
                colour = "<< (M,lightgrey) >> #white"
                name = node.id.replace('.', '_')
                result += f"class {name} <<module>> {colour} {{\n"
            else:
                result += f"class {node.id} {{\n"
            result += "\n".join([f"  {attr}" for attr in node.attrs])
            result += "\n"
            result += "\n".join([f"  {meth}()" for meth in node.meths])
            result += "\n}\n\n"
    for edge in displaymodel.graph.edges:
        line = edge_lookup[edge['uml_edge_type']]

        # See issue https://github.com/abulka/pynsource/issues/78
        # This code displays types instead of attributes, which is not useful, so stop doing it for now
        # label = f": {edge['source'].id}" if edge['uml_edge_type'] in ("composition",) else ""
        # TODO but in alsm mode, we can have edge labels back! Should use AlsmMgr.calc_plant_uml()
        label = ""
        _from = edge['source'].id
        _to = edge['target'].id
        
        _from_is_module = '.' in _from
        _to_is_module = '.' in _to

        if '.' in _from or '.' in _to:
            _from = _from.replace('.', '_')
            _to = _to.replace('.', '_')

        if _to_is_module:  # its always the to side that is the module
            if edge['uml_edge_type'] == "association":
                label = ": contains >"
                result += f"{_to} {line} {_from} {label}\n"
                result += f"{_to} {line}[hidden] {_from} {label}\n"
            else:  # normal directional ref
                result += f"{_from} {line} {_to} {label}\n"
        else:
            result += f"{_from} {line} {_to} {label}\n"
            if edge['uml_edge_type'] == "association":
                result += f"{_from} {line}[hidden] {_to} {label}\n"

    return result
