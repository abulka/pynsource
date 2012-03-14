from architecture_support import *
from ServerDotnet import SimpleServer
from System.Threading import ThreadStart, Thread

class Server(SimpleServer):
    def __init__(self, host, port):
        SimpleServer.__init__(self, host, port)
        self.app = None  # inject
        self.model = None  # inject
        self.thread_id = None
        self.observers = multicast()

    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)

    def StopServer(self):
        print "stopping server thread..."
        if self.thread_id:
            self.thread_id.Abort()
            self.thread_id = None

    def StartServer(self):
        print "starting server thread..."
        self.thread_id = Thread(ThreadStart(self.serveforever))
        self.thread_id.Start()

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
