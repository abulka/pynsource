import os
import re
from collections import namedtuple
import requests
from .gen_base import ReportGenerator, CmdLineGenerator
# from pydbg import dbg
import logging
from common.logger import config_log
import functools
from common.url_to_data import url_to_data
from common.plantuml import deflate_and_encode, plant_uml_url
import asyncio
from async_lru import alru_cache
import aiohttp

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


PLANTUML_URL_ON_INTERNET = "http://www.plantuml.com/plantuml/uml"

# The PlantUML server refuses to draw an image bigger than this (its
# PLANTUML_LIMIT_SIZE default) - it silently crops anything over the limit.
PLANTUML_PNG_LIMIT = 4096

# How many times we are prepared to re-request a PNG from the server. Fresh
# renders on the public server sometimes come back with the text missing (the
# glyphs measure zero width, so the boxes collapse); a different url usually
# gets a good one back. See Admin notes / DOWNLOADS.md troubleshooting.
PLANTUML_MAX_RENDER_ATTEMPTS = 3

# Result of a render: the url the viewer should fetch, the scale actually used
# (may be lower than requested, see clamp_plantuml_scale) and whether the
# diagram is too big for the server to draw at all.
PlantUmlRender = namedtuple("PlantUmlRender", "image_url scale too_wide attempts")

# Optional GUI hook: called with a short message whenever a render has to be
# retried, so the view can show what is going on instead of just waiting.
_progress_callback = None


def set_progress_callback(callback):
    global _progress_callback
    _progress_callback = callback


def _report_progress(message):
    if _progress_callback is not None:
        try:
            _progress_callback(message)
        except Exception:
            log.exception("Error in plantuml progress callback")


def png_pixel_size(data):
    """(width, height) read straight out of the PNG header, or None.

    Deliberately avoids Pillow - it is only a dev/test dependency.
    """
    if not data or len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width <= 0 or height <= 0:
        return None
    return (width, height)


def svg_pixel_size(svg_bytes):
    """(width, height) of the root <svg> element, or None.

    PlantUML writes e.g. <svg ... style="width:5649px;height:368px;"
    width="5649px" height="368px" viewBox="0 0 5649 368">. Only the root tag is
    inspected, so the width= of the first <rect> inside the document is not
    mistaken for the diagram size.
    """
    if not svg_bytes:
        return None
    try:
        head = svg_bytes[:4000].decode("utf-8", "replace")
    except (UnicodeDecodeError, AttributeError):
        return None
    match = re.search(r"<svg\b[^>]*>", head, re.IGNORECASE)
    if not match:
        return None
    root_tag = match.group(0)

    def attr(name):
        found = re.search(rf'\b{name}\s*=\s*"([0-9.]+)\s*(?:px)?"', root_tag, re.IGNORECASE)
        return float(found.group(1)) if found else None

    width, height = attr("width"), attr("height")
    if width is None or height is None:
        return None
    return (int(round(width)), int(round(height)))


def clamp_plantuml_scale(requested_scale, diagram_width, limit=PLANTUML_PNG_LIMIT):
    """Work out what scale the server can actually draw this diagram at.

    Returns (scale, too_wide). Asking for a scale that would push the image past
    the server's size limit gets the right hand side of the diagram cropped off
    without any warning, so we step the scale down instead.
    """
    try:
        scale = max(1, int(requested_scale or 1))
    except (TypeError, ValueError):
        scale = 1
    if not diagram_width:
        return scale, False
    max_scale = int(limit // diagram_width)
    if max_scale < 1:
        return 1, True  # too wide even at 1x - the server will crop it
    return min(scale, max_scale), False


async def _plant_uml_fetch_direct_async(plant_uml_txt: str, fmt: str, plant_uml_server: str):
    """Fetch raw image bytes straight from the PlantUML server, no HTML scraping.

    Returns (data, status_code) or (None, None) on connection failure.
    """
    url = plant_uml_url(plant_uml_txt, fmt=fmt, server_url=plant_uml_server)
    try:
        data, status_code = await url_to_data(url)
        log.info(f"Response for url {url} from plant_uml_server status_code is {status_code}")
        return data, status_code
    except (ConnectionError,
            requests.exceptions.RequestException,
            aiohttp.client_exceptions.ClientConnectorError) as e:
        log.error(
            f"Error trying to fetch {fmt} from plantuml server {plant_uml_server} {str(e)}")
        return None, None
    except asyncio.TimeoutError:
        log.error(f"TimeoutError getting plantuml {fmt}")
        raise


@alru_cache(maxsize=32)
async def plant_uml_fetch_svg_bytes_async(plant_uml_txt: str, plantuml_server_local_url: str = None):
    """Fetch the diagram as SVG bytes (async, cached).

    Used as the reference for the layout width. The SVG is laid out by the same
    server, so it can occasionally come back degraded too (text running outside
    its boxes); the caller corrects for that by also looking at the PNG width.
    """
    url = plant_uml_url(plant_uml_txt, fmt="svg", server_url=plantuml_server_local_url)
    try:
        data, status_code = await url_to_data(url)
    except (ConnectionError,
            requests.exceptions.RequestException,
            aiohttp.client_exceptions.ClientConnectorError) as e:
        log.error(f"Error trying to fetch svg from plantuml server "
                  f"{plantuml_server_local_url} {str(e)}")
        return None
    except asyncio.TimeoutError:
        log.error("TimeoutError getting plantuml svg")
        return None
    if status_code == 200 and data and data.lstrip()[:1] == b"<":
        return data
    log.error(f"plant_uml_server responded with {status_code} for svg")
    return None


@alru_cache(maxsize=32)
async def plant_uml_create_png_and_return_image_url_async(
        plant_uml_txt: str,
        plantuml_server_local_url: str = None,
        requested_scale: int = 1) -> PlantUmlRender:
    """Render the diagram as PNG and return a PlantUmlRender.

    Three things are handled here:

    1. The server crops anything wider than 4096 px, so the requested HiDPI
       scale is stepped down for wide diagrams (clamp_plantuml_scale).
    2. The public server sometimes returns a render with all the text missing.
       The layout collapses, so comparing the PNG width against the SVG width
       detects it; we then re-request with a slightly different url (a trailing
       comment line changes the encoded url, not the diagram).
    3. If everything fails, the caller gets None.

    The returned url is what the image viewer fetches, so it may include the
    retry comment.
    """
    plant_uml_server = plantuml_server_local_url if plantuml_server_local_url else PLANTUML_URL_ON_INTERNET
    log.info("plant_uml_server calculated to be %s" % (plant_uml_server,))

    svg_bytes = await plant_uml_fetch_svg_bytes_async(plant_uml_txt, plantuml_server_local_url)
    svg_size = svg_pixel_size(svg_bytes) if svg_bytes else None
    diagram_width = svg_size[0] if svg_size else None

    chosen = None  # (url, scale, png_width) - the best render seen so far
    attempts = 0
    for attempt in range(PLANTUML_MAX_RENDER_ATTEMPTS):
        attempts = attempt + 1
        scale, _ = clamp_plantuml_scale(requested_scale, diagram_width)
        if scale > 1:
            attempt_txt = f"scale {scale}\n{plant_uml_txt}"
        else:
            attempt_txt = plant_uml_txt
        if attempt > 0:
            # a trailing comment is harmless to PlantUML but changes the url,
            # which gets us a fresh render instead of the cached textless one
            attempt_txt = f"{attempt_txt}\n' pynsource-retry {attempt}\n"

        data, status_code = await _plant_uml_fetch_direct_async(attempt_txt, "png", plant_uml_server)
        if not data or status_code != 200:
            continue

        png_size = png_pixel_size(data)
        if not png_size:
            continue
        width = png_size[0]

        # Both the PNG and the SVG are laid out by the server, so either can come
        # back with the text missing - which only ever makes the layout narrower.
        # The wider of the two is therefore the honest width.
        logical_width = int(round(width / scale))
        if diagram_width is None or logical_width > diagram_width + 2:
            if diagram_width is not None:
                log.warning(f"plantuml svg width {diagram_width} looks short, "
                            f"using {logical_width} from the png instead")
            diagram_width = logical_width

        expected_width = min(int(round(diagram_width * scale)), PLANTUML_PNG_LIMIT)
        url = plant_uml_url(attempt_txt, fmt="png", server_url=plant_uml_server)
        if abs(width - expected_width) <= 2:
            chosen = (url, scale, width)
            break

        log.warning(f"plantuml render looks like it lost its text "
                    f"(png width {width}, expected {expected_width}) - retrying")
        if attempt + 1 < PLANTUML_MAX_RENDER_ATTEMPTS:
            _report_progress(
                f"PlantUML picture came back with no text - retrying "
                f"({attempt + 2} of {PLANTUML_MAX_RENDER_ATTEMPTS})...")
        else:
            _report_progress(
                "PlantUML picture came back with no text - keeping the best one we got")
        if chosen is None or width > chosen[2]:
            chosen = (url, scale, width)

    if chosen is None:
        return None

    image_url, scale, width = chosen
    # a png sitting exactly on the server's limit was cropped - the server does
    # not warn, it just cuts the right hand side (or bottom) off
    too_wide = width >= PLANTUML_PNG_LIMIT or diagram_width > PLANTUML_PNG_LIMIT
    log.info("direct diagram image_url of %s (scale %d, too_wide %s, attempts %d)"
             % (image_url, scale, too_wide, attempts))
    return PlantUmlRender(image_url, scale, too_wide, attempts)


def plant_uml_probe_server(plantuml_server_local_url: str = None, timeout=15):
    """Blocking health check of a PlantUML server, for the settings dialog.

    Returns (ok, message). Renders a trivial diagram as both SVG and PNG and
    compares the widths: a PNG that is much narrower than its SVG means the
    server returned a render with the text missing.
    """
    plant_uml_server = plantuml_server_local_url if plantuml_server_local_url else PLANTUML_URL_ON_INTERNET
    probe_txt = "class Pynsource {\n  server_probe\n}\n"
    try:
        svg_response = requests.get(
            plant_uml_url(probe_txt, fmt="svg", server_url=plant_uml_server), timeout=timeout)
        png_response = requests.get(
            plant_uml_url(probe_txt, fmt="png", server_url=plant_uml_server), timeout=timeout)
    except (ConnectionError, requests.exceptions.RequestException) as e:
        return False, f"Cannot reach {plant_uml_server} - {str(e)}"

    if png_response.status_code != 200:
        return False, f"Server responded {png_response.status_code} for png"
    content_type = png_response.headers.get("Content-Type", "")
    if not content_type.startswith("image"):
        return False, f"Server did not return an image (got {content_type})"

    png_size = png_pixel_size(png_response.content)
    svg_size = svg_pixel_size(svg_response.content) if svg_response.status_code == 200 else None
    if png_size and svg_size and abs(png_size[0] - svg_size[0]) > 2:
        return False, "Server responds, but the image came back with no text"
    return True, "Server is working"


def svg_on_white_background(svg_bytes: bytes, colour="#ffffff") -> bytes:
    """Insert an opaque background rect into a PlantUML SVG document.

    PlantUML's SVG output has a transparent page by default.  On a dark desktop
    theme the black class borders then disappear while the coloured fills stay
    visible.  A white rect immediately after the root ``<svg>`` makes the
    exported file viewer-independent.
    """
    if not svg_bytes:
        return svg_bytes
    match = re.search(rb"<svg\b[^>]*>", svg_bytes, re.IGNORECASE)
    if not match:
        return svg_bytes
    background = (
        f'<rect x="0" y="0" width="100%" height="100%" fill="{colour}"/>'
    ).encode("ascii")
    return svg_bytes[: match.end()] + background + svg_bytes[match.end():]


@functools.lru_cache(maxsize=32)
def plant_uml_fetch_svg(plant_uml_txt: str, plantuml_server_local_url: str = None) -> bytes:
    """Fetch the diagram as SVG bytes from the PlantUML server (blocking).

    Used for on-demand SVG export from the GUI save dialog. Returns the raw
    SVG document with an opaque white page, or None on failure.
    """
    PLANTUML_URL_ON_INTERNET = "http://www.plantuml.com/plantuml/uml"
    plant_uml_server = plantuml_server_local_url or PLANTUML_URL_ON_INTERNET
    url = plant_uml_url(plant_uml_txt, fmt="svg", server_url=plant_uml_server)
    log.info("fetching svg from %s" % url)
    try:
        response = requests.get(url, timeout=60)
    except (ConnectionError, requests.exceptions.RequestException) as e:
        log.error(f"Error fetching svg from plantuml server {plant_uml_server} {str(e)}")
        return None
    if response.status_code == 200 and response.content.lstrip()[:1] == b"<":
        return svg_on_white_background(response.content)
    log.error(f"plant_uml_server responded with {response.status_code} for svg")
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
