from ModelOo import Model
from ModelOoAdapter import ModelOoAdapter
#from PersistenceOoPickle import Persistence
from PersistenceOoHomegrown import Persistence
from ServerBottleAdapter import Server
from ViewWxAdapter import MyWxApp
import wx
from App import App

# Create Model - SIMPLE
model_oo = Model()
persistence = Persistence()
model = ModelOoAdapter(model_oo, persistence)

# Create Server
server = Server(host='localhost', port=8081)

# Create Gui
wxapp = MyWxApp(redirect=False)
gui = wxapp.myframe  # gui mediator inherits from gui rather than wrapping it, in this implementation

# Create Core Hexagon App and inject adapters
app = App(model, server, gui)
wx.CallAfter(app.Boot)

# Start Gui
wxapp.MainLoop()

print "DONE"
