from bottle import route, run, template, request
import thread

class Server1:
    def StartServer(self):
        thread.start_new_thread(self._DoSomeLongTask2, ())
        
    def _DoSomeLongTask2(self):
        
        @route('/hello')
        @route('/hello/:name')
        def hello(name='World'):
            return template('hello_template', name=name)

        @route('/ajax')
        def ajax():
            return template('ajax1')

        @route('/ajax_info1')
        def ajax_info1():
            print "ajax request"
            try:
                if request.is_ajax:
                    return 'This is an AJAX request'
                else:
                    return 'This is a normal request'
            except:
                print "some exception"
                return 'AJAX some exception!!'
                
        @route('/:name')
        def index(name='World'):
            return '<b>Hello %s!</b>' % name

    
        run(host='localhost', port=8080)
        # nothing runs after this point
        
if __name__ == "__main__":
    s = Server1()
    s._DoSomeLongTask2()
    