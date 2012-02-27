import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Windows.Forms import Application
import MainForm

import sys 
sys.path.append("c:\python27\lib")
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
	from ServerMock import Server
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

	# Create Core Hexagon App and inject adapters
	app = App(model, server, gui)


except Exception, inst:
	print inst

Application.Run(form)
