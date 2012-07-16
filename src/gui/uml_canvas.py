import sys, glob
if ".." not in sys.path: sys.path.append("..")

import random

from generate_code.gen_java import PySourceAsJava
from umlworkspace import UmlWorkspace

from uml_shapes import *
from coord_utils import setpos, getpos

from layout.layout_basic import LayoutBasic

from layout.snapshots import GraphSnapshotMgr
from layout.layout_spring import GraphLayoutSpring
from layout.overlap_removal import OverlapRemoval
from layout.blackboard import LayoutBlackboard
from layout.coordinate_mapper import CoordinateMapper

import wx
import wx.lib.ogl as ogl

from uml_shape_handler import UmlShapeHandler

from architecture_support import *

class UmlCanvas(ogl.ShapeCanvas):
    scrollStepX = 10
    scrollStepY = 10
    classnametoshape = {}

    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        maxWidth  = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)

        self.observers = multicast()
        
        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE") #wxWHITE)

        self.SetDiagram(ogl.Diagram())
        self.GetDiagram().SetCanvas(self)
        self.save_gdi = []
        wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)

        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.EVT_CHAR, self.onKeyChar)
        self.working = False

        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

        self.umlworkspace = UmlWorkspace()
        #self.layout = LayoutBasic()
        #self.layout = LayoutBasic(leftmargin=0, topmargin=0, verticalwhitespace=0, horizontalwhitespace=0, maxclassesperline=5)
        self.layout = LayoutBasic(leftmargin=5, topmargin=5, verticalwhitespace=50, horizontalwhitespace=50, maxclassesperline=7)

        self.snapshot_mgr = GraphSnapshotMgr(graph=self.umlworkspace.graph, controller=self)
        self.coordmapper = CoordinateMapper(self.umlworkspace.graph, self.GetSize())
        self.layouter = GraphLayoutSpring(self.umlworkspace.graph, gui=self)
        self.overlap_remover = OverlapRemoval(self.umlworkspace.graph, margin=50, gui=self)
        self._kill_layout = False   # flag to communicate with layout engine.  aborting keypress in gui should set this to true

        @property
        def kill_layout(self):
          return self._kill_layout
        @kill_layout.setter
        def kill_layout(self, value):
          self._kill_layout = value
    
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


        #if keycode == wx.WXK_DOWN:
        #    optimise = not event.ShiftDown()
        #    self.ReLayout(keep_current_positions=True, gui=self, optimise=optimise)
        #
        #elif keycode == wx.WXK_UP:
        #    optimise = not event.ShiftDown()
        #    self.ReLayout(keep_current_positions=False, gui=self, optimise=optimise)
        
        if keycode == wx.WXK_ESCAPE:
            print "ESC key detected: Abort Layout"
            self.kill_layout = True
        
        if keycode == wx.WXK_RIGHT:
            self.cmdLayoutExpand(event)
            
        elif keycode == wx.WXK_LEFT:
            self.cmdLayoutContract(event)

        elif keycode == wx.WXK_INSERT:
            self.CmdInsertNewNode()
        elif keycode == wx.WXK_DELETE:
            print "DELETE"
            self.observers.CMD_NODE_DELETE_SELECTED()
            
        self.working = False
        event.Skip()

    def cmdLayoutExpand(self, event):
        if self.coordmapper.scale > 0.8:
            self.ChangeScale(-0.2, remap_world_to_layout=event.ShiftDown(), removeoverlaps=not event.ControlDown())
            #print "expansion ", self.coordmapper.scale
        else:
            print "Max expansion prevented.", self.coordmapper.scale

    def cmdLayoutContract(self, event):
        if self.coordmapper.scale < 3:
            self.ChangeScale(0.2, remap_world_to_layout=event.ShiftDown(), removeoverlaps=not event.ControlDown())
            #print "contraction ", self.coordmapper.scale
        else:
            print "Min expansion thwarted.", self.coordmapper.scale

    def onKeyChar(self, event):
        if event.GetKeyCode() >= 256:
            event.Skip()
            return
        if self.working:
            event.Skip()
            return
        self.working = True
        
        keycode = chr(event.GetKeyCode())

        if keycode == 'q':
            self.NewEdgeMarkFrom()

        elif keycode == 'w':
            self.NewEdgeMarkTo()
            
        elif keycode in ['1','2','3','4','5','6','7','8']:
            todisplay = ord(keycode) - ord('1')
            self.snapshot_mgr.Restore(todisplay)

        elif keycode in ['b', 'B']:
            self.CmdDeepLayout()
                
        elif keycode in ['l', 'L']:
            self.CmdLayout()
            
        elif keycode in ['d', 'D']:
            self.DumpStatus()
        
        self.working = False
        event.Skip()

    def DumpStatus(self):
        # Also called by Snapshot manager.
        # When create Snapshot manager we pass ourselves as a controller and DumpStatus() is expected to exist.
        import locale
        locale.setlocale(locale.LC_ALL, '')  # http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x
        
        print "v" * 50
        self.umlworkspace.Dump()
        print
        print "  MISC Scaling etc info "
        print
        self.coordmapper.DumpCalibrationInfo(dump_nodes=False)
        print "line-line intersections", len(self.umlworkspace.graph.CountLineOverLineIntersections())
        print "node-node overlaps", self.overlap_remover.CountOverlaps()
        print "line-node crossings", self.umlworkspace.graph.CountLineOverNodeCrossings()['ALL']/2 #, self.graph.CountLineOverNodeCrossings()
        print "bounds", self.umlworkspace.graph.GetBounds()


        #print "SHAPE to classname list: -------------------"
        #for shape in self.umlboxshapes:
        #    print 'shape', shape, shape.node.classname

        print
        print "^" * 50

  
    def CmdRememberLayout1(self):
        self.snapshot_mgr.QuickSave(slot=1)
    def CmdRememberLayout2(self):
        self.snapshot_mgr.QuickSave(slot=2)
    def CmdRestoreLayout1(self):
        self.snapshot_mgr.QuickRestore(slot=1)
    def CmdRestoreLayout2(self):
        self.snapshot_mgr.QuickRestore(slot=2)

   
    def SelectNodeNow(self, shape):
        canvas = shape.GetCanvas()

        self.observers.CMD_DESELECT_ALL_SHAPES()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        shape.Select(True, dc)  # could pass None as dc if you don't want to trigger the OnDrawControlPoints(dc) handler immediately - e.g. if you want to do a complete redraw of everything later anyway
        #canvas.Refresh(False)   # t/f or don't use - doesn't seem to make a difference
        
        #self.UpdateStatusBar(shape)  # only available in the shape evt handler (this method used to live there...)

    def delete_shape_view(self, shape):
        # View
        self.observers.CMD_DESELECT_ALL_SHAPES()
        for line in shape.GetLines()[:]:
            line.Delete()
        shape.Delete()

    def Clear(self):
        print "Draw: Clear"
        self.GetDiagram().DeleteAllShapes()

        dc = wx.ClientDC(self)
        self.GetDiagram().Clear(dc)   # only ends up calling dc.Clear() - I wonder if this clears the screen?

        self.save_gdi = []
        
        self.umlworkspace.Clear()

    def NewEdgeMarkFrom(self):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if not selected:
            print "Please select a node"
            return
        
        self.new_edge_from = selected[0].node
        print "From", self.new_edge_from.id

    def NewEdgeMarkTo(self):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if not selected:
            print "Please select a node"
            return
        
        tonode = selected[0].node
        print "To", tonode.id
        
        if self.new_edge_from == None:
            print "Please set from node first"
            return
        
        if self.new_edge_from.id == tonode.id:
            print "Can't link to self"
            return
        
        if not self.umlworkspace.graph.FindNodeById(self.new_edge_from.id):
            print "From node %s doesn't seem to be in graph anymore!" % self.new_edge_from.id
            return
        
        edge = self.umlworkspace.graph.AddEdge(self.new_edge_from, tonode, weight=None)
        # TODO should also arguably add to umlworkspace's associations_composition or associations_generalisation list (or create a new one for unlabelled associations like the one we are creating here)
        edge['uml_edge_type'] = ''
        #edge['uml_edge_type'] = 'composition'
        self.CreateUmlEdge(edge)
        self.stateofthenation()

    def ConvertParseModelToUmlModel(self, p):
        
        def BuildEdgeModel(association_tuples, edge_label):
            for fromClassname, toClassname in association_tuples:
                from_node = self.umlworkspace.AddUmlNode(fromClassname)
                to_node = self.umlworkspace.AddUmlNode(toClassname)
                edge = self.umlworkspace.graph.AddEdge(from_node, to_node)
                edge['uml_edge_type'] = edge_label
            
        def AddGeneralisation(classname, parentclass):
            if (classname, parentclass) in self.umlworkspace.associations_generalisation:
                #print "DUPLICATE Generalisation skipped when ConvertParseModelToUmlModel", (classname, parentclass) # DUPLICATE DETECTION
                return
            self.umlworkspace.associations_generalisation.append((classname, parentclass))

        def AddDependency(otherclass, classname):
            if (otherclass, classname) in self.umlworkspace.associations_composition:
                #print "DUPLICATE Dependency skipped when ConvertParseModelToUmlModel", (otherclass, classname) # DUPLICATE DETECTION
                return
            self.umlworkspace.associations_composition.append((otherclass, classname))  # reverse direction so round black arrows look ok

        for classname, classentry in p.classlist.items():
            """
            These are a list of (attr, otherclass) however they imply that THIS class
            owns all those other classes.
            """
            #print 'CLASS', classname, classentry
            
            # Composition / Dependencies
            for attr, otherclass in classentry.classdependencytuples:
                AddDependency(otherclass, classname)

            # Generalisations
            if classentry.classesinheritsfrom:
                for parentclass in classentry.classesinheritsfrom:

                    #if parentclass.find('.') <> -1:         # fix names like "unittest.TestCase" into "unittest"
                    #    parentclass = parentclass.split('.')[0] # take the lhs
                    AddGeneralisation(classname, parentclass)

            classAttrs = [ attrobj.attrname for attrobj in classentry.attrs ]
            classMeths = classentry.defs
            node = self.umlworkspace.AddUmlNode(classname, classAttrs, classMeths)

        # ensure no duplicate relationships exist
        assert len(set(self.umlworkspace.associations_composition)) == len(self.umlworkspace.associations_composition), self.umlworkspace.associations_composition        # ensure no duplicates exist
        assert len(set(self.umlworkspace.associations_generalisation)) == len(self.umlworkspace.associations_generalisation), self.umlworkspace.associations_generalisation        # ensure no duplicates exist

        BuildEdgeModel(self.umlworkspace.associations_generalisation, 'generalisation')
        BuildEdgeModel(self.umlworkspace.associations_composition, 'composition')
  
    def Go(self, files=None, path=None):

        # these are tuples between class names.
        self.umlworkspace.ClearAssociations()       # WHY DO WE WANT TO DESTROY THIS VALUABLE INFO?

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
              
    def CreateImageShape(self, F):
        #shape = ogl.BitmapShape()
        shape = BitmapShapeResizable()
        img = wx.Image(F, wx.BITMAP_TYPE_ANY)
        
        #adjusted_img = img.AdjustChannels(factor_red = 1., factor_green = 1., factor_blue = 1., factor_alpha = 0.5)
        #adjusted_img = img.Rescale(10,10)
        adjusted_img = img
        
        bmp = wx.BitmapFromImage(adjusted_img)
        shape.SetBitmap(bmp)

        self.GetDiagram().AddShape(shape)
        shape.Show(True)

        evthandler = UmlShapeHandler(self.log, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.observers.NOTIFY_EVT_HANDLER_CREATED(evthandler) # allow app.controller to become observer of new evthandler, without knowing about controller here

        setpos(shape, 0, 0)
        #setpos(shape, node.left, node.top)
        #node.width, node.height = shape.GetBoundingBoxMax()
        #node.shape = shape
        #shape.node = node
        return shape
        
    def CreateUmlShape(self, node):

        def newRegion(font, name, textLst, maxWidth, totHeight = 10):
            # Taken from Boa, but put into the canvas class instead of the scrolled window class.
            region = ogl.ShapeRegion()
            
            if len(textLst) == 0:
                return region, maxWidth, 0
                
            dc = wx.ClientDC(self)  # self is the canvas
            dc.SetFont(font)
    
            for text in textLst:
                w, h = dc.GetTextExtent(text)
                if w > maxWidth: maxWidth = w
                totHeight = totHeight + h + 0 # interline padding
    
            region.SetFont(font)
            region.SetText('\n'.join(textLst))
            region.SetName(name)
    
            return region, maxWidth, totHeight

        shape = DividedShape(width=99, height=98, canvas=self)
        maxWidth = 10 # min node width, grows as we update it with text widths
        
        """
        Future: Perhaps be able to show regions or not. Might need to totally
        reconstruct the shape.
        """
        #if not self.showAttributes: classAttrs = [' ']
        #if not self.showMethods: classMeths = [' ']

        # Create each region.  If height returned is 0 this means don't create this region.
        regionName, maxWidth, nameHeight = newRegion(self.font1, 'class_name', [node.classname], maxWidth)
        regionAttribs, maxWidth, attribsHeight = newRegion(self.font2, 'attributes', node.attrs, maxWidth)
        regionMeths, maxWidth, methsHeight = newRegion(self.font2, 'methods', node.meths, maxWidth)

        # Work out total height of shape
        totHeight = nameHeight + attribsHeight + methsHeight

        # Set regions to be a proportion of the total height of shape
        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        regionAttribs.SetProportions(0.0, 1.0*(attribsHeight/float(totHeight)))
        regionMeths.SetProportions(0.0, 1.0*(methsHeight/float(totHeight)))

        # Add regions to the shape
        shape.AddRegion(regionName)
        if attribsHeight:   # Dont' make a region unless we have to
            shape.AddRegion(regionAttribs)
        if methsHeight:     # Dont' make a region unless we have to
            shape.AddRegion(regionMeths)

        shape.SetSize(maxWidth + 10, totHeight + 10)
        shape.SetCentreResize(False)  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).

        regionName.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ)
        shape.region1 = regionName  # Andy added, for later external reference to classname from just having the shape instance.
        
        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetPen(wx.BLACK_PEN)   # Controls the color of the border of the shape
        shape.SetBrush(wx.Brush("WHEAT", wx.SOLID))
        setpos(shape, node.left, node.top)
        self.GetDiagram().AddShape(shape) # self.AddShape is ok too, ShapeCanvas's AddShape is delegated back to Diagram's AddShape.  ShapeCanvas-->Diagram
        shape.Show(True)

        evthandler = UmlShapeHandler(self.log, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.observers.NOTIFY_EVT_HANDLER_CREATED(evthandler) # allow app.controller to become observer of new evthandler, without knowing about controller here
        
        shape.FlushText()

        # Don't set the node left,top here as the shape needs to conform to the node.
        # On the other hand the node needs to conform to the shape's width,height.
        # ACTUALLY I now do set the pos of the shape, see above,
        # just before the AddShape() call.
        #
        node.width, node.height = shape.GetBoundingBoxMax()
        node.shape = shape
        shape.node = node
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
        evthandler = UmlShapeHandler(None, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.observers.NOTIFY_EVT_HANDLER_CREATED(evthandler) # allow app.controller to become observer of new evthandler, without knowing about controller here

    def createCommentShape(self, node):
        shape = ogl.TextShape( node.width, node.height )
            
        shape.SetCanvas(self)
        shape.SetPen(wx.BLACK_PEN)
        shape.SetBrush(wx.LIGHT_GREY_BRUSH)
        shape.SetBrush(wx.RED_BRUSH)
        for line in node.comment.split('\n'):
            shape.AddText(line)
        
        setpos(shape, node.left, node.top)
        #shape.SetDraggable(True, True)
        self.AddShape( shape )
        node.shape = shape
        shape.node = node
        
        # wire in the event handler for the new shape
        evthandler = UmlShapeHandler(None, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.observers.NOTIFY_EVT_HANDLER_CREATED(evthandler) # allow app.controller to become observer of new evthandler, without knowing about controller here

        
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
        #print "OnWheelZoom"
        if self.working: return
        self.working = True

        if event.GetWheelRotation() < 0:
            self.cmdLayoutContract(event)
        else:
            self.cmdLayoutExpand(event)

        self.working = False

    def OnWheelZoom_OverlapRemoval_Defunct(self, event):
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
        print "Draw: stage1"
        if translatecoords:
            self.AllToWorldCoords()

        # Clear existing visualisation
        for node in self.umlworkspace.graph.nodes:
            if node.shape:
                self.delete_shape_view(node.shape)
                node.shape = None

        # Create fresh visualisation
        for node in self.umlworkspace.graph.nodes:
            assert not node.shape
            shape = self.CreateUmlShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            
        for edge in self.umlworkspace.graph.edges:
            self.CreateUmlEdge(edge)

        self.Redraw222()

    def stage2(self, force_stateofthenation=False, watch_removals=True):
        print "Draw: stage2 force_stateofthenation=", force_stateofthenation
        ANIMATION = False
        
        #if ANIMATION:
        #    self.graph.SaveOldPositionsForAnimationPurposes()
        #    watch_removals = False  # added this when I turned animation on.
        
        self.overlap_remover.RemoveOverlaps(watch_removals=watch_removals)
        if self.overlap_remover.GetStats()['total_overlaps_found'] > 0 or force_stateofthenation:
            self.stateofthenation(animate=ANIMATION)

    def stateofthenation(self, animate=False):
        print "Draw: stateofthenation"
        for node in self.umlworkspace.graph.nodes:
            self.AdjustShapePosition(node)
        self.Redraw222()
        wx.SafeYield()

    def stateofthespring(self):
        print "Draw: stateofthespring"
        self.coordmapper.Recalibrate()
        self.AllToWorldCoords()
        self.stateofthenation() # DON'T do overlap removal or it will get mad!
                
    def RedrawEverything(self):
        print "Draw: RedrawEverything"
        diagram = self.GetDiagram()
        canvas = self
        assert self == canvas == diagram.GetCanvas()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.umlboxshapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
            if shape.__class__.__name__ == 'DividedShape':
                shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)

        """
        Do we need any of this?  YES.
        Annoying to have a hack, esp if it keeps forcing calls to Recalibrate()
        But we need it so that the Recalibrate() is called at least once
        """
        #self.frame.SetScrollbars(needs lots of weird args...)
        # or
        #self.SetScrollbars(needs lots of weird args...)
        #
        # Hack To Force The Scrollbar To Show Up
        # Set the window size to something different
        # Return the size to what it was
        #
        oldSize = self.frame.GetSize()
        self.frame.SetSize((oldSize[0]+1,oldSize[1]+1))
        self.frame.SetSize(oldSize)

    def CmdLayout(self):
        print "Draw: CmdLayout"
        #print
        #print "CmdLayout"
        #print
        if self.GetDiagram().GetCount() == 0:
            #self.frame.MessageBox("Nothing to layout.  Import a python source file first.")
            return
        
        self.LayoutAndPositionShapes()
        self.RedrawEverything()

    def CmdDeepLayout_OFFLINE(self):
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        wx.SafeYield()
        try:
            b = LayoutBlackboard(graph=self.umlworkspace.graph, controller=self)
            b.LayoutMultipleChooseBest(4)
        finally:
            wx.EndBusyCursor()

    def CmdDeepLayout(self):
        from blackboard_thread import MainBlackboardFrame
        """Init Main App."""
        f = MainBlackboardFrame(parent=self.frame)
        f.Show(True)
        
        b = LayoutBlackboard(graph=self.umlworkspace.graph, controller=self)
        f.SetBlackboardObject(b)
        f.Start(num_attempts=3)
        print "CmdDeepLayout end"

    def ReLayout(self, keep_current_positions=False, gui=None, optimise=True):
        print "Draw: ReLayout"
        self.AllToLayoutCoords()
        self.layouter.layout(keep_current_positions, optimise=optimise)
        self.AllToWorldCoords()
        self.stage2() # does overlap removal and stateofthenation
    
    def LayoutAndPositionShapes(self):
        print "Draw: LayoutAndPositionShapes"
        self.ReLayout()
        return
    
        #positions, shapeslist, newdiagramsize = self.layout.Layout(self.umlworkspace, self.umlboxshapes)
        #print "Layout positions", positions
        #
        #self.setSize(newdiagramsize)
        #
        #dc = wx.ClientDC(self)
        #self.PrepareDC(dc)
        #
        ## Now move the shapes into place.
        #for (pos, classShape) in zip(positions, shapeslist):
        #    #print pos, classShape.region1.GetText()
        #    x, y = pos
        #
        #    # compensate for the fact that x, y for a ogl shape are the centre of the shape, not the top left
        #    width, height = classShape.GetBoundingBoxMax()
        #    x += width/2
        #    y += height/2
        #
        #    classShape.Move(dc, x, y, False)
        #
        ##self.umlworkspace.Dump()
        
        
    def setSize(self, size):
        size = wx.Size(size[0], size[1])
        
        nvsx, nvsy = size.x / self.scrollStepX, size.y / self.scrollStepY
        self.Scroll(0, 0)
        self.SetScrollbars(self.scrollStepX, self.scrollStepY, nvsx, nvsy)
        canvas = self
        canvas.SetSize(canvas.GetVirtualSize())


    def AdjustShapePosition(self, node, point=None):   # FROM SPRING LAYOUT
        print "Draw:  AdjustShapePosition", node.left, node.top
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
        #self.RedrawEverything() # HACK
        #return
        
        print "Draw: Redraw222   clear=", clear
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
        self.observers.CMD_DESELECT_ALL_SHAPES()


