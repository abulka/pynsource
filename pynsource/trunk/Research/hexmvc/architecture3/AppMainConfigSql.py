from ModelSimple import Model
from ModelProxySql import ModelProxySqlObject
from ServerBottle import Server
from ViewWxMediator import MyWxApp
import wx
from App import App

# Create Model - SQLOBJECT
model = ModelProxySqlObject(ModelProxySqlObject.GetModel())

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
