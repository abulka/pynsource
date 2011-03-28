# CoordinateMapper

class CoordinateMapper:
    def __init__(self, graph, world_size, scale=2):
        self.graph = graph
        self.world_size = world_size
        self.radius = 10
        self.scale = scale
        self.Recalibrate()

    def Recalibrate(self, new_world_size=None, scale=None):
        if new_world_size:
            self.world_size = new_world_size
        if scale:
            self.scale = scale

        ww, wh = self.world_size                # world width, world height
        
        lw = self.graph.layoutMaxX - self.graph.layoutMinX  # layout width
        lh = self.graph.layoutMaxY - self.graph.layoutMinY  # layout height
        
        #assert lw
        #assert lh
        if lw == 0:
            lw = 0.0001
        if lh == 0:
            lh = 0.0001
        
        self.factorX = ww/self.scale/lw
        self.factorY = wh/self.scale/lh
            
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

    def AllToLayoutCoords(self):
        for node in self.graph.nodes:
            node.layoutPosX, node.layoutPosY = self.WorldToLayout([node.left, node.top])
    
    def AllToWorldCoords(self):
        for node in self.graph.nodes:
            node.left, node.top = self.LayoutToWorld([node.layoutPosX, node.layoutPosY])


if __name__ == '__main__':

    from graph import Graph, GraphNode

    g = Graph()
    
    n1 = GraphNode('A', 0, 0, 200, 200)
    n2 = GraphNode('B', 0, 0, 200, 200)
    g.AddEdge(n1, n2)


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

