# spring force layout
#
# Ported and Adapted from Graph::Layouter::Spring in
#    http://search.cpan.org/~pasky/Graph-Layderer-0.02/
#    https://gist.github.com/heckj/324039 - javascript version

from view.graph import Graph, GraphNode
import random
import math


class GraphLayoutSpring:
    def __init__(self, graph, gui=None):
        self.graph = graph
        self.iterations = 1500  # 3000
        self.maxRepulsiveForceDistance = 6
        self.k = 2
        self.c = 0.01
        self.maxVertexMovement = 0.5
        self.gui = gui

    def layout(self, keep_current_positions=False, optimise=True):
        if len(self.graph.nodes) == 0:
            print("Layout aborted - nothing to lay out.")
            return

        if not keep_current_positions:
            self.layoutPrepare()

        if self.gui:
            self.gui.kill_layout = False  # initialise

        memento1 = self.graph.GetMementoOfLayoutPoints()
        break_pending = 0

        for i in range(0, self.iterations):
            self.layoutIteration()

            if i % 100 == 0:  # i%50==0:
                if self.gui:
                    self.layoutCalcBounds()  # this is the only time you need to call this explicitly since are in the MIDDLE of a layout and about to visualise
                    self.gui.mega_refresh(recalibrate=True, auto_resize_canvas=False)  # refresh gui

                    if self.gui.kill_layout:
                        print("Layout aborted early, due to user interrupt")
                        break

            if i % 20 == 0:
                if optimise:
                    memento2 = self.graph.GetMementoOfLayoutPoints()
                    if Graph.MementosEqual(memento1, memento2, 0.01):
                        break_pending += 1
                        # print "!",
                        if break_pending > 5:
                            # print "break"
                            break
                    else:
                        break_pending = 0
                        # print ".",
                    memento1 = memento2

        # print
        self.layoutCalcBounds()

    def layoutPrepare(self):
        for node in self.graph.nodes:
            node.layoutPosX = 0  # zero is better than random
            node.layoutPosY = 0  # zero is better than random
            node.layoutForceX = 0
            node.layoutForceY = 0

    def layoutCalcBounds(self):
        minx = float("inf")
        maxx = float("-inf")
        miny = float("inf")
        maxy = float("-inf")

        for node in self.graph.nodes:
            x = node.layoutPosX
            y = node.layoutPosY

            if x > maxx:
                maxx = x
            if x < minx:
                minx = x
            if y > maxy:
                maxy = y
            if y < miny:
                miny = y

        self.graph.layoutMinX = minx
        self.graph.layoutMaxX = maxx
        self.graph.layoutMinY = miny
        self.graph.layoutMaxY = maxy

    def layoutIteration(self):
        # Forces on nodes due to node-node repulsions
        for i in range(0, len(self.graph.nodes)):
            node1 = self.graph.nodes[i]
            for j in range(i + 1, len(self.graph.nodes)):
                node2 = self.graph.nodes[j]
                self.layoutRepulsive(node1, node2)
        # Forces on nodes due to edge attractions
        for edge in self.graph.edges:
            self.layoutAttractive(edge)

        # Move by the given force
        for node in self.graph.nodes:
            xmove = self.c * node.layoutForceX
            ymove = self.c * node.layoutForceY

            max = self.maxVertexMovement
            if xmove > max:
                xmove = max
            if xmove < -max:
                xmove = -max
            if ymove > max:
                ymove = max
            if ymove < -max:
                ymove = -max

            node.layoutPosX += xmove
            node.layoutPosY += ymove
            node.layoutForceX = 0
            node.layoutForceY = 0

    def layoutRepulsive(self, node1, node2):
        dx = node2.layoutPosX - node1.layoutPosX
        dy = node2.layoutPosY - node1.layoutPosY
        d2 = dx * dx + dy * dy
        if d2 < 0.01:
            dx = 0.1 * random.randint(0, 1000) / 1000.0 + 0.1
            dy = 0.1 * random.randint(0, 1000) / 1000.0 + 0.1
            d2 = dx * dx + dy * dy
        d = math.sqrt(d2)
        if d < self.maxRepulsiveForceDistance:
            repulsiveForce = self.k * self.k / d
            node2.layoutForceX += repulsiveForce * dx / d
            node2.layoutForceY += repulsiveForce * dy / d
            node1.layoutForceX -= repulsiveForce * dx / d
            node1.layoutForceY -= repulsiveForce * dy / d

    def layoutAttractive(self, edge):
        node1 = edge["source"]
        node2 = edge["target"]

        dx = node2.layoutPosX - node1.layoutPosX
        dy = node2.layoutPosY - node1.layoutPosY
        d2 = dx * dx + dy * dy
        if d2 < 0.01:
            dx = 0.1 * random.randint(0, 1000) / 1000.0 + 0.1
            dy = 0.1 * random.randint(0, 1000) / 1000.0 + 0.1
            d2 = dx * dx + dy * dy
        d = math.sqrt(d2)
        if d > self.maxRepulsiveForceDistance:
            d = self.maxRepulsiveForceDistance
            d2 = d * d
        attractiveForce = (d2 - self.k * self.k) / self.k
        nodeweight = edge.get("weight", None)  # ANDY
        if (not nodeweight) or (edge["weight"] < 1):
            edge["weight"] = 1
        attractiveForce *= math.log(edge["weight"]) * 0.5 + 1

        node2.layoutForceX -= attractiveForce * dx / d
        node2.layoutForceY -= attractiveForce * dy / d
        node1.layoutForceX += attractiveForce * dx / d
        node1.layoutForceY += attractiveForce * dy / d


if __name__ == "__main__":

    from graph import Graph

    g = Graph()

    n1 = GraphNode("A", 0, 0, 200, 200)
    n2 = GraphNode("B", 0, 0, 200, 200)
    g.AddEdge(n1, n2)

    layouter = GraphLayoutSpring(g)
    layouter.layout()

    for node in g.nodes:
        print(node, "layout info:", (node.layoutPosX, node.layoutPosY))

    print("Done")
