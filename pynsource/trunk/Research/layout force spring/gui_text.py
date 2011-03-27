# GraphRendererBasic

class GraphRendererBasic:
    def __init__(self, element, graph):
        self.element = element
        self.graph = graph

        self.radius = 20

        self.factorX = (element.width - 2 * self.radius) / (graph.layoutMaxX - graph.layoutMinX)
        self.factorY = (element.height - 2 * self.radius) / (graph.layoutMaxY - graph.layoutMinY)

    def translate(self, point):
        return [
          (point[0] - self.graph.layoutMinX) * self.factorX + self.radius,
          (point[1] - self.graph.layoutMinY) * self.factorY + self.radius
        ]

    def translate_all_node_coords(self):
        for node in self.graph.nodes:
            point = self.translate([node.layoutPosX, node.layoutPosY])
            node.value.top      = point[1]
            node.value.left     = point[0]

    def draw(self):
        self.translate_all_node_coords()
        #self.remove_overlaps()
        for i in range(0, len(self.graph.nodes)):
            self.drawNode(self.graph.nodes[i])
        for i in range(0, len(self.graph.edges)):
            self.drawEdge(self.graph.edges[i])

    def drawNode(self, node):
        #point = self.translate([node.layoutPosX, node.layoutPosY])
        #node.value.top      = point[1]
        #node.value.left     = point[0]
              
        print node
       
    def drawEdge(self, edge):
        source = self.translate([edge['source'].layoutPosX, edge['source'].layoutPosY])
        target = self.translate([edge['target'].layoutPosX, edge['target'].layoutPosY])

        print "Edge: from (%d, %d) to (%d, %d)" % (source[0], source[1], target[0], target[1])



if __name__ == '__main__':

    from graph import *
    from layout_spring import GraphLayoutSpring
    from overlap_removal import OverlapRemoval

    g = Graph()
    
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

