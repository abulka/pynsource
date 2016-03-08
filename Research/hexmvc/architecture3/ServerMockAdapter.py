from architecture_support import *

class Server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.app = None  # inject
        self.model = None  # inject
        self.thread_id = None
        self.observers = multicast()
        
    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)
        
    def StartServer(self):
    	print "Mock server started"

    def StopServer(self):
        print "Stopped Mock server"
        