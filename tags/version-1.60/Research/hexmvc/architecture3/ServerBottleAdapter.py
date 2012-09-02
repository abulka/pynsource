import sys; sys.path.append("../lib")
from architecture_support import *

from bottle import route, run, template, request, response, get, post, put, delete  # easy_install -U bottle
import thread
import wx # for mutex under linux so can update gui via app

class Server(object):
    def __init__(self, host, port):
        self.app = None  # inject
        self.model = None # inject
        self.host = host
        self.port = port
        self.thread_id = None
        self.observers = multicast()
        self.json_from_dict = None  # inject
        
    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)
        
    def StartServer(self):
        self.thread_id = thread.start_new_thread(self._Serve, ())

    def StopServer(self):
        print "stopping server thread..." # actually cannot kill python threads!?
        
    def _Serve(self):
        print "starting server thread..."

        def report_error(inst):
            msg = "Server exception: %s" % inst
            print msg
            return msg

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

        # JSON

        @route('/jsontest')
        def jsontest():
            import time
            return {'status':'online', 'servertime':time.time()}

        # REST API
        
        @get('/things')
        def things():
            """
            GET /things
            Comment: List of things in json format, incl. link to full object. e.g.
                { "things": [ {"info": "some thing", "link": "http://localhost:8081/things/1", "id": 1},
                              {"info": "another thing", "link": "http://localhost:8081/things/2", "id": 2}
                            ]}
            Example: GET http://localhost:8081/things
            """
            try:
                return self.app.controller.CmdGetThingsAsDict()  # no need to call self.json_from_dict as bottle handles it
            except Exception, inst:
                return report_error(inst)

        @get('/things/:id')
        def things_id(id):
            """
            GET /things/id
            Comment: Displays just the one thing object. The id is supplied for convenience
                     even though its also on the url. e.g. {"id":1, "info":"thing info content here"}
            Example: GET http://localhost:8081/things/1
            """
            try:
                return self.app.controller.CmdGetThingAsDict(id)  # no need to call self.json_from_dict as bottle handles it
            except Exception, inst:
                return report_error(inst)

        @post('/things')
        def things_post():
            """
            POST /things, thing
            Comment: Adds a thing.
                     We get a link back e.g. http://localhost:8081/things/2
            Example: POST http://localhost:8081/things, info=thing+info+content+here
            Note: Is there a way to send json to the server? e.g. {"info":"thing info content here"}
            """
            try:
                print request.headers.get('X-Requested-With') # typically 'XMLHttpRequest'
                print request.headers.get('Content-Type')
                content_type = request.headers.get('Content-Type');

                if content_type == 'application/json':
                    info = request.json["info"]
                elif content_type == 'application/x-www-form-urlencoded':
                    info = request.forms["info"]

                dict = self.app.controller.CmdAddThing(info)  # no need to call self.json_from_dict as bottle handles it
                return dict
            except Exception, inst:
                return report_error(inst)

        @put('/things')
        def thing_put():
            """
            PUT /things, thing
            Comment: Modifes a thing.
            Example: POST http://localhost:8081/things, id=1&info=fred
               Note: Is there a way to send json to the server? e.g. {"id":1, "info":"MODIFIED info content here"}
            """
            try:
                content_type = request.headers.get('Content-Type');
                if content_type == 'application/json':
                    print 'JSON REQUEST'
                    id = request.json.get("id")
                    info = request.json.get("info")
                else:
                    print 'FORM REQUEST'
                    id = request.forms.get("id")
                    info = request.forms.get("info")

                dict = self.app.controller.CmdModifyThing(id, info)  # no need to call self.json_from_dict as bottle handles it
                return dict
            except Exception, inst:
                return report_error(inst)

        @delete('/things/:id')
        def thing_delete(id):
            """
            DELETE /things/id
            Comment: Deletes a thing.
            Example: DELETE http://localhost:8081/things/1
            """
            try:
                return self.app.controller.CmdDeleteThing(id)
            except Exception, inst:
                return report_error(inst)
            
            
        # REST API - Support
            
        @route('/api')
        def modify_form():
            """
            POST is done via normal form submit post.
            PUT and DELETE are not supported in normal forms, so we have to do it via ajax
            """
            return '''
<!DOCTYPE html>

<html>
<head>
    <title>Put and Delete</title>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <meta http-equiv="content-script-type" content="text/javascript">
    <script>

    $(document).ready(function() {
        $("#PutForm input[type=button]").click(function (e) {
            //console.log("PUT " + $("#PutForm input[name=id]").attr('value') + " " + $("#PutForm input[name=info]").attr('value'));
            $.ajax({type:'PUT', url: 'things', data:$('#PutForm').serialize(), success: function(response) {
                $('#PutForm').find('.form_result').html(response);
            }});
        });
        $("#DeleteForm input[type=button]").click(function (e) {
            id = $("#DeleteForm input[name=id]").attr('value');
            $.ajax({type:'DELETE', url: 'things/'+id, data:$('#DeleteForm').serialize(), success: function(response) {
                $('#DeleteForm').find('.form_result').html(response);
            }});
        });

        /*
        $('a').click(function(){ 
           console.log("hyperlink click!"); 
        });
        */
        
        $("#postjson").click(function (e) {
        
            var thing = {info:"thing info content here"};
            
            // convert object to JSON string  (See http://jollytoad.googlepages.com/json.js)
            var objectAsJson = JSON.stringify(thing); // result is a string:  '{"Name":"Fred","Rank":"2","SerialNumber":"17268"}'
            console.log(objectAsJson );
            
            $.ajax({
              type        : "POST",
              contentType : "application/json",
              url         : "things",
              data        : objectAsJson, 
              processData : false,              // do not convert outbound data to string (already done)
              success     : function(response){ $('#PostForm').find('.form_result').html(response); },
              error       : function(xhr, textStatus, errorThrown){  } 
             });
             return false;
        });

        $("#putjson").click(function (e) {
        
            var thing = {id:1, info:"QQ"};
            var objectAsJson = JSON.stringify(thing);
            console.log(objectAsJson );
            
            $.ajax({
              type        : "PUT",
              contentType : "application/json",
              url         : "things",
              data        : objectAsJson, 
              processData : false,              // do not convert outbound data to string (already done)
              success     : function(response){ $('#PutForm').find('.form_result').html(response); },
              error       : function(xhr, textStatus, errorThrown){ $('#PutForm').find('.form_result').html("some error"); } 
             });
             return false;             
        });
        
    });
    
    </script>
</head>

<body>
    <p><a href="/things">/things</a></p>
    <p><a href="" id="postjson">post json object</a></p>
    <p><a href="" id="putjson">put json object to 1</a></p>
    
    <form id="PostForm" action="/things" method="POST">
        info: <input type="text" name="info" value="Some info" /><br/> 
        <input type="submit" value="POST"><br><br>
        <div class="form_result"> </div>
    </form>
    <form id="PutForm" >
        id: <input type="text" name="id" value="1" /><br/> 
        info: <input type="text" name="info" value="Hi" /><br/> 
        <input type="button" value="PUT"><br><br>
        <div class="form_result"> </div>
    </form>
    <form id="DeleteForm" >
        id: <input type="text" name="id" value="1" /><br/> 
        <input type="button" value="DELETE">
        <div class="form_result"> </div>
    </form>

</body>
</html>
'''
    

        run(host=self.host, port=self.port)
        # nothing runs after this point
