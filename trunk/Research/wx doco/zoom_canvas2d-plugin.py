"""
http://wxpython-users.1045709.n5.nabble.com/OGL-smart-shape-position-in-a-canvas-td2351397.html


Am 15.05.2007, 10:13 Uhr, schrieb Marco Meoni - Sbaush <[hidden email]>: 

> Infact i need a application that can zoom and use all the good 
> possibilities of Float Canvas but i need also 
> "lines-connecting-boxes", that i'm trying to implement in FloatCanvas. 

I have an ogl app which has zooming. I override GetDC and PrepareDC like   
this: 

     def GetDC(self): 
         dc = wx.ClientDC(self) 
         self.PrepareDC(dc) 
         return dc 

     def PrepareDC(self, dc): 
         ogl.ShapeCanvas.PrepareDC(self, dc) 
         dc.SetUserScale( self.zoom, self.zoom ) 


I did the project some months ago, so I am not sure about the caveats. I   
think you need to redraw the shapes + lines after you've set the zoom   
factor. 
With a bit of work ogl can do a lot of nice things. Reading the source in   
wx.lib helps tremendously when messing with ogl. 
In my project the shapes are not self-drawn, but wx.Panels (or other wx.   
objects). This allows me to reuse a lot of widgets. Maybe you want to look   
at a similar approach. If you have lots and lots of shapes you might want   
to optimize this approach a bit to save window resources. 
My wx.Panels hold a wx.PropertyGrid and I can attach lines to each   
property. You can achieve behaviour like this by hooking into the   
connection point stuff. There are probably many more possibilities to   
extend ogl. 
You are right though, the docs are not beautiful, the source code isn't   
too cleanly structured because of it's C++ ancestry and it's difficult to   
hook into several things. 
I never dealt with FloatCanvas, so it might be the better choice for you.   
I just wanted to say that ogl can do what you want although you might have   
to put a bit of effort into it. 

-Matthias
"""


import wx
import wx.lib.ogl as ogl

from Client.Sources.Net import Events
from GlitterSoul.External.louie import louie

from Plugins.Configuration import Config
from Plugins.mainGui import app

import math

#----------------------------------------------------------------------
class GraphWindow(ogl.ShapeCanvas):
    def __init__(self, frame):
        ogl.OGLInitialize()
        ogl.ShapeCanvas.__init__(self, frame)

        maxWidth  = 10000
        maxHeight = 10000
        self.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)

        self.nodeShapes = {}
        self.connShapes = [] #Connection line shapes
        self.linesFrom = {}
        self.linesTo = {}
        
        self.viewMode = 'static'

        self.SetBackgroundColour( wx.Color(*Config.backgroundColorStatic) )
        self.diagram = ogl.Diagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.SetSize((640, 480))
        
        self.zoom = 1
        self.mainFrame = mf = app.mainFrame

        self.menu = \
        mf.AddMenu( _('&Canvas'),   ( mf.MenuEntry( _('&Zoom +') + '\tCtrl++', _('Zooms in'), self.OnZoomPlus, 'Art/viewmag.png' ),
                                      mf.MenuEntry( _('&Zoom -') + '\tCtrl+-', _('Zooms out'), self.OnZoomMinus, 'Art/viewmag.png' ),
                                      mf.MenuEntry( _('Zoom &100%') + '\tCtrl+*', _('Reset zoom to 100%'), self.OnZoomReset, 'Art/viewmag.png' ),
                                     )
                   )        

        sb = mf.statusBar
        self.zoomStatusBarWidget = wx.StaticText(sb, -1, '100%' )
        noItems = sb.GetFieldsCount()
        sb.SetFieldsCount( noItems + 1  )
        sb.AddWidget( self.zoomStatusBarWidget, pos = noItems )
        newWidths = sb.GetStatusWidths()[0:-1] + [60]
        sb.SetStatusWidths( newWidths )

        self.SetDropTarget( CanvasDropTarget(self) )
        
        louie.connect( self.OnNewNode, Events.instantiateClassFinished )
        louie.connect( self.OnDeleteNode, Events.deleteNodeFinished )
        louie.connect( self.OnChangePresenterInfo, Events.changePresenterInfoFinished )
        louie.connect( self.OnChangePresenterClassInfo, Events.setPresenterClassInfoFinished )
        louie.connect( self.OnNewConnection, Events.createConnectionFinished )
        louie.connect( self.OnDeleteConnection, Events.deleteConnectionFinished )
        louie.connect( self.OnSetViewMode, Events.setViewMode )
        louie.connect( self.OnChangePropertyValue, Events.changePropertyValue )
        louie.connect( self.OnDisconnected, Events.disconnected )
        louie.connect( self.OnClearCanvas, Events.resetServerWorkspaceFinished )
        
        #self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        
    def OnDisconnected(self):
        #self.Clear()
        pass
        
    def OnClearCanvas(self, result):
        self.Clear()
        
    def OnChangePresenterInfo(self, objAndInfo, refresh = True):
        obj, info = objAndInfo
        id = obj.id
        shape = self.nodeShapes[id]

        pinfo = PresenterInfo.fromDict( info )
        
        if shape.info.presenterClass != pinfo.presenterClass:
            newNode = self.AddNode(obj, info)

            oldLinesFrom, oldLinesTo = self.getAllLinesOfNode( id )                
            for name, line in oldLinesFrom.items():
                self.removeLineFromTo( id, name, line[0][0], line[0][1] )
                self.addLineFromTo( id, name, line[0][0], line[0][1], newNode, self.nodeShapes[line[0][0]] )
            for name, line in oldLinesTo.items():
                self.removeLineFromTo( line[0][0], line[0][1], id, name )
                self.addLineFromTo( line[0][0], line[0][1], id, name, self.nodeShapes[line[0][0]], newNode )

            #self.DeleteNode(id)
        else:
            shape.UpdateInfo(pinfo)
            
        if refresh: self.Refresh()        
        
    def OnChangePresenterClassInfo(self, classAndPresenterAndNodesWithInfo):
        klass, info, nodesWithInfo = classAndPresenterAndNodesWithInfo
        
        for node, info in nodesWithInfo:
            self.OnChangePresenterInfo( (node, info), False )
            
        self.Refresh()

    def AddNode(self, obj, info):
        presenterinfo = PresenterInfo.fromDict( info )
        pclass = presenterinfo.presenterClass
        
        if not pclass:
            pclass = 'EditorPresenter'
        
        presentermodule = __import__( 'Client.Sources.GUI.Presenters.%s' % pclass, globals(), locals(), [pclass] )
        presenter = getattr(presentermodule, pclass)
        if obj.id in self.nodeShapes:
            self.DeleteNode(obj.id, False)
        self.nodeShapes[obj.id] = newShape = presenter( self, obj, presenterinfo )
        newShape.SetViewMode(self.viewMode)

        #self.classToShapes.setDefault(obj.kclsid, []).append( newShape )
        
        return newShape
    
    def DeleteNode(self, id, deleteConnections = True):        
        if deleteConnections:
            oldLinesFrom, oldLinesTo = self.getAllLinesOfNode( id )                
            for name, line in oldLinesFrom.items():
                self.removeLineFromTo( id, name, line[0][0], line[0][1] )
            for name, line in oldLinesTo.items():
                self.removeLineFromTo( line[0][0], line[0][1], id, name )
    
        shape = self.nodeShapes[id]
        del self.nodeShapes[id]
        shape.Delete()
        #del self.classToShapes[id]
        
        
    def OnNewNode(self, objandpresenterinfo):
        obj, presenterinfo = objandpresenterinfo
        
        self.AddNode(obj, presenterinfo)
        
        self.Refresh()
        
    def addLineFromTo(self, id1, name1, id2, name2, presenter1, presenter2, kind = 'ref'):
        line = ConnectionShape( self, kind, presenter1, name1, presenter2, name2 )

        if id1 not in self.linesFrom:
            self.linesFrom[id1] = {}

        self.linesFrom[id1][name1] = ( (id2, name2), line )
    
        if id2 not in self.linesTo:
            self.linesTo[id2] = {}

        self.linesTo[id2][name2] = ( (id1, name1), line )

    def removeLineFromTo(self, id1, name1, id2, name2):
        lineShape = self.linesFrom[id1][name1][1]
        
        lineShape.Delete()  

        del self.linesFrom[id1][name1]
        
        if self.linesFrom[id1] == {}:
            del self.linesFrom[id1]

        del self.linesTo[id2][name2]
        
        if self.linesTo[id2] == {}:
            del self.linesTo[id2]
            
    def getAllLinesOfNode(self, id):
        #try:
        #    linesFrom = [ l for l in self.linesFrom[id].items() ]
        #except KeyError:
        #    linesFrom = []
        #
        #try:
        #    linesTo = [ l for l in self.linesTo[id].items() ]
        #except KeyError:
        #    linesTo = []

        #return linesFrom, linesTo
        
        return self.linesFrom.get(id, {}), self.linesTo.get(id, {})
        

    def OnNewConnection(self, obj1name1obj2name2):
        obj1, name1, obj2, name2 = obj1name1obj2name2
        
        presenter1 = self.nodeShapes[obj1.id]
        presenter2 = self.nodeShapes[obj2.id]
        
        self.addLineFromTo( obj1.id, name1, obj2.id, name2, presenter1, presenter2 )

        self.Refresh()

    def OnDeleteNode(self, id):
        self.DeleteNode(id)
        self.Refresh()

    def OnDeleteConnection(self, obj1name1obj2name2):
        obj1, name1, obj2, name2 = obj1name1obj2name2
        
        self.removeLineFromTo( obj1.id, name1, obj2.id, name2 )
                
        self.Refresh()
        
    def OnSetViewMode(self, mode):
        self.viewMode = mode
        if mode == 'static':
            self.SetBackgroundColour( wx.Color(*Config.backgroundColorStatic) )
        elif mode == 'dynamic':
            self.SetBackgroundColour( wx.Color(*Config.backgroundColorDynamic) )
        
        for id, shape in self.nodeShapes.items():
            shape.SetViewMode( mode )


        self.Refresh()
        
    def OnChangePropertyValue(self, id, name, value, kind = 'static'):
        if kind == 'dynamic':
            def x():
                for id, shape in self.nodeShapes.items():
                    shape.update()
                
            wx.CallAfter( x )
    
    def Redraw(self, dc = None):
        if dc is None:
            dc = self.GetDC()
            
        ogl.ShapeCanvas.Redraw(self, dc)
        
    def GetDC(self):
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        return dc
        
    def UpdateLines(self, shape, refresh = True):
        fromTo = self.getAllLinesOfNode( shape.node.id )
        lines = fromTo[0].values() + fromTo[1].values()
        
        allLinesFrom = [ line[1] for line in lines ]

        dc = self.GetDC()
        
        for l in allLinesFrom:
            l.OnMoveLink(dc)
            
        if refresh:
            self.Refresh()
    
    def UpdateAllLines(self, refresh = True):    
        for shape in self.nodeShapes.values():
            self.UpdateLines(shape, False)
        if refresh: self.Refresh()

    def Clear(self):
        for id in self.nodeShapes.keys():
            self.DeleteNode(id)

    def SetZoom(self, zoom):
        zoom = max( min(zoom, Config.maxZoom), Config.minZoom)
        self.zoom = zoom
        self.zoomStatusBarWidget.SetLabel( '%.1f%%' % (zoom * 100) )
        self.Redraw()
        self.UpdateAllLines(False)
        self.Refresh()
    
    def OnZoomPlus(self, evt):
        evt.Skip()
        self.SetZoom( self.zoom * Config.zoomStep )
        
    def OnZoomMinus(self, evt):
        evt.Skip()
        self.SetZoom( self.zoom * 1.0 / Config.zoomStep )
        
    def OnZoomReset(self, evt):
        evt.Skip()
        self.SetZoom( 1.0 )

    def PrepareDC(self, dc):
        ogl.ShapeCanvas.PrepareDC(self, dc)
        dc.SetUserScale( self.zoom, self.zoom )
        

class ConnectionShape(ogl.LineShape):
    def __init__(self, canvas, connectionType, upNodeShp, upProp, downNodeShp, downProp):
        ogl.LineShape.__init__(self)
                
        if Config.showConnectionLabels:
            dc = canvas.GetDC()
            
            lineLabels = { 'Start' : upProp, 'Middle' : '%s - %s' % (upProp, downProp), 'End' : downProp }
            
            for label, value in lineLabels.iteritems():
                rgnId = self.GetRegionId(label)
                self.FormatText(dc, value, rgnId)
                
            for rgn in self.GetRegions():
                if rgn.GetName() in lineLabels.keys():
                    rgn.SetSize(70,10)
                    rgn.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        
        self.upShape = upNodeShp
        self.upProp = upProp
        self.downShape = downNodeShp
        self.downProp = downProp
        
        self.canvas = canvas
        self.SetCanvas(canvas)
        
        colors = { 'ref'  : (wx.BLACK_PEN, wx.BLACK_BRUSH),
                   'copy' : (wx.GREEN_PEN, wx.GREEN_BRUSH),
                   'deep' : (wx.RED_PEN, wx.RED_BRUSH)
                 }
                   
        colors = colors[connectionType]
        
        self.SetPen( colors[0] )
        self.SetBrush( colors[1] )
        self.AddArrow(ogl.ARROW_ARROW)
        #self.MakeLineControlPoints(4)
        self.MakeLineControlPoints(2)
        #self.SetSpline(False)
        upNodeShp.AddLine(self, downNodeShp)
        canvas.diagram.AddShape(self)
        self.Show(True)
        self.SetAttachments(1, 3)
        self.SetDrawHandles(True)
        #self.SetDraggable(True)

    #This method just changes view.
    def changeView(self, select = True, refreshCanvas = True):
        if select:
            pen = wx.Pen(wx.RED, 1)
            brush = wx.RED_BRUSH
        else:
            pen = wx.Pen(wx.BLACK, 1)
            brush = wx.BLACK_BRUSH
        self.SetPen(pen)
        self.SetBrush(brush)

        if refreshCanvas:
            self.GetCanvas().Refresh()

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        canvas = self.canvas
        dc = canvas.GetDC()

        if self.Selected():
            self.Select(False, dc)
            canvas.Redraw(dc)
        else:
            redraw = False
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []

            for s in shapeList:
                if s.Selected():
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            self.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)

                canvas.Redraw(dc)
                
    def FindLineEndPoints(self):
        upPoints = self.upShape.GetConnectionPoints( self.upProp )
        downPoints = self.downShape.GetConnectionPoints( self.downProp )

        def sqDist(p1, p2):
            return math.sqrt( (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 )
        
        minDist = 999999
        closestPoints = None
        for pup in upPoints:
            for pdown in downPoints:
                dist = sqDist( pup, pdown )
                if dist < minDist:
                    minDist = dist
                    closestPoints = (pup, pdown)
                    
        #print upPoints, downPoints
        return closestPoints[0][0], closestPoints[0][1], closestPoints[1][0], closestPoints[1][1]
    
    def Delete(self):        
        self.upShape.RemoveLine( self )
        ogl.LineShape.Delete(self)
        
        
    def GetLabelPosition(self, position):
        """Get the reference point for a label.

        Region x and y are offsets from this.
        position is 0 (middle), 1 (start), 2 (end).
        """
        result = ogl.LineShape.GetLabelPosition(self, position)
        if position == 0:
            # Want to take the middle section for the label
            return result
        elif position == 1:
            return result[0] + 40, result[1]
        elif position == 2:
            return result[0] - 40, result[1]
        
    #def OnMoveLink(self, dc, moveControlPoints = True):
    #    getfrom = self.GetFrom()
    #    getto = self.GetTo()
    #    x, y = (getto.GetX() - getfrom.GetX(), getto.GetY() - getfrom.GetY())
    #
    #    if y >= -x and y >= x:
    #        self.SetAttachments(2, 4)
    #    elif y >= -x and y < x:
    #        self.SetAttachments(1, 3)
    #    elif y < -x and y >= x:
    #        self.SetAttachments(3, 1)
    #    else:
    #        self.SetAttachments(4, 2)
    #
    #    ogl.LineShape.OnMoveLink(self, dc, moveControlPoints)

        #fAtPtX, fAtPtY = self.GetFrom().GetAttachmentPosition(1)
        #tAtPtX, tAtPtY = self.GetTo().GetAttachmentPosition(3)
        #self.GetNextControlPoint(self.GetFrom()).x = fAtPtX + 20
        #self.GetNextControlPoint(self.GetFrom()).y = fAtPtY
        #self.GetNextControlPoint(self.GetTo()).x = tAtPtX - 30
        #self.GetNextControlPoint(self.GetTo()).y = tAtPtY        
        
        

class PresenterInfo(object):
    def __init__(self, presenterClass, pos, size, editors, inheritPresenter, inheritEditors):
        self.presenterClass = presenterClass
        self.pos = pos
        self.size = size
        self.editors = editors
        self.inheritPresenter = inheritPresenter
        self.inheritEditors = inheritEditors
    
    
    # the next 2 funcs are a bit ugly, but I don't want to write a twisted wrapper just for them :-)
    # update: now that we use pickle with twisted, this could go away, but i am too lazy right now to change it
    def getInfo(self):
        return vars(self)
    
    @classmethod
    def fromDict(cls, dict):
        presenterinfo = cls(**dict)
        presenterinfo.__dict__.update(dict)
        return presenterinfo


import cPickle as pickle

class DropData(wx.CustomDataObject):
    def __init__(self):
        wx.CustomDataObject.__init__(self, wx.CustomDataFormat("MyDropData"))
        self.setObject(None)

    def setObject(self, obj):
        self.SetData(pickle.dumps(obj))

    def getObject(self):
        return pickle.loads(self.GetData())
    
    
class CanvasDropTarget(wx.PyDropTarget):
    def __init__(self, canvas):
        wx.PyDropTarget.__init__(self)
        self.canvas = canvas
        self._makeObjects()

    def _makeObjects(self):
        self.data = DropData()
        self.fileObject = wx.FileDataObject()
        comp = wx.DataObjectComposite()
        comp.Add(self.data)
        comp.Add(self.fileObject)
        self.comp = comp
        self.SetDataObject(comp)


    def OnEnter(self, x, y, d):
        return d

    def OnLeave(self):
        pass

    def OnDrop(self, x, y):
        #print "got an drop event at", x, y
        return True
        
    def OnDragOver(self, x, y, d):
        # provide visual feedback by selecting the item the mouse is over
        pass

        # The value returned here tells the source what kind of visual
        # feedback to give.  For example, if wx.DragCopy is returned then
        # only the copy cursor will be shown, even if the source allows
        # moves.  You can use the passed in (x,y) to determine what kind
        # of feedback to give.  In this case we return the suggested value
        # which is based on whether the Ctrl key is pressed.
        return d

    # Called when OnDrop returns True.  We need to get the data and
    # do something with it.
    def OnData(self, x, y, d):
        if self.GetData():
            filenames = self.fileObject.GetFilenames()
            nodeid, nodeType = self.data.getObject()
            
            if nodeType == 'ClassNode':
                #x, y = self.canvas.CalcUnscrolledPosition(x, y)
                dc = self.canvas.GetDC()
                x, y = dc.DeviceToLogicalX(x), dc.DeviceToLogicalY(y)
                info = PresenterInfo( '', (x,y), (220, 200), {}, True, True )
                louie.send( Events.instantiateClass, classid = nodeid, presenterinfo = info.getInfo() )

            self._makeObjects()   # reset data objects..
    
        return d  # what is returned signals the source what to do
                  # with the original data (move, copy, etc.)  In this
                  # case we just return the suggested value given to us.



def GetInfo(me):
    me.uniqueName = 'Canvas'
    me.version = 1.0
    me.info = 'Helper plugin'

