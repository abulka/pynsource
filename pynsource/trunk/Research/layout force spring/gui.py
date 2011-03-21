import wx
import wx.lib.ogl as ogl
import time
import thread

from graph import *

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
        frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)" % (x, y, width, height))

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        #print "OnLeftClick"
        shape = self.GetShape()
        self.UpdateStatusBar(shape)

    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        #print "OnEndDragLeft"
        shape = self.GetShape()

        oldpos = getpos(shape) # (int(shape.GetX()), int(shape.GetY()))
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)  # super
        newpos = getpos(shape) # (int(shape.GetX()), int(shape.GetY()))

        print shape.node.value.id, shape.node.value.left, shape.node.value.top, "moved from", oldpos, newpos
        
        # Adjust the Div to match the shape x,y
        shape.node.value.left, shape.node.value.top = newpos

        wx.SafeYield()
        time.sleep(0.2)
        
        self.naughtyref_to_graphrenderer.stage2()


class GraphRendererOgl:
    def __init__(self, graph, oglcanvas):
        self.graph = graph
        self.oglcanvas = oglcanvas

        self.radius = 10
        self.arrowAngle = Math.PI()/10

        width, height = oglcanvas.GetSize()
        self.factorX = (width/2 ) / (graph.layoutMaxX - graph.layoutMinX)
        self.factorY = (height/2 ) / (graph.layoutMaxY - graph.layoutMinY)

        self.oglcanvas.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        self.need_abort = False

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

 
    def remove_overlaps(self, fix=True):
        # Removing node overlap is actually no easy task. None of the layout
        # algorithms, or few perhaps in the graphing world take vertex
        # size into account. As such, the technique is to usually run the layout
        # you desire and then run an overlap removal algorithm afterwards which
        # should slightly move the vertices around to remove overlap.
        
        MARGIN = 1

        def getpermutations(lzt):
            result = []
            for i in range(0, len(lzt)):
                for j in range(i+1, len(lzt)):
                    result.append((lzt[i], lzt[j]))
            return result

        def GetBounds(node):
            left = node.value.left
            right = node.value.left + node.value.width
            top = node.value.top
            bottom = node.value.top + node.value.height
            return left, right, top, bottom
        
        def stayinbounds(node, deltaX=0, deltaY=0):
            assert deltaX >0 or deltaY >0
            if deltaX:
                return node.value.left - deltaX > 0
            if deltaY:
                return node.value.top - deltaY > 0

        def arenodepointsin(node1, node2):
            l, r, t, b = GetBounds(node1)
            left, right, top, bottom = GetBounds(node2)
            for x,y in [(l,t), (r,t), (l,b), (r,b)]:
                if x >= left and x <= right and y >= top and y <= bottom:
                    return True
            return False

        def hit(node1, node2):
            return arenodepointsin(node1, node2) or arenodepointsin(node2, node1)
            
        def amhitting(currnode, ignorenode=None):
            for node in self.graph.nodes:
                if node == movingnode or node == ignorenode:
                    continue
                if hit(currnode, node):
                    print "  ! sitting here, %s is hitting %s." % (currnode.value.id, node.value.id)
                    return node
            print "  ! sitting here, %s is  n o t  h i t t i n g  anything." % (currnode.value.id)
            return None

        def wouldclash(movingnode, deltaY=0, deltaX=0, ignorenode=None):
            l, r, t, b = GetBounds(movingnode)  # proposed
            checkednodesmsg = "node %s we are proposing to move: points are %s/%s/%s/%s " % (movingnode.value.id,(l,t), (r,t), (l,b), (r,b))
            
            l -= deltaX
            r -= deltaX
            t -= deltaY
            b -= deltaY
            proposednode = GraphNode(Div('temp moving proposed', top=t, left=l, width=r-l+1, height=b-t+1))
            left, right, top, bottom = GetBounds(proposednode)
            checkednodesmsg += "adjusted to proposed points %s/%s/%s/%s tmpnode %d/%d/%d/%d" % ((l,t), (r,t), (l,b), (r,b), left, right, top, bottom)
            
            for node in self.graph.nodes:
                if node == movingnode or node == ignorenode:
                    continue
                if hit(proposednode, node):
                    print "  ! moving %s by -%d/-%d would hit %s." % (movingnode.value.id, deltaX, deltaY, node.value.id)
                    return node
            print "  ! moving %s by -%d/-%d would NOT HIT anything. %s" % (movingnode.value.id, deltaX, deltaY, checkednodesmsg)
            return None

        def ExpansiveMoveWouldClash(movingnode, deltaY=0, deltaX=0, ignorenode=None):
            assert deltaX >0 or deltaY >0
            l, r, t, b = GetBounds(movingnode)  # proposed
            proposednode = GraphNode(Div('temp', top=t+deltaY, left=l+deltaX, width=r-l+deltaX+1, height=b-t+deltaY+1))
            for node in self.graph.nodes:
                if node == movingnode or node == ignorenode:
                    continue
                if hit(proposednode, node):
                    print "  ! expansive moving %s by +%d/+%d would hit %s." % (movingnode.value.id, deltaX, deltaY, node.value.id)
                    return node
            print "  ! expansive moving %s by +%d/+%d would NOT HIT anything." % (movingnode.value.id, deltaX, deltaY)
            return None
        
        def whoisonleft(node1, node2):
            if node1.value.left < node2.value.left:
                return node1, node2
            else:
                return node2, node1

        def whoisontop(node1, node2):
            if node1.value.top < node2.value.top:
                return node1, node2
            else:
                return node2, node1
        

        iterations = 0
        total_overlaps_found = 0
        fancy_negative_technique = 0
        ignorenodes = []
        numfixedthisround = 0
        total_postmove_fixes = 0
        
        for i in range(0,10):
            
            print i
            iterations += 1
            
            if numfixedthisround == 0:
                print "No fixes made last round, clearing bans"
                ignorenodes = []
            numfixedthisround = 0

            foundoverlap = False
            
            self.stateofthenation()
                    
            for node1, node2 in getpermutations(self.graph.nodes):
                if hit(node1, node2):
                    # CALC AAA1
                    leftnode, rightnode = whoisonleft(node1, node2)
                    topnode, bottomnode = whoisontop(node1, node2)
                    xoverlap_amount = (leftnode.value.left + leftnode.value.width + MARGIN) - rightnode.value.left
                    yoverlap_amount = (topnode.value.top + topnode.value.height + MARGIN) - bottomnode.value.top
                    
                    foundoverlap = True
                    total_overlaps_found += 1
                    print "Overlap %s/%s by %d/%d  (leftnode is %s  topnode is %s)" % (node1.value.id, node2.value.id, xoverlap_amount, yoverlap_amount, leftnode.value.id, topnode.value.id)
                    
                    if fix:
                        proposals = []
                        
                        if (stayinbounds(leftnode, deltaX=xoverlap_amount) and not wouldclash(leftnode, deltaX=xoverlap_amount, ignorenode=rightnode)):
                            proposals.append({'node':leftnode, 'xory':'x', 'amount':-xoverlap_amount, 'clashnode':rightnode})
                        else:
                            proposals.append({'node':rightnode, 'xory':'x', 'amount':xoverlap_amount, 'clashnode':leftnode})
                            
                        if (stayinbounds(topnode, deltaY=yoverlap_amount) and not wouldclash(topnode, deltaY=yoverlap_amount, ignorenode=bottomnode)):
                            proposals.append({'node':topnode, 'xory':'y', 'amount':-yoverlap_amount, 'clashnode':bottomnode})
                        else:
                            proposals.append({'node':bottomnode, 'xory':'y', 'amount':yoverlap_amount, 'clashnode':topnode})

                        def dumpproposal(prop):
                            return "  moving %s.%s by %s" % (prop['node'].value.id, prop['xory'], prop['amount'])
                            
                        def dumpproposals(props):
                            msg = "  Proposals: "
                            for p in props:
                                msg += dumpproposal(p)
                            return msg
                            
                        def dumpignorelist():
                            msg = ""
                            for n in ignorenodes:
                                msg += " %s," % (n.value.id)
                            print "  ignore list now ", msg

                        print dumpproposals(proposals)
                        proposals2 = [p for p in proposals if not p['node'] in ignorenodes]
                        if not proposals2:
                            print "  All proposals eliminated - worry about this overlap later"
                            dumpignorelist()
                            continue
                        
                        amounts = [abs(p['amount']) for p in proposals2]
                        lowest_amount = min(amounts)
                        proposal = [p for p in proposals2 if abs(p['amount']) == lowest_amount][0]

                        def applytrans(prop):
                            print dumpproposal(prop)
                            if prop['xory'] == 'x':
                                prop['node'].value.left += prop['amount']
                            else:
                                prop['node'].value.top += prop['amount']
                            
                        applytrans(proposal)
                        numfixedthisround += 1
                        proposals2.remove(proposal)
                        ignorenodes.append(proposal['node'])
                        dumpignorelist()
                        if proposal['amount'] < 0:
                            fancy_negative_technique += 1
                        #self.stateofthenation()
                        
                        # Post Move Algorithm - move the same node again, under certain circumstances
                        if True:
                            movingnode = proposal['node']
                            # What am I clashing with now?
                            clashingnode = amhitting(movingnode)
                            if clashingnode:
                                # CALC AAA1
                                leftnode, rightnode = whoisonleft(clashingnode, movingnode)
                                topnode, bottomnode = whoisontop(clashingnode, movingnode)
                                xoverlap_amount = (leftnode.value.left + leftnode.value.width + MARGIN) - rightnode.value.left
                                yoverlap_amount = (topnode.value.top + topnode.value.height + MARGIN) - bottomnode.value.top
        
                                xoverlap_amount = abs(xoverlap_amount)
                                yoverlap_amount = abs(yoverlap_amount)
                                
                                # check the axis opposite to that I just moved
                                if proposal['xory'] == 'x':
                                    # check y movement possibilities
                                    if ((movingnode == topnode) and stayinbounds(movingnode, deltaY=yoverlap_amount) and not wouldclash(movingnode, deltaY=yoverlap_amount)):
                                        movingnode.value.top -= yoverlap_amount
                                        total_postmove_fixes += 1
                                        print "  * extra correction to %s" % (movingnode.value.id)
                                    if ((movingnode == bottomnode) and not ExpansiveMoveWouldClash(movingnode, deltaY=yoverlap_amount)):
                                        movingnode.value.top += yoverlap_amount
                                        total_postmove_fixes += 1
                                        print "  * extra correction to %s" % (movingnode.value.id)
                                else:
                                    print "  ************** no logic in place so couldn't do any possible extra correction to %s" % (movingnode.value.id)
                                    pass
                        
                        
            if not foundoverlap:
                break  # the failsafe for loop

        if total_overlaps_found:
            print "Overlaps fixed: %d  Iterations made: %d  total_postmove_fixes: %d  fancy_negative_techniques: %d  " % (total_overlaps_found, iterations, total_postmove_fixes, fancy_negative_technique)
            if foundoverlap:
                print "Exiting with overlaps remaining :-("
        return total_overlaps_found






    def OnWheelZoom(self, event):
        self.stage2()

    def stage1(self):
        import time
        
        self.translate_node_coords()

        for i in range(0, len(self.graph.nodes)):
            self.drawNode(self.graph.nodes[i])
        for i in range(0, len(self.graph.edges)):
            self.drawEdge(self.graph.edges[i])

        self.Redraw()
        #time.sleep(1)

    def stage2(self):
        numfixed = self.remove_overlaps()
        if numfixed:
            self.stateofthenation()
        
    def stateofthenation(self):
        for node in self.graph.nodes:
            self.moveNode(node)
        self.Redraw()
        wx.SafeYield()
        time.sleep(0.2)
        
        
    def draw(self):
        self.stage1()
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
        self.oglcanvas.AddShape( shape )
        node.shape = shape
        shape.node = node
        
        # wire in the event handler for the new shape
        evthandler = MyEvtHandler(None, self.oglcanvas)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        evthandler.naughtyref_to_graphrenderer = self
        
        #self.ctx.strokeStyle = 'black'
        #self.ctx.beginPath()
        #self.ctx.arc(point[0], point[1], self.radius, 0, Math.PI*2, true)
        #self.ctx.closePath()
        #self.ctx.stroke()
       
    def drawEdge(self, edge):
        source = self.translate([edge['source'].layoutPosX, edge['source'].layoutPosY])
        target = self.translate([edge['target'].layoutPosX, edge['target'].layoutPosY])

        tan = (target[1] - source[1]) / (target[0] - source[0])
        theta = Math.atan(tan)
        if(source[0] <= target[0]): theta = Math.PI()+theta
        source = self.rotate(source, -self.radius, theta)
        target = self.rotate(target, self.radius, theta)

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
       
        self.drawArrowHead(20, self.arrowAngle, theta, source[0], source[1], target[0], target[1])

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

        canvas = ogl.ShapeCanvas( self )
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
