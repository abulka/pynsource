# HEXMVC BOOT WIRING v3 - model is separate

from hexapp import App
from hexserver import Server1
from hexmvcgui import MyWxApp
import wx

# Create Gui
wxapp = MyWxApp(redirect=False)
gui = wxapp.myframe  # arguably too wx based to be a true adapter, but as long
# as we call nothing wx specific, it acts as an adapter ok.
# Create Server
server = Server1(host="localhost", port=8081)

SIMPLE = False

if SIMPLE:
    # Create Persistence
    # Create Model - SIMPLE
    from hexmodel_simple import Model
    from hexpersistence import PersistenceMock2

    persistence = PersistenceMock2()
    model = Model(persistence)
else:
    # Create Model - SQLOBJECT
    from sqlobject.sqlite import builder
    from sqlobject import sqlhub

    SQLiteConnection = builder()
    conn = SQLiteConnection("hexmodel_sqlobject.db", debug=False)
    sqlhub.processConnection = conn
    from hexmodel_sqlobject import Model, Thing

    try:
        model = Model.get(1)
        thing = Thing.get(1)
    except:
        print("Oops - possible no database - creating...")
        Model.dropTable(True)
        Model.createTable()
        Thing.dropTable(True)
        Thing.createTable()

        model = Model()
        thing1 = Thing(info="mary", model=model)
        thing2 = Thing(info="fred", model=model)

        model = Model.get(1)

    persistence = None

# Create Core Hexagon App and inject adapters
app = App(model, server, gui)
wx.CallAfter(app.Boot)

# Start Gui
wxapp.MainLoop()

print("DONE")
