from bottle import route, run, template, request
import thread

class Server1:
    def SetApp(self, app):
        self.app = app
        
    def StartServer(self):
        thread.start_new_thread(self._Serve, ())
        
    def _Serve(self):
        print "starting server thread..."
        
        @route('/hello')
        @route('/hello/:name')
        def hello(name='World'):
            return template('hello_template', name=name)

        @route('/ajax')
        def ajax():
            return template('ajax1')

        @route('/ajax_info1')
        def ajax_info1():
            #print "ajax request"
            try:
                if request.is_ajax:
                    return 'This is an AJAX request, model length is %d' % len(self.app.model)
                else:
                    return 'This is a normal request'
            except Exception as inst:
                print "Exception!," + type(inst)     # the exception instance
                print inst           # __str__ allows args to printed directly
                #print inst.args      # arguments stored in .args
                #print traceback.print_exc()

                return 'AJAX some exception!!!'
                
        @route('/:name')
        def index(name='World'):
            return '<b>Hello %s!</b>' % name

    
        run(host='localhost', port=8081)
        # nothing runs after this point
        
if __name__ == "__main__":
    class MockModel:
        def __len__(self):
            return 999
    class MockApp:
        def __init__(self):
            self.model = MockModel()
            
    s = Server1()
    s.SetApp(MockApp())
    s._Serve()
    