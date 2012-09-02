"""
Attempt to sketch the whole hexmvc thing out simply.
"""

import sys; sys.path.append("../lib")
from architecture_support import *

SIMPLE_MODEL = False #True

#
# Ring Adapter Classes
#

# MODEL

class ModelProxyBase(object):
    def __init__(self, model):
        self.app = None
        self.model = model
        self.observers = multicast()

    def Boot(self):
        self.observers.MODEL_CHANGED(self.things)

    def __str__(self):
        return str([str(t) for t in self.model.things])

    @property
    def size(self):
        return self.model.size

    @property
    def things(self):
        return self.model.things

    # Things you can do to the Model
    
    def Clear(self):
        self.model.Clear()
        self.observers.MODEL_CLEARED()

    def AddThing(self, info):
        thing = self.model.AddThing(info)
        self.observers.MODEL_THING_ADDED(thing, self.size)
        return thing

    def AddInfoToThing(self, thing, moreinfo):
        thing.AddInfo(moreinfo)
        self.observers.MODEL_THING_UPDATE(thing)

    def DeleteThing(self, thing):
        raise Exception("DeleteThing not implemented in proxy");

if SIMPLE_MODEL:

    # Simple (in memory) Model

    class Model(object):
        def __init__(self):
            self.things = []
    
        def Clear(self):
            self.things = []
            print "simple model cleared"

        def AddThing(self, info):
            thing = Thing(info)
            thing.model = self  # backpointer
            self.things.append(thing)
            return thing

        @property
        def size(self):
            return len(self.things)
    
    class Thing:
        def __init__(self, info):
            self.model = None  # backpointer
            self.info = info
            
        def __str__(self):
            return "Thing!-" + self.info
    
        def AddInfo(self, msg):
            self.info += " " + msg

    class ModelProxySimple(ModelProxyBase):
        def DeleteThing(self, thing):
            self.model.things.remove(thing)
            self.observers.MODEL_THING_DELETED(thing)

    print ModelProxySimple(None)

else:
    
    # SqlObject Model
    
    from sqlobject import *
    
    class Model(SQLObject):
        things = MultipleJoin('Thing')
    
        @property
        def size(self):
            return len(self.things)
            
        def Clear(self):
            for thing in self.things:
                Thing.delete(thing.id)

        def AddThing(self, info):
            thing = Thing(info=info, model=self)
            return thing
    
    class Thing(SQLObject):
        info = StringCol(length=50)
        model = ForeignKey('Model', default=None)

        def __str__(self):
            return "Thing@-: " + self.info
    
        def AddInfo(self, msg):
            self.info += " " + msg

    class ModelProxySqlObject(ModelProxyBase):
        def DeleteThing(self, thing):
            Thing.delete(thing.id)
            self.observers.MODEL_THING_DELETED(thing)
        
        @classmethod
        def GetModel(self):
            
            from sqlobject.sqlite import builder
            from sqlobject import sqlhub
            
            SQLiteConnection = builder()
            conn = SQLiteConnection('hexmodel_sqlobject.db', debug=False)
            sqlhub.processConnection = conn
            try:
                model = Model.get(1)
                #a_thing = Thing.get(1)
            except:
                print "Oops - possibly no database - creating one now..."
                Model.dropTable(True)
                Model.createTable()
                Thing.dropTable(True)
                Thing.createTable()
        
                the_model = Model()
                assert the_model == Model.get(1)
                #~ thing1 = Thing(info="mary", model=model)
                #~ thing2 = Thing(info="fred", model=model)
                
                model = Model.get(1)
                
            return model
            
# SERVER

from bottle import route, run, template, request
import thread

class Server(object):
    def __init__(self, host, port):
        self.app = None
        self.model = None
        self.host = host
        self.port = port
        
    @property
    def url_server(self):
        return "http://%s:%s" % (self.host, self.port)
        
    def StartServer(self):
        thread.start_new_thread(self._Serve, ())

    def _Serve(self):
        print "starting server thread..."

        @route('/')
        def index():
            return "G'day"
        
        @route('/modelsize')
        def modelsize():
            return 'The model length is %d' % self.model.size

        @route('/dumpthings')
        def dumpthings():
            s = ""
            for thing in self.model.things:
                s += str(thing) + '<BR>'
            return s

        run(host=self.host, port=self.port)
        # nothing runs after this point
        
# GUI

import wx
import wx.lib.mixins.inspection  # Ctrl-Alt-I 
import thread, time
import random

# GUI Form is auto generated by wxBuilder tool
from architecture2_gui_gen import GuiFrame
       
# GUI Mediator inherits rather than wraps the viewComponent, in this case, due
# to the way wxBuilder sends us events - expecting us to override handlers

class MyFormMediator(GuiFrame):
    def __init__(self, parent):
        GuiFrame.__init__(self, parent)
        self.app = None
        self.observers = multicast()
        
    def Boot(self):
        self._InitHyperlinks()

    def _InitHyperlinks(self):
        def seturl(obj):
            obj.SetURL(self.app.url_server + obj.GetLabel())
            obj.SetToolTip(wx.ToolTip(obj.GetLabel()))
        seturl(self.m_hyperlink1)
        seturl(self.m_hyperlink2)
        seturl(self.m_hyperlink3)

    # Util

    def _FindClientData(self, control, clientData):
        """ Listboxes etc. don't support finding via clientData so I wrote this. """
        for i in range(0, self.m_listBox1.GetCount()):
            if self.m_listBox1.GetClientData(i) == clientData:
                return i
        return wx.NOT_FOUND

    def _RepairSelection(self, index):
        if self.m_listBox1.IsEmpty():
            return
        index = max(0, index-1)
        self.m_listBox1.SetSelection(index)
        
    # Gui Generated Events, override the handler here
    
    def OnFileNew(self, event):
        self.observers.CMD_FILE_NEW()

    def OnAddThing(self, event):
        info = str(random.randint(0,99999)) + " " + self.inputFieldTxt.GetValue()
        self.observers.CMD_ADD_THING(info)

    def OnAddInfoToThing(self, event):
        if self.m_listBox1.IsEmpty():
            return
        index = self.m_listBox1.GetSelection()
        if index == wx.NOT_FOUND:
            return
        thing = self.m_listBox1.GetClientData(index) # see ItemContainer methods http://www.wxpython.org/docs/api/wx.ItemContainer-class.html
        self.observers.CMD_ADD_INFO_TO_THING(thing, "Z")

    def OnDeleteThing(self, event):
        if self.m_listBox1.IsEmpty():
            return
        index = self.m_listBox1.GetSelection()
        thing = self.m_listBox1.GetClientData(index) # see ItemContainer methods http://www.wxpython.org/docs/api/wx.ItemContainer-class.html
        self.observers.CMD_DELETE_THING(thing)

    def onDumpModel(self, event):
        #self.m_textCtrlDump.Clear()
        self.m_textCtrlDump.AppendText(str(self.app.model) + "\n")
        
    # Non Gui Incoming Events
    
    def MODEL_CLEARED(self):
        self.m_listBox1.Clear()
        
    def MODEL_CHANGED(self, things):
        self.m_listBox1.Clear()
        for thing in things:
            self.m_listBox1.Append(str(thing), thing)

    def MODEL_THING_ADDED(self, thing, modelsize):
        self.m_listBox1.Append(str(thing), thing)

    def MODEL_THING_UPDATE(self, thing):
        index = self._FindClientData(self.m_listBox1, thing)
        if index != wx.NOT_FOUND:
            self.m_listBox1.SetString(index, str(thing))  # Maybe .Set() does both at the same time?
            self.m_listBox1.SetClientData(index, thing)

    def MODEL_THING_DELETED(self, thing):
        index = self._FindClientData(self.m_listBox1, thing)
        if index != wx.NOT_FOUND:
            self.m_listBox1.Delete(index)
            self._RepairSelection(index)        

class MyWxApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        frame = MyFormMediator(parent=None)
        frame.Show()
        self.myframe = frame
        return True

#
# Central App
#

class Controller():
    def __init__(self, model):
        self.app = None
        self.model = model

    # Events from Gui
    
    def CMD_FILE_NEW(self):
        self.model.Clear()

    def CMD_ADD_THING(self, info):
        thing = self.model.AddThing(info)

    def CMD_ADD_INFO_TO_THING(self, thing, moreinfo):
        #thing.AddInfo(moreinfo)
        self.model.AddInfoToThing(thing, moreinfo)

    def CMD_DELETE_THING(self, thing):
        self.model.DeleteThing(thing)
        
    # Other events
    
    def MODEL_THING_ADDED(self, thing, modelsize):
        print "App observer got notified, added value %(thing)s - modelsize now %(modelsize)4d" % vars()
        
class App(object):
    def __init__(self, model, server, gui):
        self.model = model
        self.server = server
        self.gui = gui
        self.controller = Controller(model)
        model.app = self.controller.app = gui.app = server.app = self

        # Inject multicast dependencies / observers
        gui.observers.addObserver(self.controller)
        model.observers.addObserver(gui)
        model.observers.addObserver(self.controller) # diagnostic, optional
        
        # Inject normal dependencies
        self.server.model = model
        
    def Boot(self):
        self.gui.Boot()
        self.model.Boot()
        self.model.AddThing("initial thing")
        self.server.StartServer()

    # Some methods the app has to define itself - rather than exposing
    # ring objects to one another for such trivial stuff

    @property
    def url_server(self):
        return self.server.url_server
        

if __name__ == '__main__':        

    if SIMPLE_MODEL:
        # Create Model - SIMPLE
        model = ModelProxySimple(Model())
    else:
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
