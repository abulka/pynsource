from architecture_support import *
from ServerSimple import SimpleServer
from System.Threading import ThreadStart, Thread

class Server(SimpleServer):
    def __init__(self, host, port):
        SimpleServer.__init__(self, host, port)
        self.observers = multicast()

    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)

    def StopServer(self):
        print "stopping server thread..."
        self.t.Abort()

    def StartServer(self):
        print "starting server thread..."
        self.t = Thread(ThreadStart(self.serveforever))
        self.t.Start()

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
        elif cmd == 'addthing':
            self.observers.CMD_ADD_THING("fred")
            return 'The model length is now %d' % self.model.size        
        else:
            # do the default
            return SimpleServer.handle(self, path, method, request, response)

if __name__ == '__main__':
    s = Server('localhost', 8081)
    s.StartServer()
