# GraphRendererBasic

class CoordinateMapper:
    def __init__(self, graph, world_size):
        self.graph = graph
        self.world_size = world_size
        self.radius = 10
        self.Recalibrate()

    def Recalibrate(self, new_world_size=None):
        if new_world_size:
            self.world_size = new_world_size

        ww, wh = self.world_size                # world width, world height
        
        lw = self.graph.layoutMaxX - self.graph.layoutMinX  # layout width
        lh = self.graph.layoutMaxY - self.graph.layoutMinY  # layout height
        
        assert lw
        assert lh
        
        self.factorX = ww/2/lw
        self.factorY = wh/2/lh
            
    def LayoutToWorld(self, point):
        return [
          int((point[0] - self.graph.layoutMinX) * self.factorX + self.radius),
          int((point[1] - self.graph.layoutMinY) * self.factorY + self.radius)
        ]

    def WorldToLayout(self, point):
        return [
          (point[0] - self.radius) / self.factorX + self.graph.layoutMinX,
          (point[1] - self.radius) / self.factorY + self.graph.layoutMinY 
        ]
        

class GraphRendererBasic:
    def __init__(self, graph, worldcanvas):
        self.graph = graph
        self.worldcanvas = worldcanvas
        self.coordmapper = CoordinateMapper(self.graph, self.worldcanvas.GetSize())

    def translate(self, point):
        return LayoutToWorld(point)

    def CoordsAllWorldToLayout(self):
        for node in self.graph.nodes:
            node.layoutPosX, node.layoutPosY = self.coordmapper.WorldToLayout([node.left, node.top])
    
    def CoordsAllLayoutToWorld(self):
        for node in self.graph.nodes:
            node.left, node.top = self.coordmapper.LayoutToWorld([node.layoutPosX, node.layoutPosY])

    def draw(self):
        for node in self.graph.nodes:
            self.drawNode(node)
        for edge in self.graph.edges:
            self.drawEdge(edge)

    def drawNode(self, node):
        print node
       
    def drawEdge(self, edge):
        print "Edge: from (%d, %d) to (%d, %d)" % (edge['source'].left, edge['source'].top, edge['target'].left, edge['target'].top)


if __name__ == '__main__':

    from graph import *
    from layout_spring import GraphLayoutSpring
    #from overlap_removal import OverlapRemoval

    g = Graph()
    
    n1 = GraphNode('A', 0, 0, 200, 200)
    n2 = GraphNode('B', 0, 0, 200, 200)
    g.AddEdge(n1, n2)
    
    """
    Spring force layout
    """
    
    layouter = GraphLayoutSpring(g)

    def dump():
        for node in g.nodes:
            print node, "layout info:", (node.layoutPosX, node.layoutPosY)

    print "layout pass 1"
    layouter.layout()
    dump()

    print "layout pass 2"
    layouter.layout()
    dump()


    """
    Rendering
    
    Its only when you have a renderer that the idea of a world/screen
    coordinate system arises.
    """
    
    class WorldCanvas:
        def __init__(self, width, height):
            self.width = width
            self.height = height
        def GetSize(self):
            return (self.width, self.height)

    r = GraphRendererBasic(g, WorldCanvas(784, 739))

    r.CoordsAllLayoutToWorld()
    r.draw();

    # move some shapes in the real world
    a = g.FindNodeById('A')
    a.left += 100
    print "Moved", a
    
    # Gonna do another layout (after having just done a world draw) so need to update the layout positions
    r.CoordsAllWorldToLayout()
    
    print "layout pass 3"
    layouter.layout()
    dump()

    # gonna do another draw (after having just done a layout), so need to remap
    r.CoordsAllLayoutToWorld()
    r.draw();



    """
    coordinate mapper translation tests
    """

    # Force some values    
    g.layoutMaxX, g.layoutMinX, g.layoutMaxY, g.layoutMinY = 5.14284838307, -7.11251323652, 4.97268108065, -5.77186339003

    c = CoordinateMapper(g, (784, 739))

    # LayoutToWorld
    
    res = c.LayoutToWorld((-2.7556504645221258, 0.39995144721675263))
    print res
    assert res[0] == 149, res
    assert res[1] == 221, res

    res = c.LayoutToWorld((-5.4927475878590482, -1.7573960183470871))
    print res
    assert res[0] == 61, res
    assert res[1] == 147, res

    # WorldToLayout

    def trunc(f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''
        slen = len('%.*f' % (n, f))
        return str(f)[:slen]
    
    res = c.WorldToLayout((149, 221))
    print res
    print "results should approximate -2.7556504645221258, 0.39995144721675263"
    assert trunc(res[0], 1) == "-2.7", trunc(res[0], 1)
    assert trunc(res[1], 1) == "0.3", trunc(res[1], 1)
    
    res = c.WorldToLayout(( 61, 147))
    print res
    assert trunc(res[0], 0) == "-5", trunc(res[0], 0)
    assert trunc(res[1], 1) == "-1.7", trunc(res[1], 1)

    print 'Done'

