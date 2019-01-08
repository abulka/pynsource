from ModelSqlAdapter import ModelSqlObjectAdapter

from ServerBottleAdapter import Server
#from ServerMockAdapter import Server

from ViewWxAdapter import MyWxApp
from UtilRandomStdpythonAdapter import RandomIntFunction
import wx
from App import App

# Create Model - SqlObject
model_sql = ModelSqlObjectAdapter.GetModel()
model = ModelSqlObjectAdapter(model_sql)

# Create Server
server = Server(host='localhost', port=8081)

# Create Gui
wxapp = MyWxApp(redirect=False)
gui = wxapp.myframe  # gui mediator inherits from gui rather than wrapping it, in this implementation

# Hook up Utility adapters
gui.random = RandomIntFunction

# Create Core Hexagon App and inject adapters
app = App(model, server, gui)
wx.CallAfter(app.Boot)

# Start Gui
wxapp.MainLoop()
print("DONE")

# Stops any background server threads.
import sys
sys.exit()
