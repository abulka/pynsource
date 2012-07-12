from bottle import debug, route, run, request
@route('/:name')
def index(name='World'):
    return '<b>Hello %s!</b>' % name
debug(True)
run(reloader=True, host='localhost', port=8080)


"""
https://github.com/defnull/bottle/issues?sort=created&direction=desc&state=open&page=1

https://github.com/defnull/bottle/issues/155

I also am having problems with the reload behavior under window 7.  Even with the most basic example

```python
from bottle import debug, route, run, request
@route('/:name')
def index(name='World'):
    return '<b>Hello %s!</b>' % name
debug(True)
run(reloader=True, host='localhost', port=8080)
```

If I 

* run the above in a cmd window, 
* issue a browser request, it works
* then kill the server with ^C 
* then issue another browser request 

then I get a exception stack appearing in my in my command window!  Never seen anything like that before.  Thought I'd killed the server.

```python
--------------------
Exception happened during processing of request from ('127.0.0.1', 16448)
Traceback (most recent call last):
  File "C:\Python26\lib\SocketServer.py", line 281, in _handle_request_noblock
    self.process_request(request, client_address)
  File "C:\Python26\lib\SocketServer.py", line 307, in process_request
    self.finish_request(request, client_address)
  File "C:\Python26\lib\SocketServer.py", line 320, in finish_request
    self.RequestHandlerClass(request, client_address, self)
  File "C:\Python26\lib\SocketServer.py", line 615, in __init__
    self.handle()
  File "C:\Python26\lib\wsgiref\simple_server.py", line 130, in handle
    self.raw_requestline = self.rfile.readline()
  File "C:\Python26\lib\socket.py", line 404, in readline
    data = self._sock.recv(self._rbufsize)
KeyboardInterrupt
----------------------------------------
```

Then if I reissue the browser request once again, the server starts up - again, weirdly, in my command window.  And the browser request succeeds. BUT the source is not re-parsed, I get the same server behavior even if I change the source code.  So despite the weirdness, the reload of source is not even achieved, which is the whole point of reloader.

## Other related behaviour:

If I kill the server in my command window with ^Break then it **does** die properly and doesn't restart when I send another browser request.

If I start the server and then kill it with ^C without a browser request ever occurring, the server **does not** attempt to restart.

## Other related behaviour part II - removing the reloader=True from the above sample code

Run the server, browse, everything works.
Hitting ^C doesn't kill the server however - or at least it doesn't appear to.
Browse the request again, I see a stack trace.
Browse the request again, server runs/restarts itself again.  Note I don't have reloader= in this version of my code.
As usual ^Break kills the server properly.

"""
