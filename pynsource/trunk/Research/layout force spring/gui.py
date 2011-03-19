import wx
import wx.lib.ogl as ogl

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

class GraphRendererOgl:
    def __init__(self, element, graph, oglcanvas):
        self.element = element
        self.graph = graph
        self.oglcanvas = oglcanvas

        self.ctx = element.getContext("2d")
        self.radius = 20
        self.arrowAngle = Math.PI()/10

        self.factorX = (element.width - 2 * self.radius) / (graph.layoutMaxX - graph.layoutMinX)
        self.factorY = (element.height - 2 * self.radius) / (graph.layoutMaxY - graph.layoutMinY)

    def translate(self, point):
        return [
          (point[0] - self.graph.layoutMinX) * self.factorX + self.radius,
          (point[1] - self.graph.layoutMinY) * self.factorY + self.radius
        ]

    def rotate(self, point, length, angle):
        dx = length * Math.cos(angle)
        dy = length * Math.sin(angle)
        return [point[0]+dx, point[1]+dy]





    def draw(self):
        self.translate_node_coords()
        self.remove_overlaps()
        for i in range(0, len(self.graph.nodes)):
            self.drawNode(self.graph.nodes[i])
        for i in range(0, len(self.graph.edges)):
            self.drawEdge(self.graph.edges[i])

    def translate_node_coords(self):
        for node in self.graph.nodes:
            point = self.translate([node.layoutPosX, node.layoutPosY])
            node.value.top      = point[1]
            node.value.left     = point[0]

    def remove_overlaps(self, fix=True):
        # Removing node overlap is actually no easy task. None of the layout
        # algorithms in JUNG, or few perhaps in the graphing world take vertex
        # size into account. As such, the technique is to usually run the layout
        # you desire and then run an overlap removal algorithm afterwards which
        # should slightly move the vertices around to remove overlap. I was able
        # to do such with the scaling and quadratic algorithms in the paper
        # above.
        # Forces on nodes due to node-node repulsions
        print "remove_overlaps"
        MARGIN = 10
        
        #for i in range(0, len(self.graph.nodes)):
        #    node1 = self.graph.nodes[i];
        #    for j in range(i + 1, len(self.graph.nodes)):
        #        node2 = self.graph.nodes[j]

        def wouldnotclashwithany_x(onleft, proposed_left):
            for node in self.graph.nodes:
                if node == onleft:
                    continue
                node_bigx = node.value.left + node.value.width + MARGIN
                if ((proposed_left < node_bigx) and (proposed_left > node.value.left)):
                    print "sorry, proposed_left %d clashes with %s's %d...%d" % (proposed_left, onleft.value.id, node.value.left, node_bigx)
                    return False
            return True

        def wouldnotclashwithany_y(ontop, proposed_top):
            for node in self.graph.nodes:
                if node == ontop:
                    continue
                node_bigy = node.value.top + node.value.height + MARGIN
                if ((proposed_top < node_bigy) and (proposed_top > node.value.top)):
                    print "sorry, proposed_top %d clashes with %s's %d...%d" % (proposed_top, ontop.value.id, node.value.top, node_bigy)
                    return False
            return True

        iterations = 0
        overlaps_found = 0
        fancy_negative_technique = 0
        for i in range(0,25):
            print i
            iterations += 1
            foundoverlaps = False
            for node1 in self.graph.nodes:
                for node2 in self.graph.nodes:
                    if node1 == node2:
                        continue
                    
                    if node1.value.left < node2.value.left:
                        onleft = node1
                        onright = node2
                    else:
                        onleft = node2
                        onright = node1
                    left_bigx = onleft.value.left + onleft.value.width + MARGIN
                    
                    if node1.value.top < node2.value.top:
                        ontop = node1
                        onbottom = node2
                    else:
                        ontop = node2
                        onbottom = node1
                    top_bigy = ontop.value.top + ontop.value.height + MARGIN
                    
                    #print "check: %s-%s %d > %d ?  %d > %d ?" % (onleft.value.id, onright.value.id, left_bigx, onright.value.left, top_bigy, onbottom.value.top)
                    if ((left_bigx > onright.value.left) and (top_bigy > onbottom.value.top)):
                        foundoverlaps = True
                        overlaps_found += 1
                        xoverlap_amount = left_bigx - onright.value.left
                        yoverlap_amount = top_bigy - onbottom.value.top
                        print "OVERLAP!!!! by %d/%d between %s and %s - %s %s" % (xoverlap_amount, yoverlap_amount, node1.value.id, node2.value.id, node1, node2)
                        if fix:
                            # only repair one dimension at a time
                            if xoverlap_amount < yoverlap_amount:
                                if ((onleft.value.left - xoverlap_amount > 0) and wouldnotclashwithany_x(onleft, proposed_left=onleft.value.left - xoverlap_amount)):
                                    onleft.value.left -= xoverlap_amount
                                    fancy_negative_technique += 1
                                else:
                                    onright.value.left += xoverlap_amount
                            else:
                                if ((ontop.value.top - yoverlap_amount > 0) and wouldnotclashwithany_y(ontop, proposed_top=ontop.value.top - yoverlap_amount)):
                                    ontop.value.top -= yoverlap_amount
                                    fancy_negative_technique += 1
                                else:
                                    onbottom.value.top += yoverlap_amount

                            print "  fixed %s %s" % (node1, node2)

            if not foundoverlaps:
                print "no overlaps anymore :-)"
                break
        if foundoverlaps:
            print "Exiting with overlaps remaining :-("
        print "Overlaps fixed: %d  Iterations made: %d  fancy_negative_techniques: %d  " % (overlaps_found, iterations, fancy_negative_technique)










    #def draw(self):
    #    for i in range(0, len(self.graph.nodes)):
    #        self.drawNode(self.graph.nodes[i])
    #    for i in range(0, len(self.graph.edges)):
    #        self.drawEdge(self.graph.edges[i])
       
    def drawNode(self, node):
        #point = self.translate([node.layoutPosX, node.layoutPosY])
        #
        #node.value.top      = point[1]
        #node.value.left     = point[0]
               
        #print node
        shape = ogl.RectangleShape( node.value.width, node.value.height )
        shape.AddText(node.value.id)
        setpos(shape, node.value.left, node.value.top)
        self.oglcanvas.AddShape( shape )
        node.shape = shape
        
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
        
        line = ogl.LineShape()
        line.SetCanvas(self.oglcanvas)
        line.SetPen(wx.BLACK_PEN)
        line.SetBrush(wx.BLACK_BRUSH)
        line.MakeLineControlPoints(2)
        
        
        fromShape = edge['source'].shape
        toShape = edge['target'].shape
        fromShape.AddLine(line, toShape)
        #line.SetEnds(source[0], source[1], target[0], target[1])
        
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
        
        class Canvas:
            def __init__(self, width, height):
                self.width = width
                self.height = height
            def getContext(self, whatever):
                return Context()
               
        ## ==========================================
        
        # apply sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Show(1)

        ## ==========================================

        people = Canvas(400, 400)        
        renderer = GraphRendererOgl(people, g, canvas);
        renderer.draw();
        
        diagram.ShowAll( 1 )
        

app = wx.PySimpleApp()
ogl.OGLInitialize()
frame = AppFrame()
app.MainLoop()
app.Destroy()
