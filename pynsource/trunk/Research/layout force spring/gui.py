# Gui for testing Layout

import wx
import wx.lib.ogl as ogl
import time
import thread
import random
from graph import *
from layout_spring import GraphLayoutSpring
from overlap_removal import OverlapRemoval
from blackboard import LayoutBlackboard
from coordinate_mapper import CoordinateMapper
from snapshots import GraphSnapshotMgr
from data_testgraphs import *

UNIT_TESTING_MODE = True

def setpos(shape, x, y):
    width, height = shape.GetBoundingBoxMax()
    shape.SetX( x + width/2 )
    shape.SetY( y + height/2 )
def getpos(shape):
    width, height = shape.GetBoundingBoxMax()
    x = shape.GetX()
    y = shape.GetY()
    return (x - width/2, y - height/2)

class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, oglcanvas):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.oglcanvas = oglcanvas

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        x, y = getpos(shape)
        width, height = shape.GetBoundingBoxMax()
        frame = self.oglcanvas.GetTopLevelParent()
        frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)  -  GraphNode is %s" % (x, y, width, height, shape.node))

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        #print "OnLeftClick"
        shape = self.GetShape()
        
        # size handles
        shape.GetCanvas().graphrendererogl.DeselectAllShapes()
        shape.Select(True, None)
        shape.GetCanvas().graphrendererogl.stateofthenation()
        
        self.UpdateStatusBar(shape)
            
    def OnDrawOutline(self, dc, x, y, w, h):
        ogl.ShapeEvtHandler.OnDrawOutline(self, dc, x, y, w, h)
        shape = self.GetShape()
        x,y = (x - w/2, y - h/2) # correct to be top corner not centre
        frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)  -  GraphNode is %s" % (x, y, w, h, shape.node))
        
    def OnDragLeft(self, draw, x, y, keys = 0, attachment = 0):
        ogl.ShapeEvtHandler.OnDragLeft(self, draw, x, y, keys = 0, attachment = 0)
        # x, y are the merely the mouse position thus useless for getting to shape x,y - intercept OnDrawOutline instead 
        
    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()

        # take care of selection points
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        
        oldpos = getpos(shape) # (int(shape.GetX()), int(shape.GetY()))
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)  # super
        newpos = getpos(shape) # (int(shape.GetX()), int(shape.GetY()))

        print shape.node.id, "moved from", oldpos, "to", newpos
        
        # Adjust the GraphNode to match the shape x,y
        shape.node.left, shape.node.top = newpos

        self.UpdateStatusBar(shape)

        wx.SafeYield()
        time.sleep(0.2)
        
        shape.GetCanvas().graphrendererogl.stage2()

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

        wx.SafeYield()
        time.sleep(0.2)
        
        shape.GetCanvas().graphrendererogl.stage2()
        
class GraphShapeCanvas(ogl.ShapeCanvas):
    scrollStepX = 10
    scrollStepY = 10
    classnametoshape = {}

    def __init__(self, parent):
        ogl.ShapeCanvas.__init__(self, parent)

    def OnLeftClick(self, x, y, keys):  # Override of ShapeCanvas method
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        self.graphrendererogl.DeselectAllShapes()

class GraphRendererOgl:
    def __init__(self, graph, oglcanvas):
        self.graph = graph
        self.oglcanvas = oglcanvas
        self.oglcanvas.graphrendererogl = self
        self.coordmapper = CoordinateMapper(self.graph, self.oglcanvas.GetSize())

        self.oglcanvas.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        self.oglcanvas.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonMenu)
        self.oglcanvas.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.oglcanvas.Bind(wx.EVT_CHAR, self.onKeyChar)
        self.oglcanvas.Bind(wx.EVT_SIZE, self.OnResizeFrame)
        
        self.popupmenu = None
        self.need_abort = False
        self.new_edge_from = None
        self.working = False
        self.snapshot_mgr = GraphSnapshotMgr(graph=self.graph, controller=self)

        if UNIT_TESTING_MODE:
            self.overlap_remover = OverlapRemoval(self.graph, margin=5, gui=self)
        else:
            self.overlap_remover = OverlapRemoval(self.graph, margin=50, gui=self)

    def AllToLayoutCoords(self):
            self.coordmapper.AllToLayoutCoords()

    def AllToWorldCoords(self):
            self.coordmapper.AllToWorldCoords()

    def OnResizeFrame (self, event):   # ANDY  interesting - GetVirtualSize grows when resize frame
        frame = self.oglcanvas.GetTopLevelParent()
        print "frame resize", frame.GetClientSize()
        self.coordmapper.Recalibrate(frame.GetClientSize()) # may need to call self.CalcVirtSize() if scrolled window
   
    def DeselectAllShapes(self):
        selected = [s for s in self.oglcanvas.GetDiagram().GetShapeList() if s.Selected()]
        if selected:
            s = selected[0]
            canvas = s.GetCanvas()
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            s.Select(False, dc)
            canvas.Refresh(False)   # Need this or else Control points ('handles') leave blank holes      

    def InsertNewNode(self):
        id = 'D' + str(random.randint(1,99))
        dialog = wx.TextEntryDialog ( None, 'Enter an id string:', 'Create a new node', id )
        if dialog.ShowModal() == wx.ID_OK:
            id = dialog.GetValue()
            if self.graph.FindNodeById(id):
                id += str(random.randint(1,9999))
            node = GraphNode(id, random.randint(0, 100),random.randint(0,100),random.randint(60, 160),random.randint(60,160))
            node = self.graph.AddNode(node)
            self.createNodeShape(node)
            node.shape.Show(True)
            self.stateofthenation()
        dialog.Destroy()

    def DeleteSelectedNode(self):
        selected = [s for s in self.oglcanvas.GetDiagram().GetShapeList() if s.Selected()]
        if selected:
            shape = selected[0]
            print 'delete', shape.node.id

            # model
            self.graph.DeleteNodeById(shape.node.id)

            # view
            self.DeselectAllShapes()
            for line in shape.GetLines()[:]:
                line.Delete()
            shape.Delete()

    def NewEdgeMarkFrom(self):
        selected = [s for s in self.oglcanvas.GetDiagram().GetShapeList() if s.Selected()]
        if not selected:
            print "Please select a node"
            return
        
        self.new_edge_from = selected[0].node
        print "From", self.new_edge_from.id

    def NewEdgeMarkTo(self):
        selected = [s for s in self.oglcanvas.GetDiagram().GetShapeList() if s.Selected()]
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
        
        if not self.graph.FindNodeById(self.new_edge_from.id):
            print "From node %s doesn't seem to be in graph anymore!" % self.new_edge_from.id
            return
        
        edge = self.graph.AddEdge(self.new_edge_from, tonode, weight=None)
        self.createEdgeShape(edge)
        self.stateofthenation()

    def OnWheelZoom(self, event):
        if self.working: return
        self.working = True

        if event.GetWheelRotation() < 0:
            self.stage2()
            print self.overlap_remover.GetStats()
        else:
            self.stateofthenation()

        self.working = False

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
            print "LL/raw %d/%d" % (len(self.graph.CountLineOverLineIntersections(ignore_nodes=False)), \
                                                len(self.graph.CountLineOverLineIntersections(ignore_nodes=True)))
            
        elif keycode == wx.WXK_LEFT:
            if self.coordmapper.scale < 3:
                self.ChangeScale(0.2, remap_world_to_layout=event.ShiftDown(), removeoverlaps=not event.ControlDown())
                print "contraction ", self.coordmapper.scale
            else:
                print "Min expansion thwarted.", self.coordmapper.scale
            print "LL/raw %d/%d" % (len(self.graph.CountLineOverLineIntersections(ignore_nodes=False)), \
                                                len(self.graph.CountLineOverLineIntersections(ignore_nodes=True)))
            
        elif keycode == wx.WXK_DELETE:
            self.DeleteSelectedNode()

        elif keycode == wx.WXK_INSERT:
            self.InsertNewNode()

        self.working = False
        event.Skip()

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
            
        elif keycode == '(':
            self.snapshot_mgr.QuickSave(slot=1)
            
        elif keycode == ')':
            self.snapshot_mgr.QuickSave(slot=2)

        elif keycode == '9':
            self.snapshot_mgr.QuickRestore(slot=1)

        elif keycode == '0':
            self.snapshot_mgr.QuickRestore(slot=2)

        elif keycode in ['1','2','3','4','5','6','7','8']:
            todisplay = ord(keycode) - ord('1')
            self.snapshot_mgr.Restore(todisplay)

        elif keycode in ['x', 'X', 'z', 'Z', 'c', 'C']:
            if keycode in ['Z','z']:
                strategy = ":reduce pre overlap removal NN overlaps"
            elif keycode in ['X','x']:
                strategy = ":reduce post overlap removal LN crossings"
            elif keycode in ['C','c']:
                strategy = ":reduce post overlap removal LN and LL crossings"
            b = LayoutBlackboard(graph=self.graph, controller=self)
            b.LayoutThenPickBestScale(scramble=keycode in ['Z','X','C'], strategy=strategy)
            
        elif keycode in ['e',]:
            b = LayoutBlackboard(graph=self.graph, controller=self)
            b.Experiment1()

        elif keycode in ['r', 'R']:
            b = LayoutBlackboard(graph=self.graph, controller=self)
            b.LayoutLoopTillNoChange(scramble=keycode == 'R')

        elif keycode in ['b', 'B']:
            b = LayoutBlackboard(graph=self.graph, controller=self)
            b.LayoutMultipleChooseBest(4)
            
        elif keycode in ['?',]:
            self.DumpStatus()
            
        self.working = False
        event.Skip()

    def DumpStatus(self):
        #print "-"*50
        print "scale", self.coordmapper.scale
        print "line-line intersections", len(self.graph.CountLineOverLineIntersections())
        print "node-node overlaps", self.overlap_remover.CountOverlaps()
        print "line-node crossings", self.graph.CountLineOverNodeCrossings()['ALL']/2 #, self.graph.CountLineOverNodeCrossings()
        print "bounds", self.graph.GetBounds()
        
    def draw(self, translatecoords=True):
        self.stage1(translatecoords=translatecoords)
        #thread.start_new_thread(self.DoSomeLongTask, ())

    def stage1(self, translatecoords=True):
        import time
        
        if translatecoords:
            self.AllToWorldCoords()

        for node in self.graph.nodes:
            self.createNodeShape(node)
        for edge in self.graph.edges:
            self.createEdgeShape(edge)

        self.Redraw()

    def stage2(self, force_stateofthenation=False, watch_removals=True):
        self.graph.SaveOldPositionsForAnimationPurposes()
        watch_removals = False  # added this when I turned animation on.
        
        self.overlap_remover.RemoveOverlaps(watch_removals=watch_removals)
        if self.overlap_remover.GetStats()['total_overlaps_found'] > 0 or force_stateofthenation:
            self.stateofthenation(animate=True)
        
    def stateofthenation(self, animate=False):
        if animate:
            from animation import GeneratePoints
            
            for node in self.graph.nodes:
                node.anilist = GeneratePoints((node.previous_left, node.previous_top), (node.left, node.top), steps=5)

            dc = wx.ClientDC(self.oglcanvas)
            self.oglcanvas.PrepareDC(dc)
            for i in range(len(self.graph.nodes[0].anilist)):
                for node in self.graph.nodes:
                    point = node.anilist.pop(0)
                    x, y = point
                    #node.shape.Move(dc, x, y, True) # don't do this or it will flicker
                    setpos(node.shape, x, y)
                    node.shape.MoveLinks(dc)
                    self.Redraw(clear=False)
                self.Redraw()
            
        else:
            for node in self.graph.nodes:
                self.AdjustShapePosition(node)
            self.Redraw()
            wx.SafeYield()
        
    def stateofthespring(self):
        self.coordmapper.Recalibrate()
        self.AllToWorldCoords()
        self.stateofthenation() # DON'T do overlap removal or it will get mad!

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
        
    def ReLayout(self, keep_current_positions=False, gui=None, optimise=True):
        self.AllToLayoutCoords()

        layouter = GraphLayoutSpring(self.graph, gui)    # should keep this around
        layouter.layout(keep_current_positions, optimise=optimise)
        
        self.AllToWorldCoords()
        self.stage2() # does overlap removal and stateofthenation
        
    def AdjustShapePosition(self, node, point=None):
        assert node.shape
        
        if point:
            x, y = point
        else:
            x, y = node.left, node.top
            
        # Don't need to use node.shape.Move(dc, x, y, False)
        setpos(node.shape, x, y)

        # But you DO need to use a dc to adjust the links
        dc = wx.ClientDC(self.oglcanvas)
        self.oglcanvas.PrepareDC(dc)
        node.shape.MoveLinks(dc)
        
    def Redraw(self, clear=True):
        diagram = self.oglcanvas.GetDiagram()
        canvas = self.oglcanvas
        assert canvas == diagram.GetCanvas()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        
        #for node in self.graph.nodes:    # TODO am still moving nodes in the pynsourcegui version?
        #    shape = node.shape
        #    shape.Move(dc, shape.GetX(), shape.GetY())
        
        if clear:
            diagram.Clear(dc)
        diagram.Redraw(dc)
     
    def createNodeShape(self, node):
        shape = ogl.RectangleShape( node.width, node.height )
        shape.AddText(node.id)
        setpos(shape, node.left, node.top)
        #shape.SetDraggable(True, True)
        self.oglcanvas.AddShape( shape )
        node.shape = shape
        shape.node = node
        
        # wire in the event handler for the new shape
        evthandler = MyEvtHandler(None, self.oglcanvas)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
       
    def createEdgeShape(self, edge):
        line = ogl.LineShape()
        line.SetCanvas(self.oglcanvas)
        line.SetPen(wx.BLACK_PEN)
        line.SetBrush(wx.BLACK_BRUSH)
        line.MakeLineControlPoints(2)
       
        fromShape = edge['source'].shape
        toShape = edge['target'].shape
        fromShape.AddLine(line, toShape)
        self.oglcanvas.GetDiagram().AddShape(line)
        line.Show(True)
        
    def OnRightButtonMenu(self, event):   # Menu
        x, y = event.GetPosition()
        frame = self.oglcanvas.GetTopLevelParent()
        
        if self.popupmenu:
            self.popupmenu.Destroy()    # wx.Menu objects need to be explicitly destroyed (e.g. menu.Destroy()) in this situation. Otherwise, they will rack up the USER Objects count on Windows; eventually crashing a program when USER Objects is maxed out. -- U. Artie Eoff  http://wiki.wxpython.org/index.cgi/PopupMenuOnRightClick
        self.popupmenu = wx.Menu()     # Create a menu
        
        item = self.popupmenu.Append(2015, "Load Graph from text...")
        frame.Bind(wx.EVT_MENU, self.OnLoadGraphFromText, item)
        
        item = self.popupmenu.Append(2017, "Dump Graph to console")
        frame.Bind(wx.EVT_MENU, self.OnSaveGraphToConsole, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(2011, "Load Graph...")
        frame.Bind(wx.EVT_MENU, self.OnLoadGraph, item)
        
        item = self.popupmenu.Append(2012, "Save Graph...")
        frame.Bind(wx.EVT_MENU, self.OnSaveGraph, item)

        self.popupmenu.AppendSeparator()

        imp = wx.Menu()
        item = imp.Append(2021, "Load Test Graph 1"); frame.Bind(wx.EVT_MENU, self.OnLoadTestGraph1, item)
        item = imp.Append(2022, "Load Test Graph 2"); frame.Bind(wx.EVT_MENU, self.OnLoadTestGraph2, item)
        item = imp.Append(2023, "Load Test Graph 3"); frame.Bind(wx.EVT_MENU, self.OnLoadTestGraph3, item)
        item = imp.Append(2023, "Load Test Graph 3a"); frame.Bind(wx.EVT_MENU, self.OnLoadTestGraph3a, item)
        item = imp.Append(2024, "Load Test Graph 4"); frame.Bind(wx.EVT_MENU, self.OnLoadTestGraph4, item)
        item = imp.Append(2025, "Load Test Graph 6 (line overlaps)"); frame.Bind(wx.EVT_MENU, self.OnLoadTestGraph6, item)
        item = imp.Append(2026, "Load Test Graph 7"); frame.Bind(wx.EVT_MENU, self.OnLoadTestGraph7, item)
        self.popupmenu.AppendMenu(-1, 'Unit Test Graphs', imp)

        imp = wx.Menu()
        item = imp.Append(2031, "Spring 2"); frame.Bind(wx.EVT_MENU, self.OnLoadSpring2, item)
        item = imp.Append(2032, "Spring 3"); frame.Bind(wx.EVT_MENU, self.OnLoadSpring3, item)
        self.popupmenu.AppendMenu(-1, 'Other Test Graphs', imp)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(2014, "Clear")
        frame.Bind(wx.EVT_MENU, self.OnClear, item)  # must pass item

        item = self.popupmenu.Append(2013, "Cancel")
        #frame.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        
        frame.PopupMenu(self.popupmenu, wx.Point(x,y))

    def OnLoadTestGraph1(self, event):
        self.LoadGraph(TEST_GRAPH1)
        
    def OnLoadTestGraph2(self, event):
        self.LoadGraph(TEST_GRAPH2)
        
    def OnLoadTestGraph3(self, event):
        self.LoadGraph(TEST_GRAPH3)

    def OnLoadTestGraph3a(self, event):
        self.LoadGraph(TEST_GRAPH3A)

    def OnLoadTestGraph4(self, event):
        self.LoadGraph(TEST_GRAPH4)

    def OnLoadTestGraph6(self, event):
        self.LoadGraph(TEST_GRAPH6)

    def OnLoadTestGraph7(self, event):
        self.LoadGraph(TEST_GRAPH7)

    def OnLoadSpring2(self, event):
        self.LoadGraph(GRAPH_SPRING2)

    def OnLoadSpring3(self, event):
        self.LoadGraph(GRAPH_SPRING3)

    def OnSaveGraphToConsole(self, event):
        print self.graph.GraphToString()

    def OnSaveGraph(self, event):
        frame = self.oglcanvas.GetTopLevelParent()
        dlg = wx.FileDialog(parent=frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.txt", style=wx.FD_SAVE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            
            fp = open(filename, "w")
            fp.write(self.graph.GraphToString())
            fp.close()
        dlg.Destroy()
        
    def OnLoadGraphFromText(self, event):
        eg = "{'type':'node', 'id':'A', 'x':142, 'y':129, 'width':250, 'height':250}"
        dialog = wx.TextEntryDialog ( None, 'Enter an node/edge persistence strings:', 'Create a new node', eg,  style=wx.OK|wx.CANCEL|wx.TE_MULTILINE )
        if dialog.ShowModal() == wx.ID_OK:
            txt = dialog.GetValue()
            self.LoadGraph(txt)
            
    def OnLoadGraph(self, event):
        frame = self.oglcanvas.GetTopLevelParent()
        dlg = wx.FileDialog(parent=frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.txt", style=wx.OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            fp = open(filename, "r")
            s = fp.read()
            fp.close()

            self.LoadGraph(s)
        dlg.Destroy()

    def LoadGraph(self, filedata=""):
        self.Clear()
        
        self.graph.LoadGraphFromStrings(filedata)
                
        # build view from model
        self.draw(translatecoords=False)
        
        # refresh view
        self.oglcanvas.GetDiagram().ShowAll(1) # need this, yes
        self.stateofthenation()

    def OnClear(self, event):
        self.Clear()
        
    def Clear(self):
        # Clear view        
        self.oglcanvas.GetDiagram().DeleteAllShapes()
        dc = wx.ClientDC(self.oglcanvas)
        self.oglcanvas.GetDiagram().Clear(dc)   # only ends up calling dc.Clear() - I wonder if this clears the screen?
        
        # clear model
        self.graph.Clear()
        
    def DoSomeLongTask(self):
        
        for i in range(1,50):
            if self.need_abort:
                print "aborted."
                return
            wx.CallAfter(self.stage2)
            #print '*',
            #wx.CallAfter(self.DoStuff)
            time.sleep(2)   # lets events through to the main wx thread and paints/messages get through ok
        print "Done."
        
        """
        print "Task started"
        if self.need_abort:
            print "aborted."
            return
        wx.CallAfter(self.stage1)
        #time.sleep(0.5)   # lets events through to the main wx thread and paints/messages get through ok
        #wx.CallAfter(self.stage2)
        print "Done."
        """
        
 
        

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__( self,
                          None, -1, "Andy's UML Layout Experimentation Sandbox",
                          size=(800,800),
                          style=wx.DEFAULT_FRAME_STYLE )
        sizer = wx.BoxSizer( wx.VERTICAL )
        # put stuff into sizer

        self.CreateStatusBar()

        canvas = GraphShapeCanvas(self) # ogl.ShapeCanvas( self )
        sizer.Add( canvas, 1, wx.GROW )

        canvas.SetBackgroundColour( "LIGHT BLUE" ) #

        diagram = ogl.Diagram()
        canvas.SetDiagram( diagram )
        diagram.SetCanvas( canvas )

        ## ==========================================
        
        g = Graph()
        
        a = GraphNode('A', 0, 0, 250, 250)
        a1 = GraphNode('A1', 0, 0)
        a2 = GraphNode('A2', 0, 0)
        g.AddEdge(a, a1)
        g.AddEdge(a, a2)

        b = GraphNode('B', 0, 0)
        b1 = GraphNode('B1', 0, 0)
        b2 = GraphNode('B2', 0, 0)
        g.AddEdge(b, b1)
        g.AddEdge(b, b2)

        b21 = GraphNode('B21', 0, 0)
        b22 = GraphNode('B22', 0, 0, 100, 200)
        g.AddEdge(b2, b21)
        g.AddEdge(b2, b22)

        c = GraphNode('c', 0, 0)
        c1 = GraphNode('c1', 0, 0)
        c2 = GraphNode('c2', 0, 0)
        c3 = GraphNode('c3', 0, 0)
        c4 = GraphNode('c4', 0, 0)
        c5 = GraphNode('c5', 0, 0, 60, 120)
        g.AddEdge(c, c1)
        g.AddEdge(c, c2)
        g.AddEdge(c, c3)
        g.AddEdge(c, c4)
        g.AddEdge(c, c5)
        g.AddEdge(a, c)
        
        g.AddEdge(b2, c)
        g.AddEdge(b2, c5)
        g.AddEdge(a, c5)

        layouter = GraphLayoutSpring(g)
        layouter.layout()
        
        for node in g.nodes:
            print node.id, (node.layoutPosX, node.layoutPosY)
        
        ## ==========================================
        
        # apply sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Show(1)

        ## ==========================================

        renderer = GraphRendererOgl(g, canvas);
        renderer.draw();
        
        diagram.ShowAll( 1 )
        

app = wx.PySimpleApp()
ogl.OGLInitialize()
frame = AppFrame()
app.MainLoop()
app.Destroy()
