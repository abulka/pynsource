from ServerSimple import SimpleServer

class Server(SimpleServer):
    def __init__(self, host, port):
        SimpleServer.__init__(self, host, port)

    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)

    def StartServer_real(self):
        print "starting server thread..."
        self.serveforever()

    def StartServer(self):
        pass
#        print "starting server thread..."
#        self.serveforever()

    def handle(self, path, method, request, response):
        #print path, method, request, response
        cmd = path[0]
        
        if cmd == '':
            return "G'day"
        elif cmd == 'modelsize':
            return 'The model length is %d' % self.model.size
        elif cmd == 'dumpthings':
            s = ""
            for thing in self.model.things:
                s += str(thing) + '<BR>'
            return s
        else:
            # do the default
            return SimpleServer.handle(self, path, method, request, response)

if __name__ == '__main__':
    s = Server('localhost', 8081)
    s.StartServer()
