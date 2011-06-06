# HEXMVC BOOT WIRING

from hexappmodel import App, Thing
from hexpersistence import PersistenceMock2
from hexserver import Server1
from hexmvcgui import MyFrame, MyApp
import wx

# Create Gui
#wxapp = wx.App(redirect=False)
#frame = MyFrame(None)

myapp = MyApp(redirect=False)

#app = App(persistence=PersistenceMock2(), server=Server1(), gui=frame)
app = App(persistence=PersistenceMock2(), server=Server1(), gui=myapp.myframe)


# Start server
#app.server.StartServer()
wx.CallAfter(app.server.StartServer)

# Start Gui
#frame.Show()
#wxapp.MainLoop()
print "myapp.MainLoop()"
myapp.MainLoop()

print "DONE"

