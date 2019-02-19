from __future__ import print_function

"""
Python 2 & 3 compatible version of
https://github.com/dougn/python-plantuml
"""
import zlib
import os
import sys

__version__ = [0, 1, 1]
__version_string__ = ".".join(str(x) for x in __version__)

__author__ = "Doug Napoleone"
__email__ = "doug.napoleone+plantuml@gmail.com"

#: Default plantuml service url
SERVER_URL = "http://www.plantuml.com/plantuml/img/"


class PlantUMLError(Exception):
    """Error in processing.
    """

    pass


class PlantUMLConnectionError(PlantUMLError):
    """Error connecting or talking to PlantUML Server.
    """

    pass


class PlantUMLHTTPError(PlantUMLConnectionError):
    """Request to PlantUML server returned HTTP Error.
    """

    def __init__(self, response, content, *args, **kwdargs):
        super(PlantUMLConnectionError, self).__init__(*args, **kwdargs)
        self.response = response
        self.content = content
        if not self.message:
            self.message = "%d: %s" % (self.response.status, self.response.reason)


def deflate_and_encode(plantuml_text):
    """zlib compress the plantuml text and encode it for the plantuml server.
       Now made python3 compatible via encode and decode. 'latin-1' needed so that non ascii chars get converted into non printable chars in a string, which encode() expects - in a string.
    """
    zlibbed_str = zlib.compress(plantuml_text.encode("utf-8"))
    compressed_string = zlibbed_str[2:-4]
    return encode(compressed_string.decode("latin-1"))


def encode(data):
    """encode the plantuml data which may be compresses in the proper
    encoding for the plantuml server
    """
    res = ""
    for i in range(0, len(data), 3):
        if i + 2 == len(data):
            res += _encode3bytes(ord(data[i]), ord(data[i + 1]), 0)
        elif i + 1 == len(data):
            res += _encode3bytes(ord(data[i]), 0, 0)
        else:
            res += _encode3bytes(ord(data[i]), ord(data[i + 1]), ord(data[i + 2]))
    return res


def _encode3bytes(b1, b2, b3):
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    res = ""
    res += _encode6bit(c1 & 0x3F)
    res += _encode6bit(c2 & 0x3F)
    res += _encode6bit(c3 & 0x3F)
    res += _encode6bit(c4 & 0x3F)
    return res


def _encode6bit(b):
    if b < 10:
        return chr(48 + b)
    b -= 10
    if b < 26:
        return chr(65 + b)
    b -= 26
    if b < 26:
        return chr(97 + b)
    b -= 26
    if b == 0:
        return "-"
    if b == 1:
        return "_"
    return "?"


class PlantUML(object):
    """Connection to a PlantUML server with optional authentication.
    
    All parameters are optional.
    
    :param str url: URL to the PlantUML server image CGI. defaults to
                    http://www.plantuml.com/plantuml/img/
    :param dict basic_auth: This is if the plantuml server requires basic HTTP
                    authentication. Dictionary containing two keys, 'username'
                    and 'password', set to appropriate values for basic HTTP
                    authentication.
    :param dict form_auth: This is for plantuml server requires a cookie based
                    webform login authentication. Dictionary containing two
                    primary keys, 'url' and 'body'. The 'url' should point to
                    the login URL for the server, and the 'body' should be a
                    dictionary set to the form elements required for login.
                    The key 'method' will default to 'POST'. The key 'headers'
                    defaults to
                    {'Content-type':'application/x-www-form-urlencoded'}.
                    Example: form_auth={'url': 'http://example.com/login/',
                    'body': { 'username': 'me', 'password': 'secret'}
    :param dict http_opts: Extra options to be passed off to the
                    httplib2.Http() constructor.
    :param dict request_opts: Extra options to be passed off to the
                    httplib2.Http().request() call.
                    
    """

    def __init__(self, url=SERVER_URL, basic_auth={}, form_auth={}, http_opts={}, request_opts={}):
        import httplib2

        self.HttpLib2Error = httplib2.HttpLib2Error
        self.url = url
        self.request_opts = request_opts
        self.auth_type = "basic_auth" if basic_auth else ("form_auth" if form_auth else None)
        self.auth = basic_auth if basic_auth else (form_auth if form_auth else None)

        self.http = httplib2.Http(**http_opts)
        if self.auth_type == "basic_auth":
            self.http.add_credentials(self.auth["username"], self.auth["password"])
        elif self.auth_type == "form_auth":
            if "url" not in self.auth:
                raise PlantUMLError(
                    "The form_auth option 'url' must be provided and point to the login url."
                )
            if "body" not in self.auth:
                raise PlantUMLError(
                    "The form_auth option 'body' must be provided and include "
                    "a dictionary with the form elements required to log in. "
                    "Example: form_auth={'url': 'http://example.com/login/', "
                    "'body': { 'username': 'me', 'password': 'secret'}"
                )
            login_url = self.auth["url"]
            body = self.auth["body"]
            method = self.auth.get("method", "POST")
            headers = self.auth.get(
                "headers", {"Content-type": "application/x-www-form-urlencoded"}
            )

            try:
                response, content = http.request(
                    login_url, method, headers=headers, body=urllib.parse.urlencode(body)
                )
            except self.HttpLib2Error as e:
                raise PlantUMLConnectionError(e)
            if response.status != 200:
                raise PlantUMLHTTPError(response, content)
            self.request_opts["Cookie"] = response["set-cookie"]

    def get_url(self, plantuml_text):
        """Return the server URL for the image.
        You can use this URL in an IMG HTML tag.
        
        :param str plantuml_text: The plantuml markup to render
        :returns: the plantuml server image URL
        """
        return self.url + deflate_and_encode(plantuml_text)

    def processes(self, plantuml_text):
        """Processes the plantuml text into the raw PNG image data.
        
        :param str plantuml_text: The plantuml markup to render
        :returns: the raw image data
        """
        url = self.get_url(plantuml_text)
        try:
            response, content = self.http.request(url, **self.request_opts)
        except self.HttpLib2Error as e:
            raise PlantUMLConnectionError(e)
        if response.status != 200:
            raise PlantUMLHTTPError(response, content)
        return content

    def processes_file(self, filename, outfile=None, errorfile=None):
        """Take a filename of a file containing plantuml text and processes
        it into a .png image.
        
        :param str filename: Text file containing plantuml markup
        :param str outfile: Filename to write the output image to. If not
                    supplied, then it will be the input filename with the
                    file extension replaced with '.png'.
        :param str errorfile: Filename to write server html error page
                    to. If this is not supplined, then it will be the
                    input ``filename`` with the extension replaced with
                    '_error.html'.
        :returns: ``True`` if the image write succedded, ``False`` if there was
                    an error written to ``errorfile``.
        """
        if outfile is None:
            outfile = os.path.splitext(filename)[0] + ".png"
        if errorfile is None:
            errorfile = os.path.splitext(filename)[0] + "_error.html"
        data = open(filename, "U").read()
        try:
            content = self.processes(data)
        except PlantUMLHTTPError as e:
            err = open(errorfile, "w")
            err.write(e.content)
            err.close()
            return False
        out = open(outfile, "wb")
        out.write(content)
        out.close()
        return True


if __name__ == "__main__":
    pl = PlantUML()
    for filename in sys.argv[1:]:
        print(filename + ":", end=" ")
        if pl.processes_file(filename):
            print("success.")
        else:
            print("failure.")
