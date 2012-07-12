"""
Attempt to sketch the whole hexmvc thing out simply.
"""

import sys; sys.path.append("../lib"); sys.path.append("../hexagon3")
from architecture_support import *
import abc

class HexAdapter(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def SetApp(self, app): pass

#
# Ring Adapter Classes
#

# MODEL

class IModel(HexAdapter):
    @abc.abstractmethod
    def Clear(self): pass
    @abc.abstractmethod
    def GetModelSize(self): pass
    @abc.abstractmethod
    def AddThing(self, info): pass
    
class Model(IModel): 
    def __init__(self):
        self.things = []
        self.observers = multicast()
        self.Clear()

    def __str__(self):
        return str([str(t) for t in self.things])

    def SetApp(self, app):
        self.app = app
        self.observers.addObserver(app)
        self.observers.addObserver(app.gui)

    def Clear(self):
        self.things = []
        self.observers.notifyOfModelChange(None, self.GetModelSize())

    def GetModelSize(self):
        return len(self.things)

    def AddThing(self, info):
        thing = Thing(info)
        self.things.append(thing)
        self.observers.notifyOfModelChange(thing, self.GetModelSize())
        return thing

class Thing:
    def __init__(self, info):
        self.info = info
        
    def __str__(self):
        return "Thing!-" + self.info

    def AddInfo(self, msg):
        self.info += " " + msg

class IModelDependencies(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def notifyOfModelChange(self, thing, modelsize): pass
    
    
# SERVER

from bottle import route, run, template, request
import thread


class IServer(HexAdapter):
    @abc.abstractmethod
    def StartServer(self): pass
    @abc.abstractmethod
    def GetUrlOrigin(self): pass

class Server(IServer):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
    def SetApp(self, app):
        self.app = app
        
    def GetUrlOrigin(self):
        return "http://%s:%s" % (self.host, self.port)
        
    def StartServer(self):
        #thread.start_new_thread(self._Serve, ())
        pass

    @route('/getinfo')
    def ajax():
        #return template('ajax1')
        return 'The model length is %d' % self.app.GetModelSize()

class IServerDependencies(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def GetModelSize(self): pass

# GUI

import wx
import wx.lib.mixins.inspection  # Ctrl-Alt-I 
from hexmvcgui_gen import HexMvcGuiFrame1
import thread, time
import random

class IGui(HexAdapter):
    @abc.abstractmethod
    def AddThing(self, event): pass
    
class MyFrame(HexMvcGuiFrame1, IGui, IModelDependencies):
    def __init__( self, parent ):
        HexMvcGuiFrame1.__init__( self, parent )
        self.need_abort = False

    def SetApp(self, app):
        self.app = app
        print "app has been set"
        #self._InitHyperlinks()

    # IModelDependencies
    
    def notifyOfModelChange(self, thing, modelsize):
        print "Gui observer got notified"
        self.m_listBox1.Append(str(thing), thing)

    # Gui Generated Events, override the handler here
    
    def AddThing(self, event):
        info = str(random.randint(0,99999))
        thing = self.app.AddThing(info)
        #self.m_listBox1.Append(str(thing), thing) # notification now does this.
        
class MyWxApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        frame = MyFrame(parent=None)
        frame.Show()
        self.myframe = frame
        return True

class IGuiDependencies(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def AddThing(self, info): pass


#
# Central App
#

assert issubclass(Model, IModel)
assert issubclass(Server, IServer)
assert issubclass(MyFrame, IGui)

class IApp(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def Boot(self): pass
    
class App(IApp, IModelDependencies, IServerDependencies, IGuiDependencies):
    def __init__(self, model, server, gui):

        assert isinstance(model, IModel)
        assert isinstance(server, IServer)
        assert isinstance(gui, IGui)
        
        self.model = model
        self.server = server
        self.gui = gui

        model.SetApp(self)
        server.SetApp(self)
        gui.SetApp(self)
        
    def Boot(self):
        self.server.StartServer()

    def AddThing(self, info):
        thing = self.model.AddThing(info)
        return thing

    def GetModelSize(self):
        return 100
    
    def notifyOfModelChange(self, thing, modelsize):
        print "App observer got notified, added value %(thing)s - modelsize now %(modelsize)4d" % vars()
        
#
# Wiring up
#

# Create Gui
wxapp = MyWxApp(redirect=False)
gui = wxapp.myframe  # arguably too wx based to be a true adapter, but as long
                     # as we call nothing wx specific, it acts as an adapter ok.
# Create Server
server = Server(host='localhost', port=8081)

# Create Model - SIMPLE
model = Model()

# Create Core Hexagon App and inject adapters
app = App(model, server, gui)
wx.CallAfter(app.Boot)

# Start Gui
wxapp.MainLoop()

print "DONE"
