import wx
import wx.lib.ogl as ogl
import time
import thread

from graph import *
from overlap_removal import OverlapRemoval
import random

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
        frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)  - div is %s" % (x, y, width, height, shape.node))

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        #print "OnLeftClick"
        shape = self.GetShape()
        
        # size handles
        shape.GetCanvas().graphrendererogl.DeselectAllShapes()
        shape.Select(True, None)
        shape.GetCanvas().graphrendererogl.stateofthenation()
        
        self.UpdateStatusBar(shape)
            
      
    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()

        # take care of selection points
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        
        oldpos = getpos(shape) # (int(shape.GetX()), int(shape.GetY()))
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)  # super
        newpos = getpos(shape) # (int(shape.GetX()), int(shape.GetY()))

        print shape.node.value.id, shape.node.value.left, shape.node.value.top, "moved from", oldpos, newpos
        
        # Adjust the Div to match the shape x,y
        shape.node.value.left, shape.node.value.top = newpos

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
        #print shape.node.value.id, shape.node.value.left, shape.node.value.top, "resized to", width, height
        # Adjust the Div to match the shape x,y
        shape.node.value.width, shape.node.value.height = width, height
        shape.node.value.left, shape.node.value.top = getpos(shape)
        
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

        self.radius = 10
        self.arrowAngle = Math.PI()/10

        width, height = oglcanvas.GetSize()
        self.factorX = (width/2 ) / (graph.layoutMaxX - graph.layoutMinX)
        self.factorY = (height/2 ) / (graph.layoutMaxY - graph.layoutMinY)

        self.oglcanvas.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        self.oglcanvas.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonMenu)
        self.oglcanvas.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        
        self.popupmenu = None
        self.need_abort = False

        self.overlap_remover = OverlapRemoval(self.graph, gui=self)

    def translate(self, point):
        return [
          (point[0] - self.graph.layoutMinX) * self.factorX + self.radius,
          (point[1] - self.graph.layoutMinY) * self.factorY + self.radius
        ]

    def rotate(self, point, length, angle):
        dx = length * Math.cos(angle)
        dy = length * Math.sin(angle)
        return [point[0]+dx, point[1]+dy]

        
    def translate_node_coords(self):
        for node in self.graph.nodes:
            point = self.translate([node.layoutPosX, node.layoutPosY])
            node.value.top      = int(point[1])
            node.value.left     = int(point[0])

       
    def DeselectAllShapes(self):
        selected = [s for s in self.oglcanvas.GetDiagram().GetShapeList() if s.Selected()]
        if selected:
            s = selected[0]
            canvas = s.GetCanvas()
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            s.Select(False, dc)
            canvas.Refresh(False)   # Need this or else Control points ('handles') leave blank holes      


        """
        shapeList = self.oglcanvas.GetDiagram().GetShapeList()

        def GetCanvasDc(s):
            canvas = s.GetCanvas()
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            return canvas, dc
            
        # If we unselect too early, some of the objects in
        # shapeList will become invalid (the control points are
        # shapes too!) and bad things will happen...
        toUnselect = []
        for s in shapeList:
            if s.Selected():
                toUnselect.append(s)

        if toUnselect:
            assert len(toUnselect) == 1
            for s in toUnselect:
                canvas, dc = GetCanvasDc(s)
                s.Select(False, dc)
                
            canvas, dc = GetCanvasDc(s)
            canvas.Refresh(False)
        """
    
    def onKeyPress(self, event):
        keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html
        #if event.ShiftDown():
        if keycode == wx.WXK_DOWN:
            print "DOWN"
        elif keycode == wx.WXK_RIGHT:
            print "RIGHT"
        elif keycode == wx.WXK_LEFT:
            print "LEFT"
        elif keycode == wx.WXK_UP:
            print "UP"
        elif keycode == wx.WXK_DELETE:
            print "DELETE"

            selected = [s for s in self.oglcanvas.GetDiagram().GetShapeList() if s.Selected()]
            if selected:
                shape = selected[0]
                print 'delete', shape.node.value.id

                # model
                self.graph.deleteNode(shape.node.value.id)

                # view
                self.DeselectAllShapes()
                for line in shape.GetLines()[:]:
                    line.Delete()
                shape.Delete()

                """
                print shape.GetLines()
                if True:
                    for line in shape.GetLines()[:]:
                        print 'delete', line, 'getlines is now', shape.GetLines()
                        line.Delete()
                        #line.Unlink()
                        #diagram.RemoveShape(line)
                else:                    
                    lineList = shape.GetLines()
                    toDelete = []
                    for line in shape.GetLines():
                        toDelete.append(line)
                        
                    for line in toDelete:
                        print 'delete', line
                        line.Unlink()
                        diagram.RemoveShape(line)                     
                    
                    
                diagram.RemoveShape(shape)
                """
                
                
                ## should do list clone instead, just don't want pointer want true copy of refs
                #lineList = shape.GetLines()
                #toDelete = []
                #for line in shape.GetLines():
                #    toDelete.append(line)
                #    
                #for line in toDelete:
                #    line.Unlink()
                #    diagram.RemoveShape(line)            
                #
                ## Uml related....
                #self.umlworkspace.DeleteShape(shape)
                #
                #assert shape in self.umlboxshapes
                #diagram.RemoveShape(shape)


        elif keycode == wx.WXK_INSERT:
            print "INSERT"
            
            id = 'D' + str(random.randint(1,99))
            dialog = wx.TextEntryDialog ( None, 'Enter an id string:', 'Create a new node', id )
            if dialog.ShowModal() == wx.ID_OK:
                id = dialog.GetValue()
                if self.graph.findNode(id):
                    id += str(random.randint(1,9999))
                div = Div(id, random.randint(0, 100),random.randint(0,100),random.randint(60, 160),random.randint(60,160))
                node = self.graph.addNode(div)
                self.drawNode(node)
                node.shape.Show(True)
                self.stateofthenation()
            dialog.Destroy()
   
            
            
        event.Skip()

    def OnRightButtonMenu(self, event):   # Menu

        x, y = event.GetPosition()
        frame = self.oglcanvas.GetTopLevelParent()
        
        if self.popupmenu:
            self.popupmenu.Destroy()    # wx.Menu objects need to be explicitly destroyed (e.g. menu.Destroy()) in this situation. Otherwise, they will rack up the USER Objects count on Windows; eventually crashing a program when USER Objects is maxed out. -- U. Artie Eoff  http://wiki.wxpython.org/index.cgi/PopupMenuOnRightClick
        self.popupmenu = wx.Menu()     # Create a menu
        
        item = self.popupmenu.Append(2011, "Load Graph...")
        frame.Bind(wx.EVT_MENU, self.OnLoadGraph, item)
        
        item = self.popupmenu.Append(2012, "Save Graph...")
        frame.Bind(wx.EVT_MENU, self.OnSaveGraph, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(2013, "Cancel")
        #frame.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        
        frame.PopupMenu(self.popupmenu, wx.Point(x,y))

            
    def OnSaveGraph(self, event):
        self.SaveGraph(None)
        return

        frame = self.oglcanvas.GetTopLevelParent()
        dlg = wx.FileDialog(parent=frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.txt", style=wx.FD_SAVE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.SaveGraph(filename)
            #self.MessageBox("graph saving not implemented yet")
        dlg.Destroy()
        
    def OnLoadGraph(self, event):
        self.LoadGraph(None)
        return
        frame = self.oglcanvas.GetTopLevelParent()
        dlg = wx.FileDialog(parent=frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.txt", style=wx.OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.LoadGraph(filename)
            self.MessageBox("graph loading not implemented yet")
        dlg.Destroy()

    def LoadGraph(self, filename):
        filedata = """
{'type':'node', 'id':'A', 'x':142, 'y':129, 'width':250, 'height':250}
{'type':'node', 'id':'A1', 'x':10, 'y':86, 'width':60, 'height':60}
{'type':'node', 'id':'A2', 'x':97, 'y':10, 'width':260, 'height':160}
{'type':'node', 'id':'B', 'x':256, 'y':103, 'width':60, 'height':60}
{'type':'node', 'id':'B1', 'x':345, 'y':10, 'width':160, 'height':60}
{'type':'node', 'id':'B2', 'x':149, 'y':229, 'width':60, 'height':60}
{'type':'node', 'id':'B21', 'x':16, 'y':251, 'width':60, 'height':420}
{'type':'node', 'id':'B22', 'x':68, 'y':338, 'width':100, 'height':100}
{'type':'node', 'id':'c', 'x':268, 'y':257, 'width':60, 'height':60}
{'type':'node', 'id':'c1', 'x':395, 'y':203, 'width':160, 'height':160}
{'type':'node', 'id':'c2', 'x':223, 'y':375, 'width':30, 'height':30}
{'type':'node', 'id':'c3', 'x':329, 'y':379, 'width':60, 'height':60}
{'type':'node', 'id':'c4', 'x':402, 'y':190, 'width':30, 'height':40}
{'type':'node', 'id':'c5', 'x':230, 'y':174, 'width':60, 'height':120}
{'type':'edge', 'id':'A_to_A1', 'source':'A', 'target':'A1'}
{'type':'edge', 'id':'A_to_A2', 'source':'A', 'target':'A2'}
{'type':'edge', 'id':'B_to_B1', 'source':'B', 'target':'B1'}
{'type':'edge', 'id':'B_to_B2', 'source':'B', 'target':'B2'}
{'type':'edge', 'id':'B2_to_B21', 'source':'B2', 'target':'B21'}
{'type':'edge', 'id':'B2_to_B22', 'source':'B2', 'target':'B22'}
{'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1'}
{'type':'edge', 'id':'c_to_c2', 'source':'c', 'target':'c2'}
{'type':'edge', 'id':'c_to_c3', 'source':'c', 'target':'c3'}
{'type':'edge', 'id':'c_to_c4', 'source':'c', 'target':'c4'}
{'type':'edge', 'id':'c_to_c5', 'source':'c', 'target':'c5'}
{'type':'edge', 'id':'A_to_c', 'source':'A', 'target':'c'}
{'type':'edge', 'id':'B2_to_c', 'source':'B2', 'target':'c'}
{'type':'edge', 'id':'B2_to_c5', 'source':'B2', 'target':'c5'}
{'type':'edge', 'id':'A_to_c5', 'source':'A', 'target':'c5'}
        """

        # Clear view        
        self.oglcanvas.GetDiagram().DeleteAllShapes()
        dc = wx.ClientDC(self.oglcanvas)
        self.oglcanvas.GetDiagram().Clear(dc)   # only ends up calling dc.Clear() - I wonder if this clears the screen?
        
        # clear model
        self.graph.clear()
        
        # load from persistence
        filedata = filedata.split('\n')
        for data in filedata:
            data = data.strip()
            if not data:
                continue
            print data
            data = eval(data)
            if data['type'] == 'node':
                # {'type':'node', 'id':'c5', 'x':230, 'y':174, 'width':60, 'height':120}
                div = Div(data['id'], data['x'], data['y'], data['width'], data['height'])
                self.graph.addNode(div)
            elif data['type'] == 'edge':
                source_id = data['source']
                target_id = data['target']
                # need to find the node corresponding to a div of id whatever
                # wire together the two divs
                sourcenode = self.graph.findNode(source_id)
                targetnode = self.graph.findNode(target_id)
                if not sourcenode:
                    print "Couldn't load source from persistence", source_id
                    continue
                if not targetnode:
                    print "Couldn't load target from persistence", target_id
                    continue
                self.graph.addEdge(sourcenode.value, targetnode.value)  # addEdge takes div objects as parameters
                
        # build view from model
        self.draw(tranlatecoords=False)
        
        # refresh view
        self.oglcanvas.GetDiagram().ShowAll(1) # need this, yes
        self.stateofthenation()

    def SaveGraph(self, filename):
        nodes = ""
        edges = ""
        for node in self.graph.nodes:
            v = node.value
            nodes += "{'type':'node', 'id':'%s', 'x':%d, 'y':%d, 'width':%d, 'height':%d}\n" % (v.id, v.left, v.top, v.width, v.height)
        for edge in self.graph.edges:
            source = edge['source'].value.id
            target = edge['target'].value.id
            edges += "{'type':'edge', 'id':'%s_to_%s', 'source':'%s', 'target':'%s'}\n" % (source, target, source, target)
        print nodes + edges
            
            
    def OnWheelZoom(self, event):
        self.stage2()

    def stage1(self, tranlatecoords=True):
        import time
        
        if tranlatecoords:
            self.translate_node_coords()

        for i in range(0, len(self.graph.nodes)):
            self.drawNode(self.graph.nodes[i])
        for i in range(0, len(self.graph.edges)):
            self.drawEdge(self.graph.edges[i])

        self.Redraw()
        #time.sleep(1)

    def stage2(self):
        #numfixed = self.remove_overlaps()
        
        numfixed = self.overlap_remover.remove_overlaps()
        if numfixed:
            self.stateofthenation()
        
    def stateofthenation(self):
        for node in self.graph.nodes:
            self.moveNode(node)
        self.Redraw()
        wx.SafeYield()
        #time.sleep(0.2)
        
        
    def draw(self, tranlatecoords=True):
        self.stage1(tranlatecoords=tranlatecoords)
        #thread.start_new_thread(self.DoSomeLongTask, ())


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
        
        
    def moveNode(self, node):
        assert node.shape
        
        # Don't need to use node.shape.Move(dc, x, y, False)
        setpos(node.shape, node.value.left, node.value.top)

        # But you DO need to use a dc to adjust the links
        dc = wx.ClientDC(self.oglcanvas)
        self.oglcanvas.PrepareDC(dc)
        node.shape.MoveLinks(dc)




        """
        fromShape = edge['source'].shape
        toShape = edge['target'].shape
        fromShape.AddLine(line, toShape)
        #line.SetEnds(source[0], source[1], target[0], target[1])
        
        self.oglcanvas.GetDiagram().AddShape(line)
        line.Show(True)
        """


        
        """
        - To add a line, use ogl.LineShape().  The exact sequence of calls is
        tricky, but this seems to work:
          line = ogl.LineShape()
          line.MakeControlPoints(2) # has to be at least 2
          line.SetEnds(x1, y1, x2, y2) # sets the first + last control points
          line.InsertControlPoint(x, y) # see below
          line.Initialise()
          line.SetSplit(True) # for a spline
          canvas.AddShape(line)
        The InsertControlPoint() adds an additional point in the list of control
        points; it is always inserted just before the end (ie (x2, y2) above), so
        repeatedly calling this "fills in" the line from start to end.
        """







        #dc = wx.ClientDC(self.oglcanvas)
        #self.oglcanvas.PrepareDC(dc)
        #
        #x, y = node.value.left, node.value.top
        #
        ## compensate for the fact that x, y for a ogl shape are the centre of the shape, not the top left
        #width, height = node.shape.GetBoundingBoxMax()
        #assert width == node.value.width
        #assert height == node.value.height
        #x += width/2
        #y += height/2
        #
        #node.shape.Move(dc, x, y, False)
        
    def Redraw(self):
        
        diagram = self.oglcanvas.GetDiagram()
        canvas = self.oglcanvas
        assert canvas == diagram.GetCanvas()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        
        #for node in self.graph.nodes:
        #    shape = node.shape
        #    shape.Move(dc, shape.GetX(), shape.GetY())
        diagram.Clear(dc)
        diagram.Redraw(dc)

     
    def drawNode(self, node):
        #point = self.translate([node.layoutPosX, node.layoutPosY])
        #node.value.top      = point[1]
        #node.value.left     = point[0]
               
        #print node
        shape = ogl.RectangleShape( node.value.width, node.value.height )
        shape.AddText(node.value.id)
        setpos(shape, node.value.left, node.value.top)
        #shape.SetDraggable(True, True)
        self.oglcanvas.AddShape( shape )
        node.shape = shape
        shape.node = node
        
        # wire in the event handler for the new shape
        evthandler = MyEvtHandler(None, self.oglcanvas)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        
        #self.ctx.strokeStyle = 'black'
        #self.ctx.beginPath()
        #self.ctx.arc(point[0], point[1], self.radius, 0, Math.PI*2, true)
        #self.ctx.closePath()
        #self.ctx.stroke()
       
    def drawEdge(self, edge):
        source = self.translate([edge['source'].layoutPosX, edge['source'].layoutPosY])
        target = self.translate([edge['target'].layoutPosX, edge['target'].layoutPosY])

        #tan = (target[1] - source[1]) / (target[0] - source[0])
        #theta = Math.atan(tan)
        #if(source[0] <= target[0]): theta = Math.PI()+theta
        #source = self.rotate(source, -self.radius, theta)
        #target = self.rotate(target, self.radius, theta)

        #print "Edge: from (%d, %d) to (%d, %d)" % (source[0], source[1], target[0], target[1])
         
        
        
        
        
          #line = ogl.LineShape()
          #line.MakeControlPoints(2) # has to be at least 2
          #line.SetEnds(x1, y1, x2, y2) # sets the first + last control points
          #line.InsertControlPoint(x, y) # see below
          #line.Initialise()
          #line.SetSplit(True) # for a spline
          #canvas.AddShape(line)        
        
        
        
        
        line = ogl.LineShape()
        line.SetCanvas(self.oglcanvas)
        line.SetPen(wx.BLACK_PEN)
        line.SetBrush(wx.BLACK_BRUSH)
        line.MakeLineControlPoints(2)
        
        
        fromShape = edge['source'].shape
        toShape = edge['target'].shape
        fromShape.AddLine(line, toShape)
        #line.SetEnds(fromShape.GetX(), fromShape.GetY(), toShape.GetX(), toShape.GetY())
        
        
        """
        Getting splines to work is a nightmare
        Seems to reply on there being shape._lineControlPoints which are sometimes zapped by ogl
        during recalculations etc. which means spline drawing can fail.
        """
        #print "GetLineControlPoints", line.GetLineControlPoints()
        #if line.GetLineControlPoints() >= 2:
        #    line.SetSpline(True)  # uses GetLineControlPoints - ensure there are at least 2 !
        
        
        self.oglcanvas.GetDiagram().AddShape(line)
        line.Show(True)        
        
        
        # draw the edge
        #self.ctx.strokeStyle = 'grey'
        #self.ctx.fillStyle = 'grey'
        #self.ctx.lineWidth = 1.0
        #self.ctx.beginPath()
        #self.ctx.moveTo(source[0], source[1])
        #self.ctx.lineTo(target[0], target[1])
        #self.ctx.stroke()
       
        #self.drawArrowHead(20, self.arrowAngle, theta, source[0], source[1], target[0], target[1])

    def drawArrowHead(self, length, alpha, theta, startx, starty, endx, endy):
        top = self.rotate([endx, endy], length, theta + alpha)
        bottom = self.rotate([endx, endy], length, theta - alpha)
        #self.ctx.beginPath()
        #self.ctx.moveTo(endx, endy)
        #self.ctx.lineTo(top[0], top[1])
        #self.ctx.lineTo(bottom[0], bottom[1])
        #self.ctx.fill()

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__( self,
                          None, -1, "Demo",
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
        
        a = Div('A', 0, 0, 250, 250)
        a1 = Div('A1', 0, 0)
        a2 = Div('A2', 0, 0)
        g.addEdge(a, a1)
        g.addEdge(a, a2)

        b = Div('B', 0, 0)
        b1 = Div('B1', 0, 0)
        b2 = Div('B2', 0, 0)
        g.addEdge(b, b1)
        g.addEdge(b, b2)

        b21 = Div('B21', 0, 0)
        b22 = Div('B22', 0, 0, 100, 200)
        g.addEdge(b2, b21)
        g.addEdge(b2, b22)

        c = Div('c', 0, 0)
        c1 = Div('c1', 0, 0)
        c2 = Div('c2', 0, 0)
        c3 = Div('c3', 0, 0)
        c4 = Div('c4', 0, 0)
        c5 = Div('c5', 0, 0, 60, 120)
        g.addEdge(c, c1)
        g.addEdge(c, c2)
        g.addEdge(c, c3)
        g.addEdge(c, c4)
        g.addEdge(c, c5)
        g.addEdge(a, c)
        
        g.addEdge(b2, c)
        g.addEdge(b2, c5)
        g.addEdge(a, c5)

        layouter = GraphLayoutSpring(g)
        layouter.layout()
        
        for node in g.nodes:
            print node.value.id, (node.layoutPosX, node.layoutPosY)
        
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
