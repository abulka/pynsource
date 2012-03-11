import sys; sys.path.append("../lib")
from architecture_support import *

from bottle import route, run, template, request
import thread

class Server(object):
    def __init__(self, host, port):
        self.app = None
        self.model = None
        self.host = host
        self.port = port
        self.thread_id = None
        self.observers = multicast()
        
    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)
        
    def StartServer(self):
        self.thread_id = thread.start_new_thread(self._Serve, ())

    def StopServer(self):
        print "stopping server thread..." # actually cannot kill python threads!?
        
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

        @route('/addthing')
        def addthing():
            self.observers.CMD_ADD_THING("fred")
            return 'The model length is now %d' % self.model.size

        @route('/json')
        def json():
            import time
            return {'status':'online', 'servertime':time.time()}
    
        run(host=self.host, port=self.port)
        # nothing runs after this point
