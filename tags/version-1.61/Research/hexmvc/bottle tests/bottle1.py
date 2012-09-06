from bottle import debug, route, run, request

@route('/:name')
def index(name='World'):
    return '<b>Helloooo %s!!</b>' % name

debug(True)
run(host='localhost', port=5000)  # reloader=True behaves strangely, restarts the server when there is a
                    # web request, even though its killed!  Also, source is not reparsed, so whats the point.
                    # might be a windows thing.
