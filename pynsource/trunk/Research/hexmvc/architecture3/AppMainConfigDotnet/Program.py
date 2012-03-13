import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Windows.Forms import Application
import ViewDotnetWinForm

import sys 
#sys.path.append("c:\python27\lib")
sys.path.append("c:\python26\lib")

# Use Python Standard Library os module. 
#import os 
#print os.getcwd() 
import System.Console
#System.Console.Clear()    
#print System.Console
System.Console.WriteLine("Wiring app...")

try:
    sys.path.append("..")
    sys.path.append("../../lib")

    from ModelOo import Model
    from ModelOoAdapter import ModelOoAdapter
    
    #from PersistenceOoPickle import Persistence
    from PersistenceOoHomegrown import Persistence
    
    #from ServerMock import Server
    from ServerDotnetAdapter import Server
    
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

    # Wire in random function
    def r1(n,m): 
        import random
        print "python random"
        return random.randint(n,m)
    def r2(n,m):
        import System.Random
        print "dot net random"
        return System.Random().Next(m)
    gui.getRandomInt = r2

    # Create Core Hexagon App and inject adapters
    app = App(model, server, gui)
    gui.callAfter = app.Boot

except Exception, inst:
    print inst

Application.Run(form)

"""
On randomness....

# set IRONPYTHONPATH=c:\Python26\Lib
# see http://stackoverflow.com/questions/2984561/module-random-not-found-when-building-exe-from-ironpython-2-6-script

#from System import Environment
#pythonPath = Environment.GetEnvironmentVariable("IRONPYTHONPATH")
#import sys
#sys.path.append(pythonPath)
#print pythonPath

#import sys
#sys.path.append(r'lib_andy_python')

import random

import System.Random
r = System.Random().Next(10000)
print r
"""
