from bottle import route, run, template, request
import _thread


class Server1:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def SetApp(self, app):
        self.app = app

    def GetUrlOrigin(self):
        return "http://%s:%s" % (self.host, self.port)

    def StartServer(self):
        _thread.start_new_thread(self._Serve, ())

    def _Serve(self):
        print("starting server thread...")

        @route("/")
        def index():
            return "G'day"

        @route("/xml")
        def xml():
            response.content_type = "xml/application"
            return "<a>blah</a>"

        @route("/hello")
        @route("/hello/:name")
        def hello(name="World"):
            return template("hello_template", name=name)

        @route("/ajax")
        def ajax():
            return template("ajax1")

        @route("/ajax_info1")
        def ajax_info1():
            # print "ajax request"
            try:
                if request.is_ajax:
                    return "This is an AJAX request, model length is %d" % self.app.GetModelSize()
                else:
                    return "This is a normal request"
            except Exception as inst:
                print("Exception!," + type(inst))  # the exception instance
                print(inst)  # __str__ allows args to printed directly
                # print inst.args      # arguments stored in .args
                # print traceback.print_exc()

                return "AJAX some exception!!!"

        @route("/:name")
        def index(name="World"):
            return "<b>Hello %s!</b>" % name

        run(host=self.host, port=self.port)
        # nothing runs after this point


if __name__ == "__main__":

    class MockModel:
        def __len__(self):
            return 999

    class MockApp:
        def __init__(self):
            self.model = MockModel()

        def GetModelSize(self):
            return len(self.model)

    s = Server1(host="localhost", port=8082)
    s.SetApp(MockApp())
    s._Serve()
