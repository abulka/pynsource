# HEXMVC BOOT WIRING

from hexappmodel import App, Thing
from hexpersistence import PersistenceMock2
from hexserver import Server1
from hexmvcgui import MyWxApp
import wx

# Create Gui
wxapp = MyWxApp(redirect=False)
gui = wxapp.myframe  # arguably too wx based to be a true adapter, but as long
                     # as we call nothing wx specific, it acts as an adapter ok.
# Create Server
server = Server1()

# Create Persistence
persistence = PersistenceMock2()

# Create Core Hexagon App and inject adapters
app = App(persistence, server, gui)

# Start server
#wx.CallAfter(app.server.StartServer)
wx.CallAfter(app.Boot)

# Start Gui
wxapp.MainLoop()

print "DONE"
