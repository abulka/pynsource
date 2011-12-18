# CoordinateMapper

import locale
locale.setlocale(locale.LC_ALL, '')  # http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x

class CustomException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
           
class CoordinateMapper:
    def __init__(self, graph, world_size, scale=2):
        self.graph = graph
        self.world_size = world_size
        self.radius = 10
        self.scale = scale
        self.factorX = -99
        self.factorY = -99
        self.Recalibrate()

    def Recalibrate(self, new_world_size=None, scale=None):
        self.DumpCalibrationInfo(True, new_world_size, scale)
        
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
            lw = 1.0 #0.0001
        if lh == 0:
            lh = 1.0 # 0.0001
        
        self.factorX = ww/self.scale/lw
        self.factorY = wh/self.scale/lh

        self.DumpCalibrationInfo(False, new_world_size, scale)

    def DumpCalibrationInfo(self, is_function_start, new_world_size=None, scale=None):
        if is_function_start:
            indent = ""
            print
            print indent+"CoordinateMapper.Recalibrate START, calling with new_world_size=%s, scale=%s" %(new_world_size, scale)
        else:
            indent = "\t"
            print indent+"CoordinateMapper.Recalibrate END"
        print indent+"scale world_size\t\t", self.scale, " ", self.world_size
        print indent+"layout (MinX/MinY)(MaxX/Maxy)\t(%2.2f,%2.2f) (%2.2f,%2.2f)" % (self.graph.layoutMinX, self.graph.layoutMinY, self.graph.layoutMaxX, self.graph.layoutMaxY)
        print indent+"layout width height\t\t%2.2f %2.2f" % (self.graph.layoutMaxX - self.graph.layoutMinX, self.graph.layoutMaxY - self.graph.layoutMinY)
        print indent+"factorX factorY\t\t\t", locale.format("%d", self.factorX, grouping=True), locale.format("%d", self.factorY, grouping=True)


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
            if node.left > 20000:
                print '-'*40, "Something's gone wrong!"
                print "node.layoutPosX, node.layoutPosY", node.layoutPosX, node.layoutPosY
                for node in self.graph.nodes:
                    print node, "node.layoutPosX, node.layoutPosY", node.layoutPosX, node.layoutPosY
                self.DumpCalibrationInfo(False)
                raise CustomException("Insane x values being generated")


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

