from ServerSimple import SimpleServer

class Server(SimpleServer):
    def __init__(self, host, port):
        SimpleServer.__init__(self, host, port)

    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)

    def StartServer(self):
        print "starting server thread..."
        self.serveforever()

    def handle(self, path, method, request, response):
        #print path, method, request, response
        cmd = path[0]
        if cmd == 'hi':
            return "hi there"
        elif cmd == 'hello':
            return "oh - we are being formal are we?  Hello!"
        else:
            # do the default
            return SimpleServer.handle(self, path, method, request, response)

if __name__ == '__main__':
    s = Server('localhost', 8081)
    s.StartServer()
