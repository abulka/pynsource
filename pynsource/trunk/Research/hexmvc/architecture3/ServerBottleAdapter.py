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

        # REST API

        @route('/jsontest')
        def jsontest():
            import time
            return {'status':'online', 'servertime':time.time()}
    
        """
        REST API DESIGN

        Need to expose some sort of referencing scheme to refer to thing objects.
            In Oo version the memory address? Do we need to actually create an integer id for the oo version?
            In Sql version the db id?
        
        GET /things
            Example:
                GET http://localhost:8081/things
            Comment:
                like dumpthings except offers list of (id, link)
            XML:
                <thinglink info="blah" href="http://localhost:8081/things/1"/>
                <thinglink info="blah2" href="http://localhost:8081/things/2"/>

        GET /things/id
            Example:
                GET http://localhost:8081/things/1
            Comment:
                display just the thing object. Should we include the id in the xml or
                the fact that its on the url enough?
            XML:
                <thing id="1">thing info content here</thing>
            JSON:
                {'id':"1", 'info':"thing info content here"}

        POST /things, thing
            Example:
                POST http://localhost:8081/things, <thing>thing2 info content here</thing>
            Comment:
                Adds a thing.  We get a link back e.g. http://localhost:8081/things/2

        PUT /things/id, thing
            Example:
                POST http://localhost:8081/things/1, <thing>thing MODIFIED info content here</thing>
            Comment:
                Modifes a thing.
                
        DELETE /things/id
            Example:
                DELETE http://localhost:8081/things/1
            Comment:
                Deletes a thing.
                
        P.S. Useful Chrome plugins:
            Simple REST Client
            JSON formatter
        """
        
        run(host=self.host, port=self.port)
        # nothing runs after this point
