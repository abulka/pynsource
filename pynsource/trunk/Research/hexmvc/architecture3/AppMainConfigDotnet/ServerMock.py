class Server(object):
    def __init__(self, host, port):
        self.app = None
        self.model = None
        self.host = host
        self.port = port
        
    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)
        
    def StartServer(self):
    	print "Mock server started"
