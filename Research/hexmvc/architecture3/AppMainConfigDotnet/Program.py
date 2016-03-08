import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Windows.Forms import Application
import ViewDotnetWinForm

import sys

# Use Python Standard Library
fp = open("app_python_location.config")
label, python_lib_path = fp.readline().strip().split('=')
fp.close()
sys.path.append(python_lib_path) # e.g. "c:\python26\lib")
#import os 
#print os.getcwd() 

import System.Console
#System.Console.Clear()    
System.Console.WriteLine("Wiring app...")

try:
    sys.path.append("..")
    sys.path.append("../../lib")

    from ModelOo import Model
    from ModelOoAdapter import ModelOoAdapter
    
    #from PersistenceOoPickle import Persistence
    from PersistenceOoHomegrown import Persistence
    
    #from ServerMockAdapter import Server
    from ServerDotnetAdapter import Server
    
    from UtilRandomDotnetAdapter import RandomIntFunction
    #from UtilRandomStdpythonAdapter import RandomIntFunction
    
    from UtilJsonDotnetAdapter import JsonFromDictFunction
    
    from App import App
    import ViewDotnetWinFormAdapter
    
    # Create Model - SIMPLE
    model_oo = Model()
    persistence = Persistence()
    model = ModelOoAdapter(model_oo, persistence)

    # Create Server
    server = Server(host='localhost', port=8081)

    # Create Gui
    Application.EnableVisualStyles()
    form = ViewDotnetWinFormAdapter.WinFormAdapter()
    gui = form

    # Wire in random utility function
    gui.random = RandomIntFunction
    server.json_from_dict = JsonFromDictFunction

    # Create Core Hexagon App and inject adapters
    app = App(model, server, gui)
    gui.callAfter = app.Boot

except Exception, inst:
    print inst

Application.Run(form)
