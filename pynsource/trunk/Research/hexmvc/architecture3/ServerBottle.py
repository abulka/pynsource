from bottle import route, run, template, request
import thread

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
        thread.start_new_thread(self._Serve, ())

    def _Serve(self):
        print "starting server thread..."

        @route('/')
        def index():
            return "G'day"
        
        @route('/modelsize')
        def modelsize():
            return 'The model length is %d' % self.model.size

        @route('/dumpthings')
        def dumpthings():
            s = ""
            for thing in self.model.things:
                s += str(thing) + '<BR>'
            return s

        run(host=self.host, port=self.port)
        # nothing runs after this point
