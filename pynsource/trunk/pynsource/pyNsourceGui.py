"""
PyNSource GUI
-------------

Andy Bulka
www.andypatterns.com

LICENSE: GPL 3

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import random
import wx
import wx.lib.ogl as ogl
from wx import Frame
import os, stat
from messages import *
from gui_umlshapes import *

APP_VERSION = 1.51
WINDOW_SIZE = (1024,768)
IMAGENODES = False
MULTI_TAB_GUI = True

# compensate for the fact that x, y for a ogl shape are the centre of the shape, not the top left
def setpos(shape, x, y):
    width, height = shape.GetBoundingBoxMax()
    shape.SetX( x + width/2 )
    shape.SetY( y + height/2 )
def getpos(shape):
    width, height = shape.GetBoundingBoxMax()
    x = shape.GetX()
    y = shape.GetY()
    return x - width/2, y - height/2

    
class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, frame, shapecanvas):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.frame = frame              # these are arbitrary initialisations
        self.shapecanvas = shapecanvas  # these are arbitrary initialisations

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        x, y = getpos(shape)
        width, height = shape.GetBoundingBoxMax()
        self.frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)" % (x, y, width, height))

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        self._SelectNodeNow(x, y, keys, attachment)

    def _SelectNodeNow(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()

        canvas.DeselectAllShapes()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        shape.Select(True, dc)  # could pass None as dc if you don't want to trigger the OnDrawControlPoints(dc) handler immediately - e.g. if you want to do a complete redraw of everything later anyway
        #canvas.Refresh(False)   # t/f or don't use - doesn't seem to make a difference
        
        self.UpdateStatusBar(shape)

    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        oldpos = getpos(shape)
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment) # super
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        newpos = getpos(shape)
        try:
            print shape.node.id, "moved from", oldpos, "to", newpos
            # Adjust the GraphNode to match the shape x,y
            shape.node.left, shape.node.top = newpos
        except:
            print "no node model attached to this shape!"
            
        self.UpdateStatusBar(shape)

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        shape = self.GetShape()

        # super        
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        
        width, height = shape.GetBoundingBoxMin()
        print shape.node, "resized to", width, height
        #print shape.node.id, shape.node.left, shape.node.top, "resized to", width, height
        # Adjust the GraphNode to match the shape x,y
        shape.node.width, shape.node.height = width, height
        shape.node.left, shape.node.top = getpos(shape)
        
        self.UpdateStatusBar(self.GetShape())

        #wx.SafeYield()
        #time.sleep(0.2)
        
        shape.GetCanvas().stage2()
        

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(shape)
        if "wxMac" in wx.PlatformInfo:
            shape.GetCanvas().Refresh(False) 

    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId()) 
        text = item.GetText() 
        if text == "Delete Node\tDel":
            self.RightClickDeleteNode()
        
    def OnRightClick(self, x, y, keys, attachment):
        self._SelectNodeNow(x, y, keys, attachment)

        #self.log.WriteText("%s\n" % self.GetShape())
        self.popupmenu = wx.Menu()     # Creating a menu
        item = self.popupmenu.Append(2011, "Delete Node\tDel")
        self.frame.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item) # Not sure why but passing item is needed.  Not to find the menu item later, but to avoid crashes?  try two right click deletes followed by main menu edit/delete.  Official Bind 3rd parameter DOCO:  menu source - Sometimes the event originates from a different window than self, but you still want to catch it in self. (For example, a button event delivered to a frame.) By passing the source of the event, the event handling system is able to differentiate between the same event type from different controls.
        item = self.popupmenu.Append(2012, "Cancel")
        self.frame.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.frame.PopupMenu(self.popupmenu, wx.Point(x,y))

    def RightClickDeleteNode(self):
        self.GetShape().GetCanvas().CmdZapShape(self.GetShape())



import sys, glob
from gen_java import PySourceAsJava
from umlworkspace import UmlWorkspace
from layout_basic import LayoutBasic

from layout_spring import GraphLayoutSpring
from overlap_removal import OverlapRemoval
#from blackboard import LayoutBlackboard
from coordinate_mapper import CoordinateMapper

class UmlShapeCanvas(ogl.ShapeCanvas):
    scrollStepX = 10
    scrollStepY = 10
    classnametoshape = {}

    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        maxWidth  = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE") #wxWHITE)

        self.SetDiagram(ogl.Diagram())
        self.GetDiagram().SetCanvas(self)
        self.save_gdi = []
        wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)

        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.working = False

        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

        self.umlworkspace = UmlWorkspace()
        #self.layout = LayoutBasic()
        #self.layout = LayoutBasic(leftmargin=0, topmargin=0, verticalwhitespace=0, horizontalwhitespace=0, maxclassesperline=5)
        self.layout = LayoutBasic(leftmargin=5, topmargin=5, verticalwhitespace=50, horizontalwhitespace=50, maxclassesperline=7)

        self.coordmapper = CoordinateMapper(self.umlworkspace.graph, self.GetSize())
        self.layouter = GraphLayoutSpring(self.umlworkspace.graph, gui=self)
        self.overlap_remover = OverlapRemoval(self.umlworkspace.graph, margin=50, gui=self)
    
    def AllToLayoutCoords(self):
        self.coordmapper.AllToLayoutCoords()

    def AllToWorldCoords(self):
        self.coordmapper.AllToWorldCoords()

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html

        if self.working:
            event.Skip()
            return
        self.working = True


        if keycode == wx.WXK_DOWN:
            optimise = not event.ShiftDown()
            self.ReLayout(keep_current_positions=True, gui=self, optimise=optimise)

        elif keycode == wx.WXK_UP:
            optimise = not event.ShiftDown()
            self.ReLayout(keep_current_positions=False, gui=self, optimise=optimise)
            
        elif keycode == wx.WXK_RIGHT:
            if self.coordmapper.scale > 0.8:
                self.ChangeScale(-0.2, remap_world_to_layout=event.ShiftDown(), removeoverlaps=not event.ControlDown())
                print "expansion ", self.coordmapper.scale
            else:
                print "Max expansion prevented.", self.coordmapper.scale
            
        elif keycode == wx.WXK_LEFT:
            if self.coordmapper.scale < 3:
                self.ChangeScale(0.2, remap_world_to_layout=event.ShiftDown(), removeoverlaps=not event.ControlDown())
                print "contraction ", self.coordmapper.scale
            else:
                print "Min expansion thwarted.", self.coordmapper.scale

        elif keycode == wx.WXK_INSERT:
            self.CmdInsertNewNode()
        elif keycode == wx.WXK_DELETE:
            print "DELETE"
            selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
            if selected:
                shape = selected[0]
                self.CmdZapShape(shape)
        self.working = False
        event.Skip()
                
    def CmdInsertNewNode(self):
        id = 'D' + str(random.randint(1,99))
        dialog = wx.TextEntryDialog ( None, 'Enter an id string:', 'Create a new node', id )
        if dialog.ShowModal() == wx.ID_OK:
            id = dialog.GetValue()
            node = self.umlworkspace.AddNode(id)
            self.createNodeShape(node)
            node.shape.Show(True)
            self.stateofthenation()
        dialog.Destroy()

    def CmdZapShape(self, shape):
        
        # Model/Uml related....
        self.umlworkspace.DeleteShape(shape)

        # View
        self.DeselectAllShapes()
        for line in shape.GetLines()[:]:
            line.Delete()
        shape.Delete()

    def Clear(self):
        self.GetDiagram().DeleteAllShapes()

        dc = wx.ClientDC(self)
        self.GetDiagram().Clear(dc)   # only ends up calling dc.Clear() - I wonder if this clears the screen?

        self.save_gdi = []
        
        self.umlworkspace.Clear()

    def ConvertParseModelToUmlModel(self, p):
        
        def BuildEdgeModel(association_tuples, edge_label):
            for fromClassname, toClassname in association_tuples:
                from_node = self.umlworkspace.AddUmlNode(fromClassname)
                to_node = self.umlworkspace.AddUmlNode(toClassname)
                edge = self.umlworkspace.graph.AddEdge(from_node, to_node)
                edge['uml_edge_type'] = edge_label
            
        for classname, classentry in p.classlist.items():
            #print 'CLASS', classname, classentry

            # These are a list of (attr, otherclass) however they imply that THIS class
            # owns all those other classes.
            
            for attr, otherclass in classentry.classdependencytuples:
                self.umlworkspace.associations_composition.append((otherclass, classname))  # reverse direction so round black arrows look ok

            # Generalisations
            if classentry.classesinheritsfrom:
                for parentclass in classentry.classesinheritsfrom:

                    if parentclass.find('.') <> -1:         # fix names like "unittest.TestCase" into "unittest"
                        parentclass = parentclass.split('.')[0] # take the lhs

                    self.umlworkspace.associations_generalisation.append((classname, parentclass))

            classAttrs = [ attrobj.attrname for attrobj in classentry.attrs ]
            classMeths = classentry.defs
            node = self.umlworkspace.AddUmlNode(classname, classAttrs, classMeths)

        BuildEdgeModel(self.umlworkspace.associations_generalisation, 'generalisation')
        BuildEdgeModel(self.umlworkspace.associations_composition, 'composition')
  
    def Go(self, files=None, path=None):

        # these are tuples between class names.
        self.umlworkspace.ClearAssociations()

        if files:
            for f in files:
                p = PySourceAsJava()
                p.optionModuleAsClass = 0
                p.verbose = 0
                p.Parse(f)
                self.ConvertParseModelToUmlModel(p)

        self.stage1()

        # Layout
        self.LayoutAndPositionShapes()
              
    def CreateUmlShape(self, node):

        def newRegion(font, name, textLst, maxWidth, totHeight = 10):
            # Taken from Boa, but put into the canvas class instead of the scrolled window class.
            region = ogl.ShapeRegion()
            dc = wx.ClientDC(self)  # self is the canvas
            dc.SetFont(font)
    
            for text in textLst:
                w, h = dc.GetTextExtent(text)
                if w > maxWidth: maxWidth = w
                totHeight = totHeight + h + 0 # interline padding
    
            region.SetFont(font)
            region.SetText('\n'.join(textLst))
            #region._text = string.join(textLst, '\n')
            region.SetName(name)
    
            return region, maxWidth, totHeight

        if len(node.attrs) == 0 and len(node.meths) == 0:
            rRectBrush = wx.Brush("MEDIUM TURQUOISE", wx.SOLID)
            dsBrush = wx.Brush("WHEAT", wx.SOLID)
            shape = self.DecorateShape(DividedShapeSmall(100, 30, self), 50, 145, wx.BLACK_PEN, dsBrush, '')
            shape.BuildRegions(canvas=self)  # build the one region
            shape.SetCentreResize(0)  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).
            shape.region1.SetText(node.classname)
            shape.ReformatRegions()
        else:
            if not IMAGENODES:
                shape = DividedShape(width=100, height=150, canvas=self)
            else:
                #print os.path.dirname( os.path.abspath( __file__ ) )
                #print os.path.relpath( __file__ )
                F = 'Research\\wx doco\\Images\\SPLASHSCREEN.BMP'
                # wx.ImageFromBitmap(bitmap) and wx.BitmapFromImage(image)
                shape = ogl.BitmapShape()
                img = wx.Image(F, wx.BITMAP_TYPE_ANY)
                bmp = wx.BitmapFromImage(img)
                shape.SetBitmap(bmp)
    
            pos = (50,50)
            maxWidth = 10 #padding
            #if not self.showAttributes: classAttrs = [' ']
            #if not self.showMethods: classMeths = [' ']
    
            regionName, maxWidth, nameHeight = newRegion(self.font1, 'class_name', [node.classname], maxWidth)
            regionAttribs, maxWidth, attribsHeight = newRegion(self.font2, 'attributes', node.attrs, maxWidth)
            regionMeths, maxWidth, methsHeight = newRegion(self.font2, 'methods', node.meths, maxWidth)
    
            totHeight = nameHeight + attribsHeight + methsHeight
    
            regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
            regionAttribs.SetProportions(0.0, 1.0*(attribsHeight/float(totHeight)))
            regionMeths.SetProportions(0.0, 1.0*(methsHeight/float(totHeight)))
    
            regionName.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ)
            shape.region1 = regionName  # Andy added, for later external reference to classname from just having the shap instance.
    
            shape.AddRegion(regionName)
            shape.AddRegion(regionAttribs)
            shape.AddRegion(regionMeths)
    
            shape.SetSize(maxWidth + 10, totHeight + 10)
    
            if not IMAGENODES:
                shape.SetRegionSizes()
    
            dsBrush = wx.Brush("WHEAT", wx.SOLID)
            self.DecorateShape(shape, pos[0], pos[1], wx.BLACK_PEN, dsBrush, '')
            
            if not IMAGENODES:
                shape.FlushText()

        # New
        node.top, node.left = getpos(shape)
        node.width, node.height = shape.GetBoundingBoxMax()
        node.shape = shape
        shape.node = node
        return shape

    def CreateUmlEdge(self, edge):
        fromShape = edge['source'].shape
        toShape = edge['target'].shape
        
        edge_label = edge.get('uml_edge_type', '')
        if edge_label == 'generalisation':
            arrowtype = ogl.ARROW_ARROW
        elif edge_label == 'composition':
            arrowtype = ogl.ARROW_FILLED_CIRCLE
        else:
            arrowtype = None

        line = ogl.LineShape()
        line.SetCanvas(self)
        line.SetPen(wx.BLACK_PEN)
        line.SetBrush(wx.BLACK_BRUSH)
        if arrowtype:
            line.AddArrow(arrowtype)
        line.MakeLineControlPoints(2)

        fromShape.AddLine(line, toShape)
        self.GetDiagram().AddShape(line)
        line.Show(True)

    def OnWheelZoom(self, event):
        if self.working: return
        self.working = True

        if event.GetWheelRotation() < 0:
            self.stage2()
            print self.overlap_remover.GetStats()
        else:
            self.stateofthenation()

        self.working = False
        
    def ChangeScale(self, delta, remap_world_to_layout=False, removeoverlaps=True):
        if remap_world_to_layout:
            self.AllToLayoutCoords()    # Experimental - only needed when you've done world coord changes 
        self.coordmapper.Recalibrate(scale=self.coordmapper.scale+delta)
        self.AllToWorldCoords()
        numoverlaps = self.overlap_remover.CountOverlaps()
        if removeoverlaps:
            self.stage2(force_stateofthenation=True, watch_removals=False) # does overlap removal and stateofthenation
        else:
            self.stateofthenation()
        
    def stage1(self, translatecoords=True):         # FROM SPRING LAYOUT
        #if translatecoords:
        #    self.AllToWorldCoords()

        for node in self.umlworkspace.graph.nodes:
            shape = self.CreateUmlShape(node)
            print 'created shape for node', node.id
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            
        for edge in self.umlworkspace.graph.edges:
            self.CreateUmlEdge(edge)

        #self.Redraw222()

    def stage2(self, force_stateofthenation=False, watch_removals=True):
        ANIMATION = False
        
        #if ANIMATION:
        #    self.graph.SaveOldPositionsForAnimationPurposes()
        #    watch_removals = False  # added this when I turned animation on.
        
        self.overlap_remover.RemoveOverlaps(watch_removals=watch_removals)
        if self.overlap_remover.GetStats()['total_overlaps_found'] > 0 or force_stateofthenation:
            self.stateofthenation(animate=ANIMATION)

    def stateofthenation(self, animate=False):
        for node in self.umlworkspace.graph.nodes:
            self.AdjustShapePosition(node)
        self.Redraw222()
        wx.SafeYield()

    def stateofthespring(self):
        self.coordmapper.Recalibrate()
        self.AllToWorldCoords()
        self.stateofthenation() # DON'T do overlap removal or it will get mad!
                
    def RedrawEverything(self):
        diagram = self.GetDiagram()
        canvas = self
        assert self == canvas == diagram.GetCanvas()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.umlboxshapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
            if not IMAGENODES:
                shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)

        # Hack To Force The Scrollbar To Show Up
        # Set the window size to something different
        # Return the size to what it was
        oldSize = self.frame.GetSize()
        self.frame.SetSize((oldSize[0]+1,oldSize[1]+1))
        self.frame.SetSize(oldSize)

    def ReLayout(self, keep_current_positions=False, gui=None, optimise=True):
        self.AllToLayoutCoords()
        self.layouter.layout(keep_current_positions, optimise=optimise)
        self.AllToWorldCoords()
        self.stage2() # does overlap removal and stateofthenation
    
    def LayoutAndPositionShapes(self):
        self.ReLayout()
        return
    
        positions, shapeslist, newdiagramsize = self.layout.Layout(self.umlworkspace, self.umlboxshapes)
        print "Layout positions", positions
        
        self.setSize(newdiagramsize)

        dc = wx.ClientDC(self)
        self.PrepareDC(dc)

        # Now move the shapes into place.
        for (pos, classShape) in zip(positions, shapeslist):
            #print pos, classShape.region1.GetText()
            x, y = pos

            # compensate for the fact that x, y for a ogl shape are the centre of the shape, not the top left
            width, height = classShape.GetBoundingBoxMax()
            x += width/2
            y += height/2

            classShape.Move(dc, x, y, False)

        #self.umlworkspace.Dump()
        
        
    def setSize(self, size):
        size = wx.Size(size[0], size[1])
        
        nvsx, nvsy = size.x / self.scrollStepX, size.y / self.scrollStepY
        self.Scroll(0, 0)
        self.SetScrollbars(self.scrollStepX, self.scrollStepY, nvsx, nvsy)
        canvas = self
        canvas.SetSize(canvas.GetVirtualSize())

    def DecorateShape(self, shape, x, y, pen, brush, text):
        # Composites have to be moved for all children to get in place
        if isinstance(shape, ogl.CompositeShape):
            dc = wx.ClientDC(self)
            self.PrepareDC(dc)
            shape.Move(dc, x, y)
        else:
            shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:    shape.SetPen(pen)
        if brush:  shape.SetBrush(brush)
        if text:
            for line in text.split('\n'):
                shape.AddText(line)
        self.GetDiagram().AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self.log, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        return shape
    
    def createNodeShape(self, node):     # FROM SPRING LAYOUT
        shape = ogl.RectangleShape( node.width, node.height )
        shape.AddText(node.id)
        setpos(shape, node.left, node.top)
        #shape.SetDraggable(True, True)
        self.AddShape( shape )
        node.shape = shape
        shape.node = node
        
        # wire in the event handler for the new shape
        evthandler = MyEvtHandler(None, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

    def AdjustShapePosition(self, node, point=None):   # FROM SPRING LAYOUT
        assert node.shape
        
        if point:
            x, y = point
        else:
            x, y = node.left, node.top
            
        # Don't need to use node.shape.Move(dc, x, y, False)
        setpos(node.shape, x, y)

        # But you DO need to use a dc to adjust the links
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        node.shape.MoveLinks(dc)
        
    def Redraw222(self, clear=True):        # FROM SPRING LAYOUT
        diagram = self.GetDiagram()
        canvas = self
        assert canvas == diagram.GetCanvas()
    
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        
        #for node in self.graph.nodes:    # TODO am still moving nodes in the pynsourcegui version?
        #    shape = node.shape
        #    shape.Move(dc, shape.GetX(), shape.GetY())
        
        if clear:
            diagram.Clear(dc)
        diagram.Redraw(dc)
        
    def get_umlboxshapes(self):
        return [s for s in self.GetDiagram().GetShapeList() if isinstance(s, DividedShape)]

    umlboxshapes = property(get_umlboxshapes)
    
    def OnDestroy(self, evt):
        for shape in self.GetDiagram().GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)

    def OnLeftClick(self, x, y, keys):  # Override of ShapeCanvas method
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        self.DeselectAllShapes()

    def DeselectAllShapes(self):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if selected:
            assert len(selected) == 1
            s = selected[0]
            canvas = s.GetCanvas()
            
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            s.Select(False, dc)
            canvas.Refresh(False)   # Need this or else Control points ('handles') leave blank holes
       

class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)
    write = WriteText

from gui_imageviewer import ImageViewer

USE_SIZER = False

class MainApp(wx.App):
    def OnInit(self):
        self.log = Log()
        wx.InitAllImageHandlers()
        self.andyapptitle = 'PyNsource GUI - Python Code into UML'

        self.frame = Frame(None, -1, self.andyapptitle, pos=(50,50), size=(0,0),
                        style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.DEFAULT_FRAME_STYLE)
        self.frame.CreateStatusBar()
        self.InitMenus()

        if MULTI_TAB_GUI:
            self.notebook = wx.Notebook(self.frame, -1)
         
            if USE_SIZER:
                # create the chain of real objects
                panel = wx.Panel(self.notebook, -1)
                self.umlwin = UmlShapeCanvas(panel, Log(), self.frame)
                # add children to sizers and set the sizer to the parent
                sizer = wx.BoxSizer( wx.VERTICAL )
                sizer.Add(self.umlwin, 1, wx.GROW)
                panel.SetSizer(sizer)
            else:
                self.umlwin = UmlShapeCanvas(self.notebook, Log(), self.frame)

            self.yuml = ImageViewer(self.notebook) # wx.Panel(self.notebook, -1)
            
            self.asciiart = wx.Panel(self.notebook, -1)
    
            if USE_SIZER:
                self.notebook.AddPage(panel, "UML")
            else:
                self.notebook.AddPage(self.umlwin, "UML")
            self.notebook.AddPage(self.yuml, "yUml")
            self.notebook.AddPage(self.asciiart, "Ascii Art")
    
            self.multiText = wx.TextCtrl(self.asciiart, -1,
            "Use the file menu to import python source code "
            "and generate UML ascii art here.\n\n"
            "Optionally join up your asci art UML using a tool like "
            "e.g Java Ascii Versatile Editor http://www.jave.de/\n\n"
            "Idea: Paste your UML Ascii art into your source code as comments!\n\n",
            style=wx.TE_MULTILINE)
            bsizer = wx.BoxSizer()
            bsizer.Add(self.multiText, 1, wx.EXPAND)
            self.asciiart.SetSizerAndFit(bsizer)
            self.multiText.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False))
            
            self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabPageChanged)
            
        else:
            self.umlwin = UmlShapeCanvas(self.frame, Log(), self.frame)
            
        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.
        
        # Set the frame to a good size for showing stuff
        self.frame.SetSize(WINDOW_SIZE)
        self.umlwin.SetFocus()
        self.SetTopWindow(self.frame)

        self.frame.Show(True)
        wx.EVT_CLOSE(self.frame, self.OnCloseFrame)
        
        self.popupmenu = None
        self.umlwin.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonMenu)
        self.Bind(wx.EVT_SIZE, self.OnResizeFrame)

        # Debug bootstrap  --------------------------------------
        #self.frame.SetSize((1024,768))
        #self.umlwin.Go(files=[os.path.abspath( __file__ )])
        self.umlwin.Go(files=[os.path.abspath( "../Research/state chart editor/Editor.py" )])
        self.umlwin.RedrawEverything()

        self.umlwin.umlworkspace.BuildGraphFromUmlWorkspace()

        # END Debug bootstrap --------------------------------------
        return True

    def OnResizeFrame (self, event):   # ANDY  interesting - GetVirtualSize grows when resize frame
        self.umlwin.coordmapper.Recalibrate(self.frame.GetClientSize()) # may need to call self.CalcVirtSize() if scrolled window
        #self.coordmapper.Recalibrate(self.frame.CalcVirtSize())

    def OnRightButtonMenu(self, event):   # Menu
        x, y = event.GetPosition()
        
        if self.popupmenu:
            self.popupmenu.Destroy()    # wx.Menu objects need to be explicitly destroyed (e.g. menu.Destroy()) in this situation. Otherwise, they will rack up the USER Objects count on Windows; eventually crashing a program when USER Objects is maxed out. -- U. Artie Eoff  http://wiki.wxpython.org/index.cgi/PopupMenuOnRightClick
        self.popupmenu = wx.Menu()     # Create a menu
        
        item = self.popupmenu.Append(wx.NewId(), "Load Graph from text...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoadGraphFromText, item)
        
        item = self.popupmenu.Append(wx.NewId(), "Dump Graph to console")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraphToConsole, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.NewId(), "BuildGraphFromUmlWorkspace")
        self.frame.Bind(wx.EVT_MENU, self.OnBuildGraphFromUmlWorkspace, item)

        self.frame.PopupMenu(self.popupmenu, wx.Point(x,y))
        
    def OnBuildGraphFromUmlWorkspace(self, event):
        #self.MessageBox("OnBuildGraphFromUmlWorkspace")
        self.umlwin.umlworkspace.BuildGraphFromUmlWorkspace()

    def OnSaveGraphToConsole(self, event):
        print self.umlwin.umlworkspace.graph.GraphToString()

    def OnSaveGraph(self, event):
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.txt", style=wx.FD_SAVE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            
            fp = open(filename, "w")
            fp.write(self.umlwin.umlworkspace.graph.GraphToString())
            fp.close()
        dlg.Destroy()
        
    def OnLoadGraphFromText(self, event):
        eg = "{'type':'node', 'id':'A', 'x':142, 'y':129, 'width':250, 'height':250}"
        dialog = wx.TextEntryDialog ( None, 'Enter an node/edge persistence strings:', 'Create a new node', eg,  style=wx.OK|wx.CANCEL|wx.TE_MULTILINE )
        if dialog.ShowModal() == wx.ID_OK:
            txt = dialog.GetValue()
            self.LoadGraph(txt)
            
    def OnLoadGraph(self, event):
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.txt", style=wx.OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            fp = open(filename, "r")
            s = fp.read()
            fp.close()

            self.LoadGraph(s)
        dlg.Destroy()

    def LoadGraph(self, filedata=""):
        self.umlwin.Clear()
        
        self.umlwin.umlworkspace.graph.LoadGraphFromStrings(filedata)
                
        # build view from model
        self.umlwin.stage1(translatecoords=False)
        
        # refresh view
        self.umlwin.GetDiagram().ShowAll(1) # need this, yes
        self.umlwin.stateofthenation()
        
    def OnTabPageChanged(self, event):
        if event.GetSelection() == 0:  # ogl
            pass
        elif event.GetSelection() == 1:  # yuml
            #self.yuml.ViewImage(thefile='../outyuml.png')
            pass
        elif event.GetSelection() == 2:  # ascii art
            pass
        
        event.Skip()
         
    def InitMenus(self):
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        menu2 = wx.Menu()
        menu3 = wx.Menu()
        menu4 = wx.Menu()

        self.next_menu_id = 200
        def Add(menu, s1, s2, func):
            menu.Append(self.next_menu_id, s1, s2)
            wx.EVT_MENU(self, self.next_menu_id, func)
            self.next_menu_id +=1

        Add(menu1, "File &Import...\tCtrl-I", "Import Python Source Files", self.FileImport)
        Add(menu1, "File &Import yUml...\tCtrl-O", "Import Python Source Files", self.FileImport2)
        Add(menu1, "File &Import Ascii Art...\tCtrl-J", "Import Python Source Files", self.FileImport3)
        menu1.AppendSeparator()
        Add(menu1, "&Clear\tCtrl-N", "Clear Diagram", self.FileNew)
        menu1.AppendSeparator()
        Add(menu1, "File &Print / Preview...\tCtrl-P", "Print", self.FilePrint)
        menu1.AppendSeparator()
        Add(menu1, "E&xit\tAlt-X", "Exit demo", self.OnButton)
        
        Add(menu2, "&Delete Class\tDel", "Delete Node", self.OnDeleteNode)
        
        Add(menu3, "&Layout UML", "Layout UML", self.OnLayout)
        Add(menu3, "&Refresh", "Refresh", self.OnRefreshUmlWindow)
        
        Add(menu4, "&Help...", "Help", self.OnHelp)
        Add(menu4, "&Visit PyNSource Website...", "PyNSource Website", self.OnVisitWebsite)
        menu4.AppendSeparator()
        Add(menu4, "&Check for Updates...", "Check for Updates", self.OnCheckForUpdates)
        Add(menu4, "&About...", "About...", self.OnAbout)

        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Edit")
        menuBar.Append(menu3, "&Layout")
        menuBar.Append(menu4, "&Help")
        self.frame.SetMenuBar(menuBar)
        
    def FileImport(self, event):
        self.notebook.SetSelection(0)
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            self.umlwin.Go(files=filenames)
            self.umlwin.RedrawEverything()
            wx.EndBusyCursor()
            print 'Import - Done.'

    def FileImport2(self, event):
        from gen_yuml import PySourceAsYuml
        import urllib
        
        self.notebook.SetSelection(1)
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            
            files=filenames
            p = PySourceAsYuml()
            p.optionModuleAsClass = 0
            p.verbose = 0
            if files:
                for f in files:
                    p.Parse(f)
            p.CalcYumls()
            print p

            #yuml_txt = "[Customer]+1->*[Order],[Order]++1-items >*[LineItem],[Order]-0..1>[PaymentMethod]"
            yuml_txt = ','.join(str(p).split())
            baseUrl = 'http://yuml.me/diagram/dir:lr;scruffy/class/'
            url = baseUrl + urllib.quote(yuml_txt)
            self.yuml.ViewImage(url=url)

            wx.EndBusyCursor()
            print 'Import - Done.'

    def FileImport3(self, event):
        from gen_asciiart import PySourceAsText
        import urllib
        
        self.notebook.SetSelection(2)
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            
            files=filenames
            p = PySourceAsText()
            p.optionModuleAsClass = 0
            p.verbose = 0
            if files:
                for f in files:
                    p.Parse(f)
            print p

            self.multiText.SetValue(str(p))
            self.multiText.ShowPosition(0)

            wx.EndBusyCursor()
            print 'Import - Done.'

    def FileNew(self, event):
        self.umlwin.Clear()
        
    def FilePrint(self, event):

        from printframework import MyPrintout

        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_LETTER)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.canvas = self.umlwin.GetDiagram().GetCanvas()

        #self.log.WriteText("OnPrintPreview\n")
        printout = MyPrintout(self.canvas, self.log)
        printout2 = MyPrintout(self.canvas, self.log)
        self.preview = wx.PrintPreview(printout, printout2, self.printData)
        if not self.preview.Ok():
            self.log.WriteText("Houston, we have a problem...\n")
            return

        frame = wx.PreviewFrame(self.preview, self.frame, "This is a print preview")

        frame.Initialize()
        frame.SetPosition(self.frame.GetPosition())
        frame.SetSize(self.frame.GetSize())
        frame.Show(True)

    def OnAbout(self, event):
        self.MessageBox(ABOUT_MSG.strip() %  APP_VERSION)

    def OnVisitWebsite(self, event):
        import webbrowser
        webbrowser.open(WEB_PYNSOURCE_HOME_URL)

    def OnCheckForUpdates(self, event):
        import urllib2
        s = urllib2.urlopen(WEB_VERSION_CHECK_URL).read()
        s = s.replace("\r", "")
        info = eval(s)
        ver = info["latest_version"]
        
        if ver > APP_VERSION:
            msg = WEB_UPDATE_MSG % (ver, info["latest_announcement"].strip())
            retCode = wx.MessageBox(msg.strip(), "Update Check", wx.YES_NO | wx.ICON_QUESTION)  # MessageBox simpler than MessageDialog
            if (retCode == wx.YES):
                import webbrowser
                webbrowser.open(info["download_url"])
        else:
            self.MessageBox("You already have the latest version:  %s" % APP_VERSION)
    
    def OnHelp(self, event):
        self.MessageBox(HELP_MSG.strip())

    def OnDeleteNode(self, event):
        for shape in self.umlwin.GetDiagram().GetShapeList():
            if shape.Selected():
                self.umlwin.CmdZapShape(shape)

    def OnLayout(self, event):
        if self.umlwin.GetDiagram().GetCount() == 0:
            self.MessageBox("Nothing to layout.  Import a python source file first.")
            return
        
        self.umlwin.LayoutAndPositionShapes()
        self.umlwin.RedrawEverything()

    def OnRefreshUmlWindow(self, event):
        self.umlwin.RedrawEverything()

    def MessageBox(self, msg):
        dlg = wx.MessageDialog(self.frame, msg, 'Message', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnButton(self, evt):
        self.frame.Close(True)


    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.umlwin.ShutdownDemo()
        evt.Skip()

def main():
    application = MainApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()


