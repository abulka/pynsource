"""
/*  Graph JavaScript framework, version 0.0.1
 *  (c) 2006 Aslak Hellesoy <aslak.hellesoy@gmail.com>
 *  (c) 2006 Dave Hoover <dave.hoover@gmail.com>
 *
 *  Ported from Graph::Layouter::Spring in
 *    http://search.cpan.org/~pasky/Graph-Layderer-0.02/
 *  The algorithm is based on a spring-style layouter of a Java-based social
 *  network tracker PieSpy written by Paul Mutton E<lt>paul@jibble.orgE<gt>.
 *
 *  Graph is freely distributable under the terms of an MIT-style license.
 *  For details, see the Graph web site: http://dev.buildpatternd.com/trac
 *
/*--------------------------------------------------------------------------*/
"""

import random
from math import sqrt, log, pi, cos, sin, atan

class Math:
    @classmethod
    def random(cls):
        return random.randint(0,1000)/1000.0
    @classmethod
    def sqrt(cls, n):
        return sqrt(n)
    @classmethod
    def log(cls, n):
        return log(n)
    @classmethod
    def PI(cls):
        return pi
    @classmethod
    def cos(cls, n):
        return cos(n)
    @classmethod
    def sin(cls, n):
        return sin(n)
    @classmethod
    def atan(cls, n):
        return atan(n)
    
class Graph:
    def __init__(self):
        self.clear()
        
    def clear(self):
        self.nodeSet = {}
        self.nodes = []
        self.edges = []

        self.layoutMinX = 0
        self.layoutMaxX = 0
        self.layoutMinY = 0
        self.layoutMaxY = 0
        
    def addNode(self, div):
        key = div.id
        element = div

        node = self.nodeSet.get(key, None)
        if not node:
            node = GraphNode(element)
            self.nodeSet[key] = node
            self.nodes.append(node)
        return node

    def findNode(self, id):
        node = self.nodeSet.get(id, None)
        return node

    def deleteNode(self, id):
        node = self.findNode(id)
        if node:
            self.nodes.remove(node)
            if id in self.nodeSet.keys():
                del self.nodeSet[id]
        for edge in self.edges[:]:
            if edge['source'] == id or edge['target'] == id:
                self.edges.remove(edge)
            
    def addEdge(self, source, target):
        # Uniqueness must be ensured by caller
        s = self.addNode(source)
        t = self.addNode(target)
        edge = {'source': s, 'target': t}
        self.edges.append(edge)

    def LoadGraphFromStrings(self, filedata):
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
                div = Div(data['id'], data['y'], data['x'], data['width'], data['height'])
                self.addNode(div)
            elif data['type'] == 'edge':
                source_id = data['source']
                target_id = data['target']
                # need to find the node corresponding to a div of id whatever
                # wire together the two divs
                sourcenode = self.findNode(source_id)
                targetnode = self.findNode(target_id)
                if not sourcenode:
                    print "Couldn't load source from persistence", source_id
                    continue
                if not targetnode:
                    print "Couldn't load target from persistence", target_id
                    continue
                self.addEdge(sourcenode.value, targetnode.value)  # addEdge takes div objects as parameters

    def GraphToString(self):
        nodes = ""
        edges = ""
        for node in self.nodes:
            v = node.value
            nodes += "{'type':'node', 'id':'%s', 'x':%d, 'y':%d, 'width':%d, 'height':%d}\n" % (v.id, v.left, v.top, v.width, v.height)
        for edge in self.edges:
            source = edge['source'].value.id
            target = edge['target'].value.id
            edges += "{'type':'edge', 'id':'%s_to_%s', 'source':'%s', 'target':'%s'}\n" % (source, target, source, target)
        return nodes + edges

class GraphNode:
    def __init__(self, value):
        self.value = value
        
        self.layoutPosX = 0
        self.layoutPosY = 0
        self.layoutForceX = 0
        self.layoutForceY = 0
        
    def __str__(self):
        return "NodeDiv %s: x,y (%d, %d) w,h (%d, %d)" % (self.value.id, self.value.left, self.value.top, self.value.width, self.value.height)
        
class Context:
    pass

class Div:
    def __init__(self, id, top, left, width=60, height=60):  # TODO: top, left should be left, top
        self.id = id
        self.top = top
        self.left = left
        self.width=width
        self.height=height
    
class GraphRendererBasic:
    def __init__(self, element, graph):
        self.element = element
        self.graph = graph

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
        
        for i in range(0, len(self.graph.nodes)):
            node1 = self.graph.nodes[i];
            for j in range(i + 1, len(self.graph.nodes)):
                node2 = self.graph.nodes[j]
                
                if node1.value.left < node2.value.left:
                    onleft = node1
                    onright = node2
                else:
                    onleft = node2
                    onright = node1
                left_bigx = onleft.value.left + onleft.value.width
                if left_bigx > onright.value.left:
                    overlap_amount = left_bigx - onright.value.left
                    print "OVERLAP!!!! by %d between %s and %s - %s %s" % (overlap_amount, onleft.value.id, onright.value.id, onleft, onright)
                    if fix:
                        onright.value.left += overlap_amount

    def drawNode(self, node):
        #point = self.translate([node.layoutPosX, node.layoutPosY])
        #node.value.top      = point[1]
        #node.value.left     = point[0]
               
        print node
        
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

        print "Edge: from (%d, %d) to (%d, %d)" % (source[0], source[1], target[0], target[1])
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

class GraphLayoutSpring:
    def __init__(self, graph):
        self.graph = graph
        self.iterations = 500
        self.maxRepulsiveForceDistance = 6
        self.k = 2
        self.c = 0.01
        self.maxVertexMovement = 0.5
       
    def layout(self):
        self.layoutPrepare()
        for i in range(0, self.iterations):
            self.layoutIteration()
        self.layoutCalcBounds()
       
    def layoutPrepare(self):
        for i in range(0, len(self.graph.nodes)):
            node = self.graph.nodes[i]
            node.layoutPosX = 0
            node.layoutPosY = 0
            node.layoutForceX = 0
            node.layoutForceY = 0
       
    def layoutCalcBounds(self):
        minx = float("inf")
        maxx = float("-inf")
        miny = float("inf")
        maxy = float("-inf")

        for i in range(0, len(self.graph.nodes)):
            x = self.graph.nodes[i].layoutPosX
            y = self.graph.nodes[i].layoutPosY
                                   
            if(x > maxx): maxx = x
            if(x < minx): minx = x
            if(y > maxy): maxy = y
            if(y < miny): miny = y

        self.graph.layoutMinX = minx
        self.graph.layoutMaxX = maxx
        self.graph.layoutMinY = miny
        self.graph.layoutMaxY = maxy
       
    def layoutIteration(self):
        # Forces on nodes due to node-node repulsions
        for i in range(0, len(self.graph.nodes)):
            node1 = self.graph.nodes[i];
            for j in range(i + 1, len(self.graph.nodes)):
                node2 = self.graph.nodes[j]
                self.layoutRepulsive(node1, node2)
        # Forces on nodes due to edge attractions
        for i in range(0, len(self.graph.edges)):
            edge = self.graph.edges[i]
            self.layoutAttractive(edge)
               
        # Move by the given force
        for i in range(0, len(self.graph.nodes)):
            node = self.graph.nodes[i];
            xmove = self.c * node.layoutForceX
            ymove = self.c * node.layoutForceY

            max = self.maxVertexMovement
            if(xmove > max): xmove = max
            if(xmove < -max): xmove = -max
            if(ymove > max): ymove = max
            if(ymove < -max): ymove = -max
           
            node.layoutPosX += xmove
            node.layoutPosY += ymove
            node.layoutForceX = 0
            node.layoutForceY = 0

    def layoutRepulsive(self, node1, node2):
        dx = node2.layoutPosX - node1.layoutPosX
        dy = node2.layoutPosY - node1.layoutPosY
        d2 = dx * dx + dy * dy
        if(d2 < 0.01):
            dx = 0.1 * Math.random() + 0.1
            dy = 0.1 * Math.random() + 0.1
            d2 = dx * dx + dy * dy
        d = Math.sqrt(d2);
        if(d < self.maxRepulsiveForceDistance):
            repulsiveForce = self.k * self.k / d
            node2.layoutForceX += repulsiveForce * dx / d
            node2.layoutForceY += repulsiveForce * dy / d
            node1.layoutForceX -= repulsiveForce * dx / d
            node1.layoutForceY -= repulsiveForce * dy / d

    def layoutAttractive(self, edge):
        node1 = edge['source']
        node2 = edge['target']
       
        dx = node2.layoutPosX - node1.layoutPosX
        dy = node2.layoutPosY - node1.layoutPosY
        d2 = dx * dx + dy * dy
        if(d2 < 0.01):
            dx = 0.1 * Math.random() + 0.1
            dy = 0.1 * Math.random() + 0.1
            d2 = dx * dx + dy * dy
        d = Math.sqrt(d2);
        if(d > self.maxRepulsiveForceDistance):
            d = self.maxRepulsiveForceDistance
            d2 = d * d
        attractiveForce = (d2 - self.k * self.k) / self.k
        nodeweight = edge.get('weight', None)   # ANDY      
        if ((not nodeweight) or (edge['weight'] < 1)):
            edge['weight'] = 1
        attractiveForce *= Math.log(edge['weight']) * 0.5 + 1
       
        node2.layoutForceX -= attractiveForce * dx / d
        node2.layoutForceY -= attractiveForce * dy / d
        node1.layoutForceX += attractiveForce * dx / d
        node1.layoutForceY += attractiveForce * dy / d


if __name__ == '__main__':

    g = Graph()
    
    #n1 = Div('wilma', 10, 10)
    #n2 = Div('fred', 50, 50)
    #g.addEdge(n1, n2)
    #n3 = Div('andy', 500, 500)
    #g.addEdge(n1, n3)

    n1 = Div('A', 0, 0, 200, 200)
    n2 = Div('B', 0, 0, 200, 200)
    g.addEdge(n1, n2)
    
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
           
    people = Canvas(200, 200)
    renderer = GraphRendererBasic(people, g);
    renderer.draw();
    
    print 'Done'
