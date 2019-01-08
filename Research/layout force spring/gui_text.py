# GraphRendererBasic

from coordinate_mapper import CoordinateMapper


class GraphRendererBasic:
    def __init__(self, graph, worldcanvas):
        self.graph = graph
        self.worldcanvas = worldcanvas
        self.coordmapper = CoordinateMapper(self.graph, self.worldcanvas.GetSize())

    def AllToLayoutCoords(self):
        self.coordmapper.AllToLayoutCoords()

    def AllToWorldCoords(self):
        self.coordmapper.AllToWorldCoords()

    def draw(self):
        for node in self.graph.nodes:
            self.drawNode(node)
        for edge in self.graph.edges:
            self.drawEdge(edge)

    def drawNode(self, node):
        print(node)

    def drawEdge(self, edge):
        print(
            "Edge: from (%d, %d) to (%d, %d)"
            % (edge["source"].left, edge["source"].top, edge["target"].left, edge["target"].top)
        )


if __name__ == "__main__":

    from graph import *
    from layout_spring import GraphLayoutSpring

    # from overlap_removal import OverlapRemoval

    g = Graph()

    n1 = GraphNode("A", 0, 0, 200, 200)
    n2 = GraphNode("B", 0, 0, 200, 200)
    g.AddEdge(n1, n2)

    """
    Spring force layout
    """

    layouter = GraphLayoutSpring(g)

    def dump():
        for node in g.nodes:
            print(node, "layout info:", (node.layoutPosX, node.layoutPosY))

    print("layout pass 1")
    layouter.layout()
    dump()

    print("layout pass 2")
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

    r.AllToWorldCoords()
    r.draw()

    # move some shapes in the real world
    a = g.FindNodeById("A")
    a.left += 100
    print("Moved", a)

    # Gonna do another layout (after having just done a world draw) so need to update the layout positions
    r.AllToLayoutCoords()
    print("layout pass 3")
    layouter.layout()
    dump()

    # gonna do another draw (after having just done a layout), so need to remap
    r.AllToWorldCoords()
    r.draw()

    print("Done")
