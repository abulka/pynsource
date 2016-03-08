from System import AsyncCallback
from System.Net import HttpListener, HttpListenerException
from System.Text import Encoding

class SimpleServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def serveforever(self):
        self.failed = False
        listener = HttpListener()
        
        prefix = 'http://%s:%s/' % (self.host, str(self.port))
        listener.Prefixes.Add(prefix)
        
        try:
            listener.Start()
        except HttpListenerException:
            self.failed = True
            return

        while True:
            result = listener.BeginGetContext(AsyncCallback(self.handleRequest), listener)
            result.AsyncWaitHandle.WaitOne()

    def pathComponents(self, context):
        url = context.Request.RawUrl.strip('/')      # We make use of request.RawUrl
        return url.split('/')

    def handleRequest(self, result):
        listener = result.AsyncState
        try:
            context = listener.EndGetContext(result)
        except:
            # Catch the exception when the thread has been aborted
            return

        request = context.Request
        response = context.Response
        path = self.pathComponents(context)
        method = context.Request.HttpMethod
        print method, path
        """
        if you call with http://localhost:8081 path='' method=GET
        if you call with http://localhost:8081/fred path='fred' method=GET
        """

        text = self.handle(path, method, request, response)
        
        buffer = Encoding.UTF8.GetBytes(text)
        response.ContentLength64 = buffer.Length
        output = response.OutputStream
        output.Write(buffer, 0, buffer.Length)
        output.Close()

    # Subclasses to override this.
    def handle(self, path, method, request, response):
        url = '<P><STRONG>URL Requested: %s</STRONG></P>' % request.RawUrl
        pagesServed = '<P><STRONG>Number of Pages Served: %s</STRONG></P>' % 999
        text = """
        <HTML>
        <HEAD><TITLE>Welcome to the Simple Server</TITLE></HEAD>
        <BODY><STRONG><H1>Welcome to the Simple Server</H1>%s</STRONG></BODY>
        </HTML>
        """
        return text % (url + pagesServed)

if __name__ == '__main__':
    s = SimpleServer('localhost', 8081)
    s.serveforever()
